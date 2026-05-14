import logging
from typing import List, Dict

import yaml

from src.constants import ACTIVITY_CLIENT
from src.env import RELTIO_TENANT, RDM_TENANT_ID
from src.util.api import (
    get_reltio_url,
    get_rdm_url,
    get_rdm_config_url,
    http_request,
    create_error_response,
    validate_connection_security
)
from src.util.auth import get_reltio_headers
from src.util.models import LookupListRequest, RdmLookupAddRequest
from src.util.activity_log import ActivityLog
from src.tools.util import ActivityLogLabel

# Configure logging
logger = logging.getLogger("mcp.server.reltio")

"""Lists all lookups in the Reltio instance
  
  Args:
      tenant_id (str): Tenant ID for the Reltio environment. Defaults to RELTIO_TENANT env value.
  
  Returns:
      A dictionary containing the lookups list
  
  Raises:
      Exception: If there's an error getting the lookups
  """

async def get_all_lookups(tenant_id : str = RELTIO_TENANT) -> dict:
    # Construct URL with validated entity ID
    url = get_reltio_url("lookups", "api", tenant_id)
    #print(url)
    try:
        headers = get_reltio_headers()

        # Validate connection security
        validate_connection_security(url, headers)
    except Exception as e:
        logger.error(f"Authentication or security error: {str(e)}")
        return create_error_response(
            "AUTHENTICATION_ERROR",
            "Failed to authenticate with Reltio API"
        )
    # Make the request with timeout
    try:
        #print("trying to get lookup values ")
        lookup_vals = http_request(url=url, headers=headers)
        #print(lookup_vals)
    except Exception as e:
        logger.error(f"API request error: {str(e)}")

        # Check if it's a 404 error (entity not found)
        if "404" in str(e):
            return create_error_response(
                "RESOURCE_NOT_FOUND",
                f"Cannot retrieve the lookup types"
            )

        return create_error_response(
            "SERVER_ERROR",
            "Failed to retrieve lookup details from Reltio API"
        )

    # # Try to log activity for success
    # try:
    #     await ActivityLog.execute_and_log_activity(
    #         tenant_id=tenant_id,
    #         label=ActivityLogLabel.USER_PROFILE_VIEW.value,
    #         client_type=ACTIVITY_CLIENT,
    #         description=json.dumps({"uri":f"entities/{entity_id.split('/')[-1]}","label":entity.get("label","")}),
    #         items=[{"objectUri":f"entities/{entity_id.split('/')[-1]}"}]
    #     )
    # except Exception as log_error:
    #     logger.error(f"Activity logging failed for get_entity_details: {str(log_error)}")


    return yaml.dump(lookup_vals, sort_keys=False)


async def rdm_lookups_list(lookup_type: str, tenant_id: str = RELTIO_TENANT, max_results: int = 10,
                           display_name_prefix: str = "") -> dict:
    """List lookups by RDM lookup type
    
    Args:
        lookup_type (str): RDM lookup type (e.g., 'rdm/lookupTypes/VistaVegetarianOrVegan')
        tenant_id (str): Tenant ID for the Reltio environment. Defaults to RELTIO_TENANT env value.
        max_results (int): Maximum number of results to return. Defaults to 10.
        display_name_prefix (str): Display name prefix to filter by. Defaults to "".
    
    Returns:
        A dictionary containing the lookups list
    
    Raises:
        Exception: If there's an error getting the lookups
    """
    try:
        # Validate and sanitize inputs using Pydantic model
        try:
            lookup_request = LookupListRequest(
                lookup_type=lookup_type,
                tenant_id=tenant_id,
                max_results=max_results,
                display_name_prefix=display_name_prefix
            )
        except ValueError as e:
            logger.warning(f"Validation error in rdm_lookups_list: {str(e)}")
            return create_error_response(
                "VALIDATION_ERROR",
                f"Invalid input parameters: {str(e)}"
            )
        
        # Construct URL for lookups list endpoint
        url = get_reltio_url("lookups/list", "api", lookup_request.tenant_id)
        
        try:
            headers = get_reltio_headers()
            
            # Validate connection security
            validate_connection_security(url, headers)
        except Exception as e:
            logger.error(f"Authentication or security error: {str(e)}")
            return create_error_response(
                "AUTHENTICATION_ERROR",
                "Failed to authenticate with Reltio API"
            )
        
        # Build the payload
        payload = {
            "type": lookup_request.lookup_type if lookup_request.lookup_type != "all" else "",
            "max": lookup_request.max_results,
            "displayNamePrefix": lookup_request.display_name_prefix
        }
        
        # Make the request with timeout
        try:
            result = http_request(url, method='POST', headers=headers, data=payload)
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return create_error_response(
                "SERVER_ERROR",
                "Failed to retrieve lookups from Reltio API"
            )
        
        try:
            # Count the number of lookups returned
            lookup_count = len(result) if isinstance(result, list) else 0
            lookup_summary = f"{lookup_count} lookups found" if lookup_count > 0 else "no lookups found"
            
            await ActivityLog.execute_and_log_activity(
                tenant_id=tenant_id,
                label=ActivityLogLabel.LOOKUP_LIST.value,
                client_type=ACTIVITY_CLIENT,
                description=f"rdm_lookups_list_tool : Successfully retrieved lookups: {lookup_summary} for lookup_type {lookup_type}"
            )
        except Exception as log_error:
            logger.error(f"Activity logging failed for rdm_lookups_list: {str(log_error)}")
        
        # Return the lookups in YAML format for better readability
        return yaml.dump(result, sort_keys=False)
        
    except Exception as e:
        # Log the error
        logger.error(f"Unexpected error in rdm_lookups_list: {str(e)}")
        
        # Return a sanitized error response
        return create_error_response(
            "SERVER_ERROR",
            "An unexpected error occurred while processing your request"
        )


async def rdm_lookups_add(
    entries: List[Dict],
    tenant_id: str = RDM_TENANT_ID
) -> dict:
    """Add one or more lookup values to an RDM lookup type in a single API call.

    IMPORTANT: The RDM API natively supports bulk insertion. You MUST batch all lookup
    entries for the same lookup type into a single call rather than making multiple
    individual calls. This is more efficient and is the intended usage pattern.

    Args:
        entries (List[Dict]): One or more lookup entry objects to create. All entries
            in a single call MUST belong to the same lookup type (the URL is derived
            from the first entry's 'type' field).

            Each entry dict supports the following fields:
                - tenantId (str, required): RDM tenant ID (e.g., 'ndZmT8187MY7L0L').
                - type (str, required): Full lookup type URI
                    (e.g., 'rdm/lookupTypes/AddressTypes').
                - code (str, required): Canonical lookup code
                    (e.g., 'ShipTo').
                - label (str, optional): Human-readable display label
                    (e.g., 'Shipping Address').
                - enabled (bool, optional): Whether the lookup is active.
                    Defaults to True.
                - sourceMappings (List[Dict], optional): Source system mappings.
                    Each mapping has:
                        - source (str): Source system name (e.g., 'SAP').
                        - values (List[Dict]): Source-specific values, each with:
                            - operation (str): 'ADD' or 'DELETE'.
                            - code (str): Source code value.
                            - value (str): Source display value.
                            - enabled (bool): Whether the value is active.
                            - canonicalValue (bool): Whether this is canonical.
                            - downStreamDefaultValue (bool): Downstream default flag.

        tenant_id (str): RDM tenant ID used for URL routing and activity logging.
            Defaults to the RDM_TENANT_ID environment variable.

    Returns:
        A YAML-formatted string of the API response.

    Example — adding two entries in one call:
        entries = [
            {
                "tenantId": "ndZmT8187MY7L0L",
                "type": "rdm/lookupTypes/AddressTypes",
                "code": "ShipTo",
                "label": "Shipping Address",
                "enabled": True,
                "sourceMappings": [
                    {
                        "source": "SAP",
                        "values": [
                            {
                                "operation": "ADD",
                                "code": "ShipTo",
                                "value": "Shipping To",
                                "enabled": True,
                                "canonicalValue": True,
                                "downStreamDefaultValue": True
                            }
                        ]
                    }
                ]
            },
            {
                "tenantId": "ndZmT8187MY7L0L",
                "type": "rdm/lookupTypes/AddressTypes",
                "code": "ReturnTo",
                "label": "Returning Address",
                "enabled": True
            }
        ]
    """
    try:
        if not entries or not isinstance(entries, list):
            return create_error_response(
                "VALIDATION_ERROR",
                "entries must be a non-empty list of lookup entry objects"
            )

        # Derive the lookup_type_short from the first entry for URL construction
        first_type: str = entries[0].get("type", "")
        if first_type.startswith('rdm/lookupTypes/'):
            lookup_type_short = first_type[len('rdm/lookupTypes/'):]
        else:
            lookup_type_short = first_type

        # Ensure tenantId is set on every entry (fallback to tenant_id parameter)
        normalised_entries: List[Dict] = []
        for entry in entries:
            e = dict(entry)
            e.setdefault("tenantId", tenant_id)
            e.setdefault("enabled", True)
            e.setdefault("localizations", [])
            e.setdefault("attributes", [])
            # Normalise type to full URI if caller passed the short form
            if e.get("type") and not e["type"].startswith("rdm/lookupTypes/"):
                e["type"] = f"rdm/lookupTypes/{e['type']}"
            normalised_entries.append(e)

        try:
            request = RdmLookupAddRequest(
                rdm_tenant=tenant_id,
                lookup_type_short=lookup_type_short,
                entries=normalised_entries
            )
        except ValueError as e:
            logger.warning(f"Validation error in rdm_lookups_add: {str(e)}")
            return create_error_response(
                "VALIDATION_ERROR",
                f"Invalid input parameters: {str(e)}"
            )

        # Construct the URL: POST /lookups/{rdm_tenant}/{TYPE}
        url = get_rdm_url(request.lookup_type_short, request.rdm_tenant)
        try:
            headers = get_reltio_headers()
            validate_connection_security(url, headers)
        except Exception as e:
            logger.error(f"Authentication or security error in rdm_lookups_add: {str(e)}")
            return create_error_response(
                "AUTHENTICATION_ERROR",
                "Failed to authenticate with Reltio API"
            )

        # Serialize entries to plain dicts for the API body
        payload = [entry.model_dump(exclude_none=True) for entry in request.entries]
        try:
            result = http_request(url, method='POST', headers=headers, data=payload)
        except Exception as e:
            logger.error(f"API request error in rdm_lookups_add: {str(e)}")
            return create_error_response(
                "SERVER_ERROR",
                f"Failed to create lookup in RDM API: {str(e)}"
            )

        try:
            codes = ", ".join(e.get("code", "") for e in normalised_entries)
            await ActivityLog.execute_and_log_activity(
                tenant_id=tenant_id,
                label=ActivityLogLabel.LOOKUP_ADD.value,
                client_type=ACTIVITY_CLIENT,
                description=(
                    f"rdm_lookups_add_tool: Successfully created {len(normalised_entries)} "
                    f"lookup(s) [{codes}] for lookup_type '{first_type}'"
                )
            )
        except Exception as log_error:
            logger.error(f"Activity logging failed for rdm_lookups_add: {str(log_error)}")

        return yaml.dump(result, sort_keys=False)

    except Exception as e:
        logger.error(f"Unexpected error in rdm_lookups_add: {str(e)}")
        return create_error_response(
            "SERVER_ERROR",
            "An unexpected error occurred while processing your request"
        )

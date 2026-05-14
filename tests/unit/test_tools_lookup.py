import pytest
from unittest.mock import patch, MagicMock
import yaml
from src.tools.lookup import rdm_lookups_list, rdm_lookups_partial_update, rdm_lookup_types_list

LOOKUP_TYPE = "rdm/lookupTypes/VistaVegetarianOrVegan"
TENANT_ID = "test-tenant"

@pytest.mark.asyncio
class TestRdmLookupsList:
    """Test cases for the rdm_lookups_list function"""
    
    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_success(self, mock_request, mock_url, mock_headers, mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test successful lookup list retrieval"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""
        
        mock_url.return_value = f"https://reltio.com/lookups/list"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = [
            {"id": "lookup1", "displayName": "Vegetarian", "value": "VEG"},
            {"id": "lookup2", "displayName": "Vegan", "value": "VEGAN"}
        ]
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_with_prefix(self, mock_request, mock_url, mock_headers, mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test lookup list retrieval with display name prefix"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 5
        mock_request.return_value.display_name_prefix = "Veg"
        
        mock_url.return_value = f"https://reltio.com/lookups/list"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = [
            {"id": "lookup1", "displayName": "Vegetarian", "value": "VEG"}
        ]
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 5, "Veg")
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_empty_result(self, mock_request, mock_url, mock_headers, mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test lookup list retrieval with empty result"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""
        
        mock_url.return_value = f"https://reltio.com/lookups/list"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = []
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity", side_effect=Exception("Logging failed"))
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_success_with_activity_log_failure(self, mock_request, mock_url, mock_headers, mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test successful lookup list retrieval with activity logging failure"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""
        
        mock_url.return_value = f"https://reltio.com/lookups/list"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = [
            {"id": "lookup1", "displayName": "Vegetarian", "value": "VEG"}
        ]
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()

    @patch("src.tools.lookup.LookupListRequest", side_effect=ValueError("Invalid lookup type"))
    async def test_rdm_lookups_list_validation_error(self, mock_request):
        """Test lookup list retrieval with validation error"""
        result = await rdm_lookups_list("invalid-lookup-type", TENANT_ID, 10, "")
        assert result["error"]["code_key"] == "VALIDATION_ERROR"

    @patch("src.tools.lookup.validate_connection_security", side_effect=Exception("Auth failed"))
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_authentication_error(self, mock_request, mock_url, mock_headers, mock_validate):
        """Test lookup list retrieval with authentication error"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result["error"]["code_key"] == "AUTHENTICATION_ERROR"

    @patch("src.tools.lookup.http_request", side_effect=Exception("API error"))
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_api_error(self, mock_request, mock_url, mock_headers, mock_validate, mock_http):
        """Test lookup list retrieval with API error"""
        # Mock the request model
        mock_request.return_value.lookup_type = LOOKUP_TYPE
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""

        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result["error"]["code_key"] == "SERVER_ERROR"

    @patch("src.tools.lookup.LookupListRequest", side_effect=Exception("Unexpected error"))
    async def test_rdm_lookups_list_unexpected_error(self, mock_request):
        """Test lookup list retrieval with unexpected error"""
        result = await rdm_lookups_list(LOOKUP_TYPE, TENANT_ID, 10, "")
        assert result["error"]["code_key"] == "SERVER_ERROR"

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_reltio_url")
    @patch("src.tools.lookup.LookupListRequest")
    async def test_rdm_lookups_list_all_lookup_type(self, mock_request, mock_url, mock_headers, mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test lookup list retrieval with 'all' lookup type"""
        # Mock the request model
        mock_request.return_value.lookup_type = "all"
        mock_request.return_value.tenant_id = TENANT_ID
        mock_request.return_value.max_results = 10
        mock_request.return_value.display_name_prefix = ""
        
        mock_url.return_value = f"https://reltio.com/lookups/list"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = [
            {"id": "lookup1", "displayName": "Vegetarian", "value": "VEG"},
            {"id": "lookup2", "displayName": "Vegan", "value": "VEGAN"}
        ]
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_list("all", TENANT_ID, 10, "")
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()


RDM_TENANT = "ndZmT8187MY7L0L"
VALID_ENTRIES = [
    {
        "code": "US",
        "type": "rdm/lookupTypes/Country",
        "enabled": True,
        "sourceMappings": [
            {
                "source": "CRM",
                "values": [
                    {
                        "operation": "UPDATE",
                        "code": "US",
                        "value": "United States of America",
                        "enabled": True,
                        "canonicalValue": True
                    }
                ]
            }
        ]
    }
]


@pytest.mark.asyncio
class TestRdmLookupsPartialUpdate:
    """Test cases for the rdm_lookups_partial_update function"""

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_url")
    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest")
    async def test_partial_update_success(self, mock_request, mock_url, mock_headers,
                                          mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test successful partial update"""
        mock_entry = MagicMock()
        mock_entry.code = "US"
        mock_entry.model_dump.return_value = VALID_ENTRIES[0]

        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.entries = [mock_entry]

        mock_url.return_value = f"https://rdm.reltio.com/lookups/{RDM_TENANT}/_update"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = {"status": "ok"}
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_partial_update(VALID_ENTRIES, RDM_TENANT, TENANT_ID)
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()

    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest", side_effect=ValueError("Invalid entries"))
    async def test_partial_update_validation_error(self, mock_request):
        """Test partial update with validation error"""
        result = await rdm_lookups_partial_update([], RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "VALIDATION_ERROR"

    @patch("src.tools.lookup.validate_connection_security", side_effect=Exception("Auth failed"))
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_url")
    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest")
    async def test_partial_update_authentication_error(self, mock_request, mock_url,
                                                       mock_headers, mock_validate):
        """Test partial update with authentication error"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.entries = []

        result = await rdm_lookups_partial_update(VALID_ENTRIES, RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "AUTHENTICATION_ERROR"

    @patch("src.tools.lookup.http_request", side_effect=Exception("API error"))
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_url")
    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest")
    async def test_partial_update_api_error(self, mock_request, mock_url, mock_headers,
                                            mock_validate, mock_http):
        """Test partial update with API error"""
        mock_entry = MagicMock()
        mock_entry.code = "US"
        mock_entry.model_dump.return_value = VALID_ENTRIES[0]

        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.entries = [mock_entry]

        result = await rdm_lookups_partial_update(VALID_ENTRIES, RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "SERVER_ERROR"

    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest", side_effect=Exception("Unexpected"))
    async def test_partial_update_unexpected_error(self, mock_request):
        """Test partial update with unexpected error"""
        result = await rdm_lookups_partial_update(VALID_ENTRIES, RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "SERVER_ERROR"

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity", side_effect=Exception("Log failed"))
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_url")
    @patch("src.tools.lookup.RdmLookupPartialUpdateRequest")
    async def test_partial_update_success_with_activity_log_failure(self, mock_request, mock_url,
                                                                    mock_headers, mock_validate,
                                                                    mock_http, mock_dump, mock_activity_log):
        """Test successful partial update even when activity logging fails"""
        mock_entry = MagicMock()
        mock_entry.code = "US"
        mock_entry.model_dump.return_value = VALID_ENTRIES[0]

        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.entries = [mock_entry]

        mock_url.return_value = f"https://rdm.reltio.com/lookups/{RDM_TENANT}/_update"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = {"status": "ok"}
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookups_partial_update(VALID_ENTRIES, RDM_TENANT, TENANT_ID)
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()


@pytest.mark.asyncio
class TestRdmLookupTypesList:
    """Test cases for the rdm_lookup_types_list function"""

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_config_url")
    @patch("src.tools.lookup.RdmLookupTypesListRequest")
    async def test_lookup_types_list_success(self, mock_request, mock_url, mock_headers,
                                             mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test successful lookup types list retrieval"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.tenant_id = TENANT_ID

        mock_url.return_value = f"https://rdm.reltio.com/configuration/{RDM_TENANT}"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = {
            "tenantId": RDM_TENANT,
            "lookupTypes": [
                {"uri": "rdm/lookupTypes/Gender", "label": "Gender", "enabled": True},
                {"uri": "rdm/lookupTypes/Country", "label": "Country", "enabled": True}
            ]
        }
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()
        mock_dump.assert_called_once()

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity")
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_config_url")
    @patch("src.tools.lookup.RdmLookupTypesListRequest")
    async def test_lookup_types_list_empty(self, mock_request, mock_url, mock_headers,
                                           mock_validate, mock_http, mock_dump, mock_activity_log):
        """Test lookup types list retrieval with no lookup types"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.tenant_id = TENANT_ID

        mock_url.return_value = f"https://rdm.reltio.com/configuration/{RDM_TENANT}"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = {"tenantId": RDM_TENANT, "lookupTypes": []}
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()

    @patch("src.tools.lookup.RdmLookupTypesListRequest", side_effect=ValueError("rdm_tenant is required"))
    async def test_lookup_types_list_validation_error(self, mock_request):
        """Test lookup types list with validation error"""
        result = await rdm_lookup_types_list("", TENANT_ID)
        assert result["error"]["code_key"] == "VALIDATION_ERROR"

    @patch("src.tools.lookup.validate_connection_security", side_effect=Exception("Auth failed"))
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_config_url")
    @patch("src.tools.lookup.RdmLookupTypesListRequest")
    async def test_lookup_types_list_authentication_error(self, mock_request, mock_url,
                                                          mock_headers, mock_validate):
        """Test lookup types list with authentication error"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.tenant_id = TENANT_ID

        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "AUTHENTICATION_ERROR"

    @patch("src.tools.lookup.http_request", side_effect=Exception("API error"))
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_config_url")
    @patch("src.tools.lookup.RdmLookupTypesListRequest")
    async def test_lookup_types_list_api_error(self, mock_request, mock_url, mock_headers,
                                               mock_validate, mock_http):
        """Test lookup types list with API error"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.tenant_id = TENANT_ID

        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "SERVER_ERROR"

    @patch("src.tools.lookup.ActivityLog.execute_and_log_activity", side_effect=Exception("Log failed"))
    @patch("src.tools.lookup.yaml.dump")
    @patch("src.tools.lookup.http_request")
    @patch("src.tools.lookup.validate_connection_security")
    @patch("src.tools.lookup.get_reltio_headers")
    @patch("src.tools.lookup.get_rdm_config_url")
    @patch("src.tools.lookup.RdmLookupTypesListRequest")
    async def test_lookup_types_list_success_with_activity_log_failure(self, mock_request, mock_url,
                                                                       mock_headers, mock_validate,
                                                                       mock_http, mock_dump, mock_activity_log):
        """Test successful lookup types list even when activity logging fails"""
        mock_request.return_value.rdm_tenant = RDM_TENANT
        mock_request.return_value.tenant_id = TENANT_ID

        mock_url.return_value = f"https://rdm.reltio.com/configuration/{RDM_TENANT}"
        mock_headers.return_value = {"Authorization": "Bearer token"}
        mock_http.return_value = {
            "tenantId": RDM_TENANT,
            "lookupTypes": [{"uri": "rdm/lookupTypes/Gender", "label": "Gender", "enabled": True}]
        }
        mock_dump.return_value = "yaml_output"

        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result == "yaml_output"
        mock_activity_log.assert_called_once()

    @patch("src.tools.lookup.RdmLookupTypesListRequest", side_effect=Exception("Unexpected"))
    async def test_lookup_types_list_unexpected_error(self, mock_request):
        """Test lookup types list with unexpected error"""
        result = await rdm_lookup_types_list(RDM_TENANT, TENANT_ID)
        assert result["error"]["code_key"] == "SERVER_ERROR"

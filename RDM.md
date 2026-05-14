## Add a new lookup value

RDM_API_URL=https://rdm.reltio.com
RDM_TENANT_ID=ndZmT8187MY7L0L

POST ${RDM_API_URL}/services/lookups/${RDM_TENANT_ID}/${TYPE}
Body:

```json
[
  {
    "tenantId": "RDM_TENANT_ID",
    "type": "rdm/lookupTypes/TYPE",
    "code": "US",
    "enabled": true,
    "sourceMappings": [
      {
        "source": "Reltio",
        "values": [
          {
            "code": "RLT_US",
            "value": "United States of America",
            "description": "USA definition in the Reltio source system.",
            "enabled": true,
            "canonicalValue": false,
            "downStreamDefaultValue": false
          }
        ]
      }
    ],
    "localizations": [],
    "attributes": []
  }
]
```

When a user asks to create a lookup value inside lets say for example Country, the MCP server should use this
REST API call to create it. if the TYPE value is not mentioned by user i.e ("type": "rdm/lookupTypes/TYPE"), the llm should ask back user in which type it should create the lookup value.

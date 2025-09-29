# Description
This readme explains how to use [mcp inspector](https://modelcontextprotocol.io/docs/tools/inspector) to connect to OCI hosted remote MCP server. Once you have an ACTIVE Model deployment resource hosting your MCP server, we can use MCP inspector to connect and make list/call tools to MCP server.

# Prerequisites

To enable generating OCI Auth credentials before making API calls to Model deployment endpoints, we will create a local proxy server, which will intercept calls from inspector, created OCI auth and adds required header for outgoing calls.

- Install pip dependencies mentioned in [requirements.txt](./requirements.txt)
```
pip install -r requirements.txt
```

- Start [oci_proxy.py](./oci_proxy.py)
```
python3 oci_proxy.py
```

- Create OCI session and populate your local OCI config files with valid [session details](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/clitoken.htm)
```
oci session authenticate
```

- Start mcp inspector on your local
```
npx @modelcontextprotocol/inspector
```

- Configure MCP inspector with configuration as:
   - Transport type: Stramble HTTP
   - URL: http://localhost:8000/proxy/{endpoint-URI-Path}/predict?target_host={endpoint-region-host}

   (Use model deployment invoke endpoint details from console to fill these values. For example : endpoint-URI-Path = ocid1.datasciencemodeldeployment.oc1....... and endpoint-region-host = modeldeployment.us-ashburn-1.oci.customer-oci.com)

- Click connect and the status should show "Connected", as shown in [screenshot](./screenshot.png)
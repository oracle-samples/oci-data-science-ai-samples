import json

import requests
import oci

MCP_SESSION_ID = "mcp-session-id"

def get_auth():
    PROFILE_NAME = 'DEFAULT'
    SECURITY_TOKEN_FILE_KEY = 'security_token_file'
    KEY_FILE_KEY = 'key_file'
    config = oci.config.from_file(profile_name=PROFILE_NAME)
    token_file = config[SECURITY_TOKEN_FILE_KEY]
    token = None
    with open(token_file, 'r') as f:
      token = f.read()
    private_key = oci.signer.load_private_key_from_file(config[KEY_FILE_KEY])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key) 
    return signer

def initializeSession(url):
   request_headers = {
      "Accept-Encoding":"gzip, deflate, br, zstd", 
      "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8", 
      "Connection":"keep-alive", 
      "accept":"application/json, "
      "text/event-stream", 
      "content-type":"application/json"
    }
   
   request_body = json.dumps({
      "method":"initialize",
      "params": {
        "protocolVersion":"2025-03-26",
         "capabilities": {
            "sampling":{},
            "roots": {
               "listChanged":True
             }
          },
          "clientInfo": {
             "name":"oci-cli",
             "version":"0.14.0"
          }
        },
        "jsonrpc":"2.0",
        "id":0
    })
   response = requests.request("POST", url, headers=request_headers, data=request_body, auth=get_auth(), verify=False)
   print("Initialized instance")
   print(response.content)
   print(response.headers)
   return response.headers[MCP_SESSION_ID]

def initializeGroup(url, mcpSessionId):
    request_headers = {
      "Accept-Encoding":"gzip, deflate, br, zstd", 
      "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8", 
      "Connection":"keep-alive", 
      "accept":"application/json, "
      "text/event-stream", 
      "content-type":"application/json",
      MCP_SESSION_ID: mcpSessionId
    }
   
    request_body = json.dumps({"method":"notifications/initialized","jsonrpc":"2.0"})
    response = requests.request("POST", url, headers=request_headers, data=request_body, auth=get_auth(), verify=False)
    print("Initialized group")

def listTools(url, mcpSessionId):
    request_headers = {
      "Accept-Encoding":"gzip, deflate, br, zstd", 
      "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8", 
      "Connection":"keep-alive", 
      "accept":"application/json, "
      "text/event-stream", 
      "content-type":"application/json",
      MCP_SESSION_ID: mcpSessionId
    }
   
    request_body = json.dumps({"method":"notifications/initialized","jsonrpc":"2.0"})
    response = requests.request("POST", url, headers=request_headers, data=request_body, auth=get_auth(), verify=False)
    print("Listing available tools")
    print(response)


def callTools(url, mcpSessionId):
    request_headers = {
      "Accept-Encoding":"gzip, deflate, br, zstd", 
      "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8", 
      "Connection":"keep-alive", 
      "accept":"application/json, "
      "text/event-stream", 
      "content-type":"application/json",
      MCP_SESSION_ID: mcpSessionId
    }

    request_body = json.dumps({"method":"tools/call","params":{"name":"start-notification-stream","arguments":{"interval":2,"count":5,"caller":"nipun"},"_meta":{"progressToken":2}},"jsonrpc":"2.0","id":2})

    with requests.request("POST", url, headers=request_headers, data=request_body, auth=get_auth(), verify=False, stream=True) as response:
      response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
      for chunk in response.iter_content(chunk_size=8192): # 8192 is the default chunk size
          if chunk: # Filter out keep-alive new chunks
              print(chunk)

if __name__ == "__main__":
     predict_url = 'https://modeldeployment-int.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeploymentint.oc1.iad.amaaaaaav66vvniawc3d32h3m44nfnbjxksjg4x2fea6gtakduafevclee7a/predictWithResponseStream'
    
     # Generate MCP session id
     mcpSessionId = initializeSession(predict_url)

     # initialise group
     initializeGroup(predict_url, mcpSessionId)

     # list tools
     listTools(predict_url, mcpSessionId)

     # call streaming tool
     callTools(predict_url, mcpSessionId)

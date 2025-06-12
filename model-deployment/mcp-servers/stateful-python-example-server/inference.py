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
   
    request_body = json.dumps({"method":"tools/list","params":{"_meta":{"progressToken":1}},"jsonrpc":"2.0","id":1})
    response = requests.request("POST", url, headers=request_headers, data=request_body, auth=get_auth(), verify=False)
    print("Listing available tools")
    print(response.content)


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
     predict_url = '<MODEL_DEPLOYMENT_STREAMING_URL..../predictWithResponseStream>'
    
     # Generate MCP session id
     mcpSessionId = initializeSession(predict_url)

     # initialise group
     initializeGroup(predict_url, mcpSessionId)

     # list tools
     listTools(predict_url, mcpSessionId)

     # call streaming tool
     callTools(predict_url, mcpSessionId)

# Sample run logs - 

# > python3 inference.py 
#Initialized instance
#b'id: 825b5179-1ad3-425a-8dc3-95f3f369278b\r\nevent: message\r\ndata: {"jsonrpc":"2.0","id":0,"result":{"protocolVersion":"2025-03-26","capabilities":{"experimental":{},"tools":{"listChanged":false}},"serverInfo":{"name":"mcp-streamable-http-demo","version":"1.9.4.dev7+29c69e6"}}}\r\n\r\n'
#{'date': 'Thu, 12 Jun 2025 06:01:19 GMT', 'server': 'uvicorn', 'cache-control': 'no-cache, no-transform', 'connection': 'keep-alive', 'content-type': 'text/event-stream', 'mcp-session-id': '4161e6185f934d289dbe7e61c32f3d97', 'x-accel-buffering': 'no', 'Transfer-Encoding': 'chunked'}
#Initialized group
#Listing available tools
#<Response [202]>
#b'id: a8beaa09-36f5-4943-bf2f-a1e141805a3c\r\nevent: message\r\ndata: {"method":"notifications/message","params":{"level":"info","logger":"notification_stream","data":"[1/5] Event from \'nipun\' - Use Last-Event-ID to resume if disconnected"},"jsonrpc":"2.0"}\r\n\r\n'
#b'id: b81de9d0-b520-4714-8b07-75a8d57f1bc1\r\nevent: message\r\ndata: {"method":"notifications/message","params":{"level":"info","logger":"notification_stream","data":"[2/5] Event from \'nipun\' - Use Last-Event-ID to resume if disconnected"},"jsonrpc":"2.0"}\r\n\r\n'
#b'id: 2ae71b1c-63d5-4f37-8830-e209e5beedf0\r\nevent: message\r\ndata: {"method":"notifications/message","params":{"level":"info","logger":"notification_stream","data":"[3/5] Event from \'nipun\' - Use Last-Event-ID to resume if disconnected"},"jsonrpc":"2.0"}\r\n\r\n'
#b'id: bf26d789-170d-40f2-b67c-10c1f5f191cb\r\nevent: message\r\ndata: {"method":"notifications/message","params":{"level":"info","logger":"notification_stream","data":"[4/5] Event from \'nipun\' - Use Last-Event-ID to resume if disconnected"},"jsonrpc":"2.0"}\r\n\r\n'
#b'id: b3bb3f5a-729f-4347-b64a-aad02a8a2d33\r\nevent: message\r\ndata: {"method":"notifications/message","params":{"level":"info","logger":"notification_stream","data":"[5/5] Event from \'nipun\' - Use Last-Event-ID to resume if disconnected"},"jsonrpc":"2.0"}\r\n\r\n'
#b'id: aa0837f6-ac17-4aa7-97a6-3bc7046a1ead\r\nevent: message\r\ndata: {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"Sent 5 notifications with 2s interval for caller: nipun"}],"isError":false}}\r\n\r\n'


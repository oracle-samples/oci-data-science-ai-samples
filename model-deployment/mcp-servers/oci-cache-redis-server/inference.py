import json

import requests
import oci


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

def predict():
    predict_url = '<MODEL_DEPLOYMENT_URL>'
    # list tools
    predict_body = json.dumps({"method":"tools/list","params":{"_meta":{"progressToken":1}},"jsonrpc":"2.0","id":1})
    # call tools
    # predict_body = json.dumps({"method":"tools/call","params":{"name":"start-notification-stream","arguments":{"interval":7,"count":1,"caller":"nipun"},"_meta":{"progressToken":3}},"jsonrpc":"2.0","id":3})
    
    predict_headers = {
        'Connection': 'keep-alive',
        'accept': 'application/json, text/event-stream',
        'content-type': 'application/json'
        #'mcp-session-id':'<MCP-SESSION_ID>' # Can be found in predict logs, only needed when stateful deployment
    }

    response = requests.request("POST", predict_url, headers=predict_headers, data=predict_body, auth=get_auth(), verify=False)
    print(response.content)


if __name__ == "__main__":
    predict()
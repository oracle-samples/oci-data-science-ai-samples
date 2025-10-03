import asyncio
import requests
import oci
from mcp.client.session_group import StreamableHttpParameters
from oracle.adk import Agent, AgentClient
from oracle.adk.mcp import MCPClientStreamableHttp

MCP_SERVER_URL = <MODEL_DEPLOYMENT_URL>
GENAI_ENDPOINT = "<ocid1.genaiagentendpoint.oc....>"
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
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key, body_headers=["content-type", "x-content-sha256"])
    return signer

def oci_auth_headers():
    signer=get_auth()
    request = requests.Request("POST", MCP_SERVER_URL, auth=signer, headers={'Content-Type': 'application/json'})
    prepared = request.prepare()
    signer(prepared)
    del(prepared.headers['content-length'])
    return prepared.headers

async def main():

    headers = oci_auth_headers()
    client = AgentClient(
        auth_type="security_token",
        profile="DEFAULT",
        region="us-ashburn-1",
    )

    params = StreamableHttpParameters(
        url=MCP_SERVER_URL,
        headers=headers
    )

    async with MCPClientStreamableHttp(
        params=params,
        name="Streamable MCP Server",
    ) as mcp_client:
        agent = Agent(
            client=client,
            agent_endpoint_id=GENAI_ENDPOINT,
            instructions="Use the tools to answer the questions.",
            tools=[await mcp_client.as_toolkit()],
        )
        agent.setup()
        print("Done", mcp_client, agent)
        #mcp_client.list_tools()

if __name__ == "__main__":
    asyncio.run(main())
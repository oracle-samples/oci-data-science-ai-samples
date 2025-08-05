import logging
from typing import Any
from uuid import uuid4
import httpx
import oci
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)

class OCISignerAuth(httpx.Auth):
    def __init__(self, signer):
        self.signer = signer
    def auth_flow(self, request):
        import requests
        req = requests.Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            data=request.content
        ).prepare()
        self.signer(req)
        for k, v in req.headers.items():
            request.headers[k] = v
        yield request

def get_auth():
    PROFILE_NAME = 'default'
    SECURITY_TOKEN_FILE_KEY = 'security_token_file'
    KEY_FILE_KEY = 'key_file'
    config = oci.config.from_file(profile_name=PROFILE_NAME)
    token_file = config[SECURITY_TOKEN_FILE_KEY]
    with open(token_file, 'r') as f:
        token = f.read()
    private_key = oci.signer.load_private_key_from_file(config[KEY_FILE_KEY])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    return OCISignerAuth(signer)

def get_auth_rps():
    print(f'[DEBUG] Getting RPS auth')
    rps = oci.auth.signers.get_resource_principals_signer()
    print(f'[DEBUG] RPS auth: {rps}')
    print(f'[DEBUG] RPS token: {rps.get_security_token()}')
    return OCISignerAuth(rps)

async def main() -> None:
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = '<add your custom url mdocid url here taken from the invoke your model screen in model deployment console>'
    async with httpx.AsyncClient(auth=get_auth(), verify=False, headers={"Content-Length": "0"}) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        final_agent_card_to_use: AgentCard | None = None
        try:
            logger.info(
                f'Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}'
            )
            _public_card = (
                await resolver.get_agent_card()
            )
            logger.info('Successfully fetched public agent card:')
            logger.info(
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card
            logger.info(
                '\nUsing PUBLIC agent card for client initialization (default).'
            )
            if _public_card.supportsAuthenticatedExtendedCard:
                try:
                    logger.info(
                        f'\nPublic card supports authenticated extended card. Attempting to fetch from: {base_url}{EXTENDED_AGENT_CARD_PATH}'
                    )
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    logger.info(
                        'Successfully fetched authenticated extended agent card:'
                    )
                    logger.info(
                        _extended_card.model_dump_json(
                            indent=2, exclude_none=True
                        )
                    )
                    final_agent_card_to_use = (
                        _extended_card
                    )
                    logger.info(
                        '\nUsing AUTHENTICATED EXTENDED agent card for client initialization.'
                    )
                except Exception as e_extended:
                    logger.warning(
                        f'Failed to fetch extended agent card: {e_extended}. Will proceed with public card.',
                        exc_info=True,
                    )
            elif (
                _public_card
            ):
                logger.info(
                    '\nPublic card does not indicate support for an extended card. Using public card.'
                )
        except Exception as e:
            logger.error(
                f'Critical error fetching public agent card: {e}', exc_info=True
            )
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e
        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info('A2AClient initialized.')
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'how much is 10 USD in INR?'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        response = await client.send_message(request)
        print(response.model_dump(mode='json', exclude_none=True))
        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        stream_response = client.send_message_streaming(streaming_request)
        async for chunk in stream_response:
            print(chunk.model_dump(mode='json', exclude_none=True))

async def get_agent_answer(base_url: str, question: str) -> str:
    print(f'[DEBUG] Sending request to other agent: {base_url}')
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    async with httpx.AsyncClient(auth=get_auth_rps(), verify=False, headers={"Content-Length": "0"}) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        _public_card = await resolver.get_agent_card()
        print(f'[DEBUG] Resolved agent card: {_public_card}')
        client = A2AClient(
            httpx_client=httpx_client, agent_card=_public_card
        )
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': question}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        response = await client.send_message(request)
        print(f'[DEBUG] Response: {response}')
        try:
            parts = response.result.message.parts
            for part in parts:
                if 'text' in part:
                    return part['text']
            return str(response.model_dump(mode='json', exclude_none=True))
        except Exception:
            return str(response.model_dump(mode='json', exclude_none=True))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
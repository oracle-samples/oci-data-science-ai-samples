import io
import json
import logging
import oci
import requests
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    auth = oci.auth.signers.get_resource_principals_signer()
    logger = logging.getLogger()
    try:
        logger.info("Inside function")
        body = json.loads(data.getvalue())
        logger.info("Body : " + json.dumps(body))
        headers = ctx.Headers()
        logger.info("Headers: " + json.dumps(headers))
        endpoint = body.get("ENDPOINT")
        payload = body.get("PAYLOAD")
        resp = requests.post(endpoint, json=json.loads(payload), auth=auth)
        logger.info("response : " + resp.json())
    except (Exception, ValueError) as ex:
        logger.error("Failed to call endpoint with ex : {}".format(str(ex)))
    return response.Response(
            ctx, response_data=resp.json(),
            headers={"Content-Type": "application/json"}
        )

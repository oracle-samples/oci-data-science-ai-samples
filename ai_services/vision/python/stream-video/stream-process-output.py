import time
import base64
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import json
import oci
from oci.object_storage import ObjectStorageClient


NAMESPACE = ""
BUCKET = ""
PREFIX = ""
CONFIG_PROFILE = ""


def decode_image(image_data):
    """Decode base64 image to OpenCV format and ensure it has 3 channels (RGB)."""
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def process_and_display(message):
    """Process detection data and update the window."""
    message = message.replace("'", '"')  # Make it valid JSON
    message_dict = json.loads(message)

    image = decode_image(message_dict['imageData'])
    if len(message_dict['detectedObjects']) > 0:
        face_id = message_dict['detectedObjects'][0]['objectId']
        print("face detected", face_id)

    print(message_dict['detectedObjects'])
    # Uncomment if you want to visualize
    annotated_image = draw_faces(image, message_dict['detectedObjects'], message_dict["imageData"])
    cv2.imshow("Face Detection", annotated_image)
    cv2.waitKey(1)


def draw_faces(image, faces, frame):
    """Draw bounding boxes around detected faces."""
    height, width, _ = image.shape
    for face in faces:
        if face['name'] == 'weapon':
            vertices = face['boundingPolygon']['normalizedVertices']
            pts = [(int(v['x'] * width), int(v['y'] * height)) for v in vertices]
            cv2.polylines(image, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=2)
    if frame is not None:
        # Add frame number text in the top right corner
        text = f"Frame: {frame}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)
        thickness = 1
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = width - text_size[0] - 10
        text_y = 30
        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness)

    return image


def main():
    # Configure OCI client
    config = oci.config.from_file('~/.oci/config', profile_name=CONFIG_PROFILE)
    oendpoint = "https://objectstorage.us-ashburn-1.oraclecloud.com"

    token_file = config['security_token_file']
    with open(token_file, 'r') as f:
        token = f.read()

    private_key = oci.signer.load_private_key_from_file(config['key_file'])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    object_storage_client = ObjectStorageClient(config=config, signer=signer, service_endpoint=oendpoint)

    while True:
        ts_ns = int(time.time() * 1_000_000_000) - 3_000_000_000
        filename = f"new1/frame_{ts_ns}.json"

        objects = object_storage_client.list_objects(
            namespace_name=NAMESPACE,
            bucket_name=BUCKET,
            prefix=PREFIX,
            start_after=filename
        ).data.objects

        if objects:
            obj_name = objects[0].name
            resp = object_storage_client.get_object(
                namespace_name=NAMESPACE,
                bucket_name=BUCKET,
                object_name=obj_name
            )
            content = resp.data.content.decode("utf-8")
            process_and_display(content)
            print(f"File: {obj_name}")
            # print(content)

        time.sleep(1)


if __name__ == "__main__":
    main()
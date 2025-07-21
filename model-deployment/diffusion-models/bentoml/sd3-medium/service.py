import typing as t
import bentoml
from PIL.Image import Image
from annotated_types import Le, Ge
from typing_extensions import Annotated
import oci
import io
import os


MODEL_ID = "stabilityai/stable-diffusion-3-medium-diffusers"

sample_prompt = "A cat holding a sign that says hello world"

def get_oss_client():
    print("Getting Resource Principal authenticated in ObjectStorage client")
    return oci.object_storage.ObjectStorageClient({}, signer=oci.auth.signers.get_resource_principals_signer(), service_endpoint="https://objectstorage.us-ashburn-1.oraclecloud.com")

object_storage_client = get_oss_client()

@bentoml.service(
    traffic={"timeout": 300},
    workers=1,
    resources={
        "gpu": 1,
        "gpu_type": "nvidia-l4",
    },
)
class SD3Medium:
    def __init__(self) -> None:
        import torch
        from diffusers import StableDiffusion3Pipeline

        self.pipe = StableDiffusion3Pipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
        )
        self.pipe.to(device="cuda")

    def __is_ready__(self) -> bool:
      return True

    @bentoml.api(route="/predict")
    def txt2img(
            self,
            prompt: str = sample_prompt,
            negative_prompt: t.Optional[str] = None,
            num_inference_steps: Annotated[int, Ge(1), Le(50)] = 28,
            guidance_scale: float = 7.0,
    ) -> Image:
        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]
        namespace = os.getEnv("NAMESPACE")
        bucketName = os.getEnv("BUCKET_NAME")
        objectName = "image.jpg"
        in_mem_file = io.BytesIO()
        image.save(in_mem_file, "png")
        in_mem_file.seek(0)
        put_object_response = object_storage_client.put_object(namespace, bucketName, objectName, in_mem_file)
        return put_object_response.headers
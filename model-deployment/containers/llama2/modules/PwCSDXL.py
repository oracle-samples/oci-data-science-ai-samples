from diffusers import DiffusionPipeline
import torch
from pathlib import Path
import gc


model_id = "stabilityai/stable-diffusion-xl-base-1.0"
refiner_model_id = "stabilityai/stable-diffusion-xl-refiner-1.0"

model_dir = Path("/opt/sdxl/model/openvino-sd-xl-base-1.0")
refiner_model_dir = Path("/opt/sdxl/model/openvino-sd-xl-refiner-1.0")


if not model_dir.exists():
    print(f"Folder {model_dir} doesn't exist. Building...")
    base = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    # base.half()
    base.save_pretrained(model_dir)
    #text2image_pipe.compile()
    del base
    gc.collect()

base = DiffusionPipeline.from_pretrained(
    model_dir,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)

#base.to("cuda")
base.enable_model_cpu_offload()
# base.unet = torch.compile(base.unet, mode="reduce-overhead", fullgraph=True)

if not refiner_model_dir.exists():
    print(f"Folder {refiner_model_dir} doesn't exist. Building...")
    refiner = DiffusionPipeline.from_pretrained(refiner_model_id, text_encoder_2=base.text_encoder_2, vae=base.vae, torch_dtype=torch.float16, use_safetensors=True, variant="fp16",)
    # refiner.half()
    refiner.save_pretrained(refiner_model_dir)
    del refiner
    gc.collect()

refiner = DiffusionPipeline.from_pretrained(refiner_model_dir,
    text_encoder_2=base.text_encoder_2,
    vae=base.vae,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)

#refiner.to("cuda")
refiner.enable_model_cpu_offload()
# refiner.unet = torch.compile(refiner.unet, mode="reduce-overhead", fullgraph=True)

high_noise_frac = 0.8

def generate_from_text(text, negative_text, seed, base_steps, refiner_steps, width, height):
    image = base(
        prompt=text,
        negative_prompt=negative_text,
        num_inference_steps=base_steps,
        denoising_end=high_noise_frac,
        height=height,
        width=width,
        output_type="latent",
    ).images
    image = refiner(
        prompt=text,
        negative_prompt=negative_text,
        num_inference_steps=refiner_steps,
        denoising_start=high_noise_frac,
        image=image,
    ).images[0]
    return image


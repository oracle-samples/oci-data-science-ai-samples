# Introduction
Diffusion models are a type of generative model that learns to create new data samples by reversing a gradual process of adding noise to an initial sample. They work by first adding noise to real data points, gradually transforming them into pure noise, and then training a neural network to reverse this process, effectively learning to generate data from noise. 

[BentoML](https://github.com/bentoml/BentoML) is a Python library for building online serving systems optimized for AI apps and model inference. What sets it apart from other text generation frameworks, is that it can also support image generation usecases with Stable Diffusion 3 Medium, Stable Video Diffusion, Stable Diffusion XL Turbo, ControlNet, and LCM LoRAs.
In this sample, we are going to deploy [Stable Diffusion 3 Medium](https://github.com/bentoml/BentoDiffusion/tree/main/sd3-medium) with BentoML.

# Steps

## Dockerize
First let's dockerize our model serving framework using the [Dockerfile](./Dockerfile).
```
docker build -f Dockerfile -t bentoml:latest .  
```

## Create BentoML framework API code to serve Stable Diffusion 3 Medium
Refer the code in [directory](./sd3-medium). 
Note the changes that are done, in order to support it on OCI Data Science Model Deployment.
* Add readiness logic if needed, for checking health of model server.
* Add route in bentoml api to support `predict` api endpoint for image generation.
* Check OCI Buckets integration using resource principal, to put the generated images in the bucket of your choice.
NOTE - In order to allow model deployment service create objects in your bucket, add below policy -
```
allow any-user to manage objects in compartment <compartment> where ALL { request.principal.type='datasciencemodeldeployment', target.bucket.name='<BUCKET_NAME>' }
```

## Zip the artifact and create Model catalog entry
```
cd sd3-medium
zip -0 -r artifact.zip *
```
Use this zip to create simple model catalog entry and fetch the model ocid.

Note - Create a VCN, Subnet with internet connectivity in order to fetch the model of your choice, or choose model catalog method to bring the model along with bentoml files.

## Create Model deployment
Create model deployment using the [file](./model-deployment.py) as reference.

## Prediction
Once MD is active, use below oci cli request to send an image generation call -
```
oci raw-request --http-method POST --target-uri <MODEL_DEPLOYMENT_ENDPOINT> --request-body '{ "prompt": "A cat holding a sign that says hello World", "num_inference_steps": 10,"guidance_scale": 7.0 }' --request-headers '{"Content-Type":"application/json"}'
```

Generated image will be placed in chosen bucket.
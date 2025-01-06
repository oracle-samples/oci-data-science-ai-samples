# AI Quick Action - Batch Inferencing

#### This notebook offers a detailed, step-by-step guide for performing batch inference on LLMs using AI Quick Action.


```python
import os
from ads.jobs import Job, DataScienceJob, ContainerRuntime
import ads
import json

ads.set_auth("resource_principal")
```


```python
##  Update following variables as required

compartment_id = os.environ["PROJECT_COMPARTMENT_OCID"]
project_id = os.environ["PROJECT_OCID"]

log_group_id = "ocid1.loggroup.oc1.xxx.xxxxx"
log_id = "cid1.log.oc1.xxx.xxxxx"

instance_shape = "VM.GPU.A10.2"
region = "us-ashburn-1"

container_image = "dsmc://odsc-vllm-serving:0.6.2"

bucket = "<bucket_name>"  # this should be a versioned bucket
namespace = "<bucket_namespace>"
model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
hf_token = "<your-huggingface-token>"
oci_iam_type = "resource_principal"
prefix = "batch-inference"

job_artifacts = "job-artifacts"
```

## Prepare The JOB Artifacts

### 1. Create a **job_artifacts** folder


```python
os.makedirs(job_artifacts, exist_ok=True)
artifacts_path = os.path.expanduser(job_artifacts)
```

### 2. Add [**input.json**](notebook_examples/batch-inferencing-data/input.json) to **job_artifacts** folder

**Sample input.json**
```json

    {
        "vllm_engine_config": {
            "tensor_parallel_size": 2,
            "disable_custom_all_reduce": true
        },
        "sampling_config": {
            "max_tokens": 250,
            "temperature": 0.7,
            "top_p": 0.85
        },
        "data": [
            [
            {
                "role": "system",
                "content": "You are a friendly chatbot who is a great story teller."
            },
            {
                "role": "user",
                "content": "Tell me a 1000 words story"
            }
            ]
        ]
    }

```

This file defines the configuration and data for batch inferenceing. It contains the following key sections:

#### 1.1. vLLM Engine Configuration (`vllm_engine_config`)
The vLLM engine config from official [vllm documentation](https://docs.vllm.ai/en/latest/dev/offline_inference/llm.html) can be added here.

#### 1.2. Sampling Configuration (`sampling_config`)
- **`max_tokens`**: Specifies the maximum number of tokens the model can generate for each prompt, set to `250`.
- **`temperature`**: Controls the randomness of the sampling process, with a value of `0.7`, balancing between randomness and determinism.
- **`top_p`**: Controls the diversity of the generated text using nucleus sampling, set to `0.85`, meaning only the top 85% probable next tokens will be considered.

More details can be found [here](https://docs.vllm.ai/en/latest/dev/sampling_params.html#vllm.SamplingParams).

#### 1.3. Data Section (`data`)
The `data` section contains a list of messages. Each message object has two required fields:
- **`role`** : the role of the messenger (either system, user, assistant or tool)
- **`content`** : the content of the message (e.g., Write me a beautiful poem)

For more information on prompt engineering, please refer to the OpenAI prompt engineering [documentation](https://platform.openai.com/docs/guides/prompt-engineering/strategy-write-clear-instructions).


### 2. Creating the inferencing script within **job_artifacts** folder

This script is designed for batch inferencing using a VLLM engine, performing the following key tasks:

- Loads model configurations and Hugging Face credentials from environment variables.
- Initializes the model and tokenizer for inference.
- Processes input prompts in batches, generates responses, and uploads the generated results to an Object Storage bucket.



```python
%%writefile job-artifacts/vllm_batch_inferencing.py

from typing import Any, Dict, List, Union
import os
import json
import logging
import time
from ads.model.datascience_model import DataScienceModel
from vllm import LLM, SamplingParams
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
from ads.common.utils import ObjectStorageDetails
from ads.aqua.common.utils import upload_folder


## Constants class for centralized variable management
class Constants:
    import os

    # Environment variables used in the script
    OCI_IAM_TYPE = (
        "OCI_IAM_TYPE"  # Authentication type for OCI (Oracle Cloud Infrastructure)
    )
    INPUT_PROMPT = "input_prompt"  # Key for input prompt in data structure
    OUTPUT = "generated_output"  # Key for generated output in data structure
    VLLM_ENGINE_CONFIG = (
        "vllm_engine_config"  # Key for VLLM engine configuration in data
    )
    SAMPLING_CONFIG = "sampling_config"  # Key for sampling parameters in data
    MODEL = "MODEL"  # Environment variable for model selection
    HF_TOKEN = "HF_TOKEN"  # Environment variable for Hugging Face token
    OUTPUT_FOLDER_PATH = os.path.expanduser(
        "~/outputs"
    )  # Output folder path for generated data
    OUTPUT_FILE_PATH = os.path.join(
        OUTPUT_FOLDER_PATH, "output_prompts.json"
    )  # Path to save output prompts
    OS_OBJECT = "batch-inference"  # Object name used for storing in OCI


class Deployment:
    def __init__(self, vllm_config: List[Dict[str, Any]], **kwargs: Any) -> None:
        """
        Initializes the Deployment object.
        Loads the model and tokenizer using the provided VLLM configuration.
        Also handles authentication for Hugging Face using the token from environment variables.
        """
        print("Initializing VLLM with the provided model")

        # Login to Hugging Face if token is provided
        hf_token = os.environ.get(Constants.HF_TOKEN, "")
        if hf_token:
            login(token=hf_token)

        # Get model name from environment variables,
        try:
            model_name = os.environ.get(
                Constants.MODEL, "meta-llama/Meta-Llama-3.1-8B-Instruct"
            )
            if not model_name:
                raise ValueError
        except ValueError:
            print(f"Invalid model name in {Constants.MODEL}")

        self.model = os.environ[Constants.MODEL]

        # Store the VLLM configuration
        self.vllm_config = vllm_config

        # Initialize the tokenizer and model using the Hugging Face `transformers` library
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.llm = LLM(model=self.model, **self.vllm_config)

        print("Initialization complete.")

    def requests(
        self, data: List[Dict[str, Any]], sampling_config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Processes a batch of requests (prompts) and returns the generated responses.

        Args:
            data: A list of dictionaries, each containing input prompts.
            sampling_config: Optional configuration for controlling sampling behavior (e.g., max tokens, temperature).

        Returns:
            A list of dictionaries containing the input prompts and their corresponding generated outputs.
        """
        # Convert input messages to token IDs for the model using a chat template
        prompt_token_ids = [
            self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)
            for messages in data
        ]

        # Set sampling parameters (e.g., max tokens, temperature, top-p)
        sampling_params = (
            SamplingParams(**sampling_config)
            if sampling_config
            else SamplingParams(max_tokens=250, temperature=0.6, top_p=0.9)
        )

        # Generate outputs using the VLLM model
        outputs = self.llm.generate(
            prompt_token_ids=prompt_token_ids, sampling_params=sampling_params
        )

        processed_outputs = []
        # Loop through each output and decode the token IDs into human-readable text
        for output in outputs:
            input_prompt = self.tokenizer.decode(
                output.prompt_token_ids
            )  # Decode the input prompt
            generated_text = output.outputs[
                0
            ].text  # Extract the first generated output
            # Store the input prompt, output, and configurations in the result
            processed_outputs.append(
                {
                    Constants.INPUT_PROMPT: input_prompt,
                    Constants.OUTPUT: generated_text,
                    Constants.VLLM_ENGINE_CONFIG: self.vllm_config,
                    Constants.SAMPLING_CONFIG: sampling_config,
                }
            )

        # Save the generated output to a JSON file
        os.makedirs(
            Constants.OUTPUT_FOLDER_PATH, exist_ok=True
        )  # Ensure the output folder exists
        with open(Constants.OUTPUT_FILE_PATH, "w") as f:
            json.dump(processed_outputs, f)  # Write the output data to a JSON file

        return processed_outputs  # Return the list of processed outputs


def main():
    """
    Main function to run the batch inference pipeline.
    Reads input data from a file, initializes the deployment, runs the inference, and uploads results.
    """
    # Load input data from the specified JSON file
    with open("job-artifacts/input.json") as f:
        input_data = json.load(f)

    # Initialize the deployment with the VLLM engine configuration from input data
    deployment = Deployment(input_data[Constants.VLLM_ENGINE_CONFIG])

    # Run the batch inference and generate responses based on the input prompts
    response = deployment.requests(
        input_data["data"], input_data.get(Constants.SAMPLING_CONFIG)
    )

    # Upload the result to Object Storage in Oracle Cloud
    prefix = os.environ.get("PREFIX", Constants.OS_OBJECT)
    os_path = ObjectStorageDetails(
        os.environ["BUCKET"], os.environ["NAMESPACE"], prefix
    ).path

    # Upload the folder containing the output data to Object Storage
    model_artifact_path = upload_folder(
        os_path=os_path, local_dir=Constants.OUTPUT_FOLDER_PATH, model_name="outputs"
    )

    # Print the path to the uploaded model artifact
    print(model_artifact_path)


if __name__ == "__main__":
    main()

```

## Define and Run the inferencing Job

### Setup Job Infrastructure



```python
infrastructure = (
    DataScienceJob()
    # Configure logging for getting the job run outputs.
    .with_log_group_id(log_group_id)
    # Log resource will be auto-generated if log ID is not specified.
    .with_log_id(log_id)
    .with_job_infrastructure_type("ME_STANDALONE")
    # If you are in an OCI data science notebook session,
    # the following configurations are not required.
    # Configurations from the notebook session will be used as defaults.
    .with_compartment_id(compartment_id)
    .with_project_id(project_id)
    .with_shape_name(instance_shape)
    # Minimum/Default block storage size is 50 (GB).
    .with_block_storage_size(80)
)
```

### Configure Job Conatiner Runtime



```python
conatiner_runtime = (
    ContainerRuntime()
    # Specify the service conda environment by slug name.
    .with_image(container_image)
    # Environment variable
    .with_environment_variable(
        HF_TOKEN=hf_token,
        MODEL=model_name,
        BUCKET=bucket,
        NAMESPACE=namespace,
        OCI_IAM_TYPE=oci_iam_type,
        PREFIX=prefix,
    )
    # Command line argument
    .with_entrypoint(["bash", "-c"])
    .with_cmd(
        "microdnf install -y unzip &&"
        + "pip install oracle-ads[opctl] &&"
        + "cd /home/datascience/ &&"
        + "ls -lt &&"
        + "unzip job-artifacts.zip -d . && "
        + "chmod +x job-artifacts/vllm_batch_inferencing.py &&"
        + "python job-artifacts/vllm_batch_inferencing.py"
    )
    .with_artifact(artifacts_path)
)
```

### Run a Job and Monitor outputs


```python
job = (
    Job(name=f"Batch-inferencing of {model_name} using AI Quick Action.")
    .with_infrastructure(infrastructure)
    .with_runtime(conatiner_runtime)
)
# Create the job on OCI Data Science
job.create()
# Start a job run
run = job.run()

# Stream the job run outputs
run.watch()
```

## Download the output file from OS


```python
!oci os object bulk-download  --bucket-name $bucket --namespace $namespace --prefix prefix --dest-dir . --auth resource_principal
```

### Display downloaded output file


```python
output_file = os.path.join(os.path.abspath(prefix), "outputs", "output_prompts.json")

!python -m json.tool $output_file
```

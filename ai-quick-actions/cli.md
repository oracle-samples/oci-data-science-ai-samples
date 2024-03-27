# AI Quick Actions CLI

This document provides documentation on how to use ADS to create AI Quick Actions (Aqua) model deployments, fine-tune foundational models and evaluate the models.
You'll need the latest version of ADS to run these, installation instructions are available [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/quickstart.html).

# Table of Contents
- [Models](#models)
  - [List Models](#list-models)
  - [Get Model Details](#get-model-details)
- [Model Deployment](#model-deployment)
  - [Create Deployment](#create-model-deployment)
  - [List Model Deployments](#list-model-deployments)
  - [Get Model Deployment Details](#get-model-deployment-details)
- [Model Evaluation](#model-evaluation)
  - [Create Model Evaluation](#create-model-evaluation)
  - [List Model Evaluation](#list-model-evaluations)
  - [Get Model Evaluation Details](#get-model-evaluation-details)
- [Model Fine-Tuning](#model-fine-tuning)
  - [Create Fine-Tuned Model](#create-fine-tuned-model)


# Models

## List Models

### Description

Lists all Aqua models within a specified compartment and/or project.  If `compartment_id` is not specified, 
the method defaults to returning the service models within the pre-configured default compartment.

### Usage

```bash
ads aqua model list [OPTIONS]
```

### Optional Parameters

`--compartment_id [str]`

The ID of the compartment in which the aqua models are available. If not provided, then it defaults to the service compartment identified by the environment variable `ODSC_MODEL_COMPARTMENT_OCID`.

`--project_id [str]`

The ID of the project in which the aqua models are available. If not provided, then it defaults to the user's project.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI list_models API. For more details on acceptable parameters, see [ListModels API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelSummary/ListModels).

### Example

```bash
ads aqua model list --compartment_id ocid1.compartment.oc1..<ocid>
```

<details>
  <summary>CLI Output</summary>

```console
{
    "compartment_id": "ocid1.compartment.oc1..<ocid>",
    "icon": "",
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "is_fine_tuned_model": false,
    "license": "llama2",
    "name": "CodeLlama-34b-Instruct-hf",
    "organization": "Meta",
    "project_id": "",
    "tags": {
        "license": "llama2",
        "task": "code_synthesis",
        "OCI_AQUA": "",
        "organization": "Meta"
    },
    "task": "code_synthesis",
    "time_created": "2024-03-13T12:34:16.959000+00:00",
    "console_link": [
        "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
    ],
    "search_text": "llama2,code_synthesis,,Meta",
    "ready_to_deploy": true
}
...
...
...
  ```
</details>



## Get Model Details

### Description

Gets the information of an Aqua model.

### Usage

```bash
ads aqua model get [OPTIONS]
```

### Required Parameters

`--model_id [str]`

The OCID of the Aqua model.


### Example

```bash
ads aqua model get --model_id ocid1.datasciencemodel.oc1.iad.<ocid>
```

<details>
  <summary>CLI Output</summary>

```console
{
  "compartment_id": "ocid1.compartment.oc1..<ocid>",
  "icon": "",
  "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
  "is_fine_tuned_model": false,
  "license": "Apache 2.0",
  "name": "Mistral-7B-Instruct-v0.1",
  "organization": "Mistral AI",
  "project_id": "ocid1.datascienceproject.oc1.iad.<ocid>",
  "tags": {
    "license": "Apache 2.0",
    "task": "text_generation",
    "OCI_AQUA": "",
    "organization": "Mistral AI"
  },
  "task": "text_generation",
  "time_created": "2024-02-27T14:08:15.564000+00:00",
  "console_link": [
    "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
  ],
  "search_text": "The Mistral-7B-Instruct-v0.1 Large Language Model (LLM) is a instruct fine-tuned version of the Mistral-7B-v0.1 generative text model using a variety of publicly available conversation datasets. Apache 2.0,text_generation,,Mistral AI",
  "ready_to_deploy": true,
  "model_card": "---\nlicense: apache-2.0\npipeline_tag: text-generation\ntags:\n- finetuned\ninference:\n  parameters:\n    temperature: 0.7\n---\n\n# Model Card for Mistral-7B-Instruct-v0.1\n\nThe Mistral-7B-Instruct-v0.1 Large Language Model (LLM) is a instruct fine-tuned version of the [Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) generative text model using a variety of publicly available conversation datasets.\n\nFor full details of this model please read our [release blog post](https://mistral.ai/news/announcing-mistral-7b/)\n\n## Instruction format\n\nIn order to leverage instruction fine-tuning, your prompt should be surrounded by `[INST]` and `[\\INST]` tokens. The very first instruction should begin with a begin of sentence id. The next instructions should not. The assistant generation will be ended by the end-of-sentence token id.\n\nE.g.\n```\ntext = \"<s>[INST] What is your favourite condiment? [/INST]\"\n\"Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!</s> \"\n\"[INST] Do you have mayonnaise recipes? [/INST]\"\n```\n\nThis format is available as a [chat template](https://huggingface.co/docs/transformers/main/chat_templating) via the `apply_chat_template()` method:\n\n```python\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\ndevice = \"cuda\" # the device to load the model onto\n\nmodel = AutoModelForCausalLM.from_pretrained(\"mistralai/Mistral-7B-Instruct-v0.1\")\ntokenizer = AutoTokenizer.from_pretrained(\"mistralai/Mistral-7B-Instruct-v0.1\")\n\nmessages = [\n    {\"role\": \"user\", \"content\": \"What is your favourite condiment?\"},\n    {\"role\": \"assistant\", \"content\": \"Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!\"},\n    {\"role\": \"user\", \"content\": \"Do you have mayonnaise recipes?\"}\n]\n\nencodeds = tokenizer.apply_chat_template(messages, return_tensors=\"pt\")\n\nmodel_inputs = encodeds.to(device)\nmodel.to(device)\n\ngenerated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)\ndecoded = tokenizer.batch_decode(generated_ids)\nprint(decoded[0])\n```\n\n## Model Architecture\nThis instruction model is based on Mistral-7B-v0.1, a transformer model with the following architecture choices:\n- Grouped-Query Attention\n- Sliding-Window Attention\n- Byte-fallback BPE tokenizer\n\n## Troubleshooting\n- If you see the following error:\n```\nTraceback (most recent call last):\nFile \"\", line 1, in\nFile \"/transformers/models/auto/auto_factory.py\", line 482, in from_pretrained\nconfig, kwargs = AutoConfig.from_pretrained(\nFile \"/transformers/models/auto/configuration_auto.py\", line 1022, in from_pretrained\nconfig_class = CONFIG_MAPPING[config_dict[\"model_type\"]]\nFile \"/transformers/models/auto/configuration_auto.py\", line 723, in getitem\nraise KeyError(key)\nKeyError: 'mistral'\n```\n\nInstalling transformers from source should solve the issue\npip install git+https://github.com/huggingface/transformers\n\nThis should not be required after transformers-v4.33.4.\n\n## Limitations\n\nThe Mistral 7B Instruct model is a quick demonstration that the base model can be easily fine-tuned to achieve compelling performance. \nIt does not have any moderation mechanisms. We're looking forward to engaging with the community on ways to\nmake the model finely respect guardrails, allowing for deployment in environments requiring moderated outputs.\n\n## The Mistral AI Team\n\nAlbert Jiang, Alexandre Sablayrolles, Arthur Mensch, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Florian Bressand, Gianna Lengyel, Guillaume Lample, Lélio Renard Lavaud, Lucile Saulnier, Marie-Anne Lachaux, Pierre Stock, Teven Le Scao, Thibaut Lavril, Thomas Wang, Timothée Lacroix, William El Sayed."
}
  ```
</details>


# Model Deployment

## Create Model Deployment

### Description

Creates a new Aqua model deployment.

### Usage

```bash
ads aqua deployment create [OPTIONS]
```

### Required Parameters

`--model_id [str]`

The model OCID to deploy.

`--instance_shape [str]`

The shape of the instance used for model deployment.

`--display_name [str]`

The name of model deployment.


### Optional Parameters

`--compartment_id [str]`

The compartment OCID where model deployment is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where model deployment is to be created. If not provided, then it defaults to user's project.

`--description [str]`

The description of the model deployment. Defaults to None.

`--instance_count [int]`

The number of instance used for model deployment. Defaults to 1.

`--log_group_id [str]`

The oci logging group id. The access log and predict log share the same log group.

`--access_log_id [str]`

The access log OCID for the access logs. Check [model deployment logging](https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_using_logging.htm) for more details.

`--predict_log_id [str]`

The predict log OCID for the predict logs. Check [model deployment logging](https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_using_logging.htm) for more details.

`--web_concurrency [int]`

The number of worker processes/threads to handle incoming requests.

`--server_port [int]`

The server port for docker container image. Defaults to 8080.

`--health_check_port [int]`

The health check port for docker container image. Defaults to 8080.

`--env_var [dict]`

Environment variable for the model deployment, defaults to None.


### Example

```bash
ads aqua deployment create --model_id "ocid1.datasciencemodel.oc1.iad.<ocid>" --instance_shape "VM.GPU.A10.1" --display_name "falcon7b MD with Aqua CLI"
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "falcon7b MD with Aqua CLI",
    "aqua_service_model": true,
    "state": "CREATING",
    "description": null,
    "created_on": "2024-02-03 21:21:31.952000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": 1.0,
        "memory_in_gbs": 16.0
    },
    "tags": {
        "aqua_service_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#falcon-7b",
        "OCI_AQUA": ""
    }
}
  ```
</details>



## List Model Deployments

### Description

Lists all Aqua model deployments within a specified compartment and/or project.

### Usage

```bash
ads aqua deployment list [OPTIONS]
```

### Optional Parameters

`--compartment_id [text]`

The ID of the compartment in which the aqua model deployments are available. If not provided, then it defaults to the user's compartment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI list_model_deployments API. For more details on acceptable parameters, see [List Model Deployments API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeploymentSummary/ListModelDeployments).


### Example

```bash
ads aqua deployment list
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
    "display_name": "Mistral-7B-v0.1 MD",
    "aqua_service_model": false,
    "state": "INACTIVE",
    "description": null,
    "created_on": "2024-03-16 21:57:21.143000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment-int.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_details": "",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.2",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "OCI_AQUA": ""
    }
}
...
...
  ```
</details>



## Get Model Deployment Details

### Description

Gets the information of an Aqua model deployment.

### Usage

```bash
ads aqua deployment get [OPTIONS]
```

### Required Parameters

`--model_deployment_id [str]`

The OCID of the Aqua model deployment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI get_model_deployment API. For more details on acceptable parameters, see [Get Model Deployment API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeployment/GetModelDeployment).

### Example

```bash
ads aqua deployment get --model_deployment_id "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>"
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
    "display_name": "MD for falcon7b Model",
    "aqua_service_model": false,
    "state": "DELETED",
    "description": null,
    "created_on": "2024-02-22 05:00:29.520000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment-int.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_details": "Model Deployment with all associated resources has been deleted",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "OCI_AQUA": ""
    },
    "log_group": {
        "id": "ocid1.loggroup.oc1.iad.<ocid>",
        "name": "log_name",
        "url": "https://cloud.oracle.com/logging/log-groups/ocid1.loggroup.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "log": {
        "id": "ocid1.log.oc1.iad.<ocid>",
        "name": "llm-deployments",
        "url": "https://cloud.oracle.com/logging/search?searchQuery=search \"ocid1.compartment.oc1..<ocid>/ocid1.loggroup.oc1.iad.<ocid>/ocid1.log.oc1.iad.<ocid>\" | source='ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>' | sort by datetime desc®ions=us-ashburn-1"
    }
}  
```
</details>



# Model Evaluation

## Create Model Evaluation

### Description

Creates a new evaluation model using an existing Aqua model or model deployment. Currently, evaluation is only supported via model deployment as the source.

### Usage

```bash
ads aqua evaluation create [OPTIONS]
```

### Required Parameters

`--evaluation_source_id [str]`

The evaluation source id. Must be either model or model deployment ocid.

`--evaluation_name [str]`

The name for evaluation.

`--dataset_path [str]`

The dataset path for the evaluation. Could be either a local path from notebook session or an object storage path.

`--report_path [str]`

The report path for the evaluation. Must be an object storage path.

`--model_parameters [str]`

The parameters for the evaluation.

`--shape_name [str]`

The shape name for the evaluation job infrastructure.

`--block_storage_size [int]`

The storage for the evaluation job infrastructure.

`--metrics [list]`

The metrics for the evaluation.


### Optional Parameters

`--compartment_id [str]`

The compartment OCID where evaluation is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where evaluation is to be created. If not provided, then it defaults to user's project.

`--evaluation_description [str]`

The description of the evaluation. Defaults to None.

`--memory_in_gbs [float]`

The memory in gbs for the shape selected.

`--ocpus [float]`

The ocpu count for the shape selected.

`--experiment_id [str]`

The evaluation model version set id. If provided, evaluation model will be associated with it. Defaults to None.

`--experiment_name [str]`

The evaluation model version set name. If provided, the model version set with the same name will be used if exists, otherwise a new model version set will be created with the name.

`--experiment_description [str]`

The description for the evaluation model version set.

`--log_group_id [str]`

The log group id for the evaluation job infrastructure. Defaults to None.

`--log_id [str]`

The log id for the evaluation job infrastructure. Defaults to None.


### Example

```bash
ads aqua evaluation create  --evaluation_source_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>" --evaluation_name "test_evaluation" --dataset_path "oci://test_bucket@namespace/score.jsonl" --report_path "oci://test_bucket@namespace/" --model_parameters '{"max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}' --shape_name "VM.Standard.E4.Flex" --block_storage_size 50 --metrics '[{"name": "bertscore", "args": {}}]'
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "test_evaluation",
    "aqua_service_model": true,
    "state": "CREATING",
    "description": null,
    "created_on": "2024-02-03 21:21:31.952000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "shape_info": {
        "instance_shape": "VM.Standard.E4.Flex",
        "instance_count": 1,
        "ocpus": 1.0,
        "memory_in_gbs": 16.0
    },
    "tags": {
        "aqua_service_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Llama-2-13b",
        "OCI_AQUA": ""
    }
}  
```
</details>



## List Model Evaluations

### Description

Lists all Aqua model evaluations within a specified compartment and/or project.

### Usage

```bash
ads aqua evaluation list [OPTIONS]
```

### Required Parameters

`--compartment_id [text]`

The ID of the compartment in which the aqua model evaluations are available.


### Example

```bash
ads aqua evaluation list --compartment_id ocid1.compartment.oc1..<ocid>
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "test-eval",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "FAILED",
    "lifecycle_details": "",
    "time_created": "2024-03-18T00:31:28.026000+00:00",
    "tags": {
        "aqua_evaluation": "aqua_evaluation"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "experiment_name",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.ocid",
        "name": "mistral-classifier",
        "url": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejobrunint.oc1.iad.<ocid>",
        "name": "test-eval",
        "url": "https://cloud.oracle.com/data-science/job-runs/ocid1.datasciencejobrunint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 50,
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stop": [],
        "shape": "VM.Standard.E3.Flex",
        "dataset_path": "oci://aqua-eval-test-bucket@namespace/dataset/evaluation-sample-with-sys-message.jsonl",
        "report_path": "oci://aqua-eval-test-bucket@namespace/report/"
    }
}
...
...
```
</details>



## Get Model Evaluation Details

### Description

Gets the information of an Aqua model evaluation.

### Usage

```bash
ads aqua evaluation get [OPTIONS]
```

### Required Parameters

`--eval_id [str]`

The OCID of the Aqua model evaluation.


### Example

```bash
ads aqua evaluation get --eval_id "ocid1.datasciencemodel.oc1.iad.<ocid>"
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "test-eval",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "FAILED",
    "lifecycle_details": "An error occurred during the evaluation, please check the log for more information. Exit code: 1.",
    "time_created": "2024-03-18T00:06:07.994000+00:00",
    "tags": {
        "aqua_evaluation": "aqua_evaluation"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "experiment_name",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
        "name": "mistral-classifier",
        "url": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejobrunint.oc1.iad.<ocid>",
        "name": "test-eval",
        "url": "https://cloud.oracle.com/data-science/job-runs/ocid1.datasciencejobrunint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 50,
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stop": [],
        "shape": "VM.Standard.E3.Flex",
        "dataset_path": "oci://aqua-eval-test-bucket@namespace/dataset/evaluation-sample-with-sys-message.jsonl",
        "report_path": "oci://aqua-eval-test-bucket@namespace/report/"
    },
    "log_group": {
        "id": "",
        "name": null,
        "url": ""
    },
    "log": {
        "id": "",
        "name": null,
        "url": ""
    },
    "introspection": {
        "aqua_evaluate": {
            "output_report_path": {
                "key": "output_report_path",
                "category": "aqua_evaluate",
                "description": "Verify output report path.",
                "error_msg": "The destination folder does not exist or cannot be accessed for writing. Please verify that the folder exists and has the appropriate write permissions.",
                "success": false
            }
        }
    }
}
```
</details>



# Model Fine-Tuning

## Create Fine-Tuned Model

### Description

Creates a new fine-tuned model using an existing Aqua model with a user provided dataset.

### Usage

```bash
ads aqua fine_tuning create [OPTIONS]
```

### Required Parameters

`--ft_source_id [str]`

The fine-tuning source id. Must be foundational model ocid.

`--ft_name [str]`

The name for fine-tuned model.

`--dataset_path [str]`

The dataset path for the model fine-tuning. Could be either a local path from notebook session or an object storage path.

`--report_path [str]`

The report path of the fine-tuned model. Must be an object storage path.

`--ft_parameters [dict]`

The parameters for model fine-tuning.

`--shape_name [str]`

The shape name for the model fine-tuning job infrastructure.

`--replica [int]`

The replica for the model fine-tuning job runtime.

`--validation_set_size [float]`

The validation set size for fine-tuning job. Must be a float in between [0,1).


### Optional Parameters

`--compartment_id [str]`

The compartment OCID where evaluation is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where evaluation is to be created. If not provided, then it defaults to user's project.

`--ft_description [str]`

The description of the fine-tuned model. Defaults to None.

`--experiment_id [str]`

The fine-tuned model version set id. If provided, evaluation model will be associated with it. Defaults to None.

`--experiment_name [str]`

The fine-tuned model version set name. If provided, the model version set with the same name will be used if exists, otherwise a new model version set will be created with the name.

`--experiment_description [str]`

The description for the fine-tuned model version set.

`--block_storage_size [int]`

The storage for the model fine-tuning job infrastructure.

`--subnet_id [str]`

The custom egress for model fine-tuning job. Defaults to None.

`--log_group_id [str]`

The log group id for the evaluation job infrastructure. Defaults to None.

`--log_id [str]`

The log id for the evaluation job infrastructure. Defaults to None.


### Example

```bash
ads aqua fine_tuning create --ft_source_id "ocid1.datasciencemodel.oc1.iad.<ocid>" --ft_name "Mistral-7B-Instruct-v0.1 FT" --dataset_path "oci://test_bucket@namespace/datasets/samsum_500.jsonl" --report_path "oci://test_bucket@namespace/aqua_ft" --ft_parameters '{"epochs": 10, "learning_rate": 0.0002}' --shape_name "VM.GPU.A10.2" --replica 2 --validation_set_size 0.5 --subnet_id "ocid1.subnet.oc1.iad.<ocid>" --log_group_id "ocid1.loggroup.oc1.iad.<ocid>" --log_id "ocid1.log.oc1.iad.<ocid>" --experiment_id "ocid1.datasciencemodelversionset.oc1.iad.<ocid>"
```

<details>
  <summary>CLI Output</summary>

```console
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "Test Mistral-7B-Instruct-v0.1 FT",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "ACCEPTED",
    "lifecycle_details": "",
    "time_created": "2024-03-18 22:59:02.748000+00:00",
    "tags": {
        "aqua_finetuning": "aqua_finetuning",
        "finetuning_job_id": "ocid1.datasciencejob.oc1.iad.<ocid>",
        "finetuning_source": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "finetuning_experiment_id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "test_version_set",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "name": "Mistral-7B-v0.1",
        "url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejob.oc1.iad.<ocid>",
        "name": "Test Mistral-7B-Instruct-v0.1 FT",
        "url": "https://cloud.oracle.com/data-science/jobs/ocid1.datasciencejob.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "epochs": 10,
        "learning_rate": 0.0002
    }
}
```
</details>

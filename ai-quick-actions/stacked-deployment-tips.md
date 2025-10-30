# **AI Quick Actions Stacked Deployment (Available through CLI only)**

# Table of Contents
- # Introduction to Stacked Deployment and Serving
- [Models](#models)
- [Stacked Deployment](#stacked-deployment)
  - [Create Stacked Deployment](#create-stacked-deployment)
  - [Manage Stacked Deployments](#manage-stacked-deployments)
    - [List Stacked Deployments](#list-stacked-deployments)
    - [Edit Stacked Deployments](#edit-stacked-deployments)
- [Stacked Model Inferencing](#stacked-model-inferencing)
- [Stacked Model Evaluation](#stacked-model-evaluation)
  - [Create Model Evaluations](#create-model-evaluations)

# Introduction to Stacked Deployment and Serving

Stacked Model Deployment enables deploying a base model alongside multiple fine-tuned weights within the same deployment. During inference, responses can be generated using either the base model or the associated fine-tuned weights, depending on the request. The Data Science server has prebuilt **vLLM service container** that make deploying and serving stacked large language model very easy, simplifying the deployment process and reducing operational complexity. This container comes with **VLLM's native routing** which routes requests to the appropriate model, ensuring seamless prediction.

**Stacked Deployment is currently in beta and is only available through the CLI.**

This document provides documentation on how to use ADS CLI to create stacked deployment using AI Quick Actions (AQUA) model deployments, and evaluate the models. you'll need the latest version of ADS to run these, installation instructions are available [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/quickstart.html).

# Models

First step in process is to get the OCIDs of the desired base service LLM AQUA models, which are required to initiate the stacked deployment process. Refer to [AQUA CLI tips](cli-tips.md) for detailed instructions on how to obtain the OCIDs of base service LLM AQUA models.

You can also obtain the OCID from the AQUA user interface by clicking on the model card and selecting the `Copy OCID` button from the `More Options` dropdown in the top-right corner of the screen.

# Stacked Deployment

## Create Stacked Deployment

### Description

Creates a new Aqua Stacked deployment.

### Usage

```bash
ads aqua deployment create [OPTIONS]
```

### Required Parameters

`--models [str]`

The String representation of a JSON array, where each object defines a model OCID, model name and its associating fine tuned weights. The model names are used to reference specific models during inference requests and support a [maximum length of 32 characters](https://docs.oracle.com/en-us/iaas/Content/data-science/using/models-mms-top.htm#models-mms-key-concepts). Model OCID will be used for inferencing if no model name is provided. Only **one** base model is allowed for creating stacked deployment <br>
Example: `'[{"model_id":"<model_ocid>", "model_name":"<model_name>", "fine_tune_weights": [{"model_id": "<ft_ocid>", "model_name":"<ft_name>"},{"model_id":"<ft_ocid>", "model_name": "<ft_name>"}]}]'` for  `VM.GPU.A10.2` shape. <br>


`--instance_shape [str]`

The shape (GPU) of the instance used for model deployment. <br>
Example: `VM.GPU.A10.2, BM.GPU.A10.4, BM.GPU4.8, BM.GPU.A100-v2.8`.

`--display_name [str]`

The name of model deployment.

`--container_image_uri [str]`

The URI of the inference container associated with the model being registered. In case of Stacked, the value is vLLM container URI. <br>
Example: `dsmc://odsc-vllm-serving:0.6.4.post1.2` or `dsmc://odsc-vllm-serving:0.8.1.2`

`--deployment_type [str]`

The deployment type for creating model deployment. In case of Stacked, the value must be `STACKED`. Failing to provide `--deployment_type` will result in creating multi model deployment instead.

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

`--private_endpoint_id [str]`

The private endpoint id of model deployment.

### Example

#### Create Stacked deployment with `/v1/completions`

```bash
ads aqua deployment create \
  --container_image_uri "dsmc://odsc-vllm-serving:0.6.4.post1.2" \
  --models '[{"model_id":"ocid1.datasciencemodel.oc1.iad.<ocid>", "model_name":"test_model_name"}]' \
  --instance_shape "VM.GPU.A10.1" \
  --display_name "modelDeployment_stacked_model"
  --deployment_type "STACKED"

```

##### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "modelDeployment_stacked_model",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodelgroup.oc1.iad.<ocid>",
    "models": [],
    "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "state": "CREATING",
    "description": null,
    "created_on": "2025-10-13 17:48:53.416000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": null,
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "task": "text_generation",
        "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "BASE_MODEL": "service_models/Meta-Llama-3.1-8B-Instruct/5206a32/artifact",
        "VLLM_ALLOW_RUNTIME_LORA_UPDATING": "true",
        "MODEL": "/opt/ds/model/deployed_model/ocid1.datasciencemodel.oc1.iad.<ocid>/",
        "PARAMS": "--served-model-name test_model_name --disable-custom-all-reduce --seed 42 --max-model-len 4096 --max-lora-rank 32 --enable_lora",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080",
        "AQUA_TELEMETRY_BUCKET_NS": "ociodscdev",
        "AQUA_TELEMETRY_BUCKET": "service-managed-models"
    },
    "cmd": []
}
```

#### Create Stacked deployment with `/v1/chat/completions`

```bash
ads aqua deployment create \
  --container_image_uri "dsmc://odsc-vllm-serving:0.6.4.post1.2" \
  --models '[{"model_id":"ocid1.datasciencemodel.oc1.iad.<ocid>", "model_name":"test_model_name"}]' \
  --env-var '{"MODEL_DEPLOY_PREDICT_ENDPOINT":"/v1/chat/completions"}' \
  --instance_shape "VM.GPU.A10.1" \
  --display_name "modelDeployment_stacked_model"
  --deployment_type "STACKED"

```

##### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "modelDeployment_stacked_model",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodelgroup.oc1.iad.<ocid>",
    "models": [],
    "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "state": "CREATING",
    "description": null,
    "created_on": "2025-10-13 17:48:53.416000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": null,
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "task": "text_generation",
        "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "BASE_MODEL": "service_models/Meta-Llama-3.1-8B-Instruct/5206a32/artifact",
        "VLLM_ALLOW_RUNTIME_LORA_UPDATING": "true",
        "MODEL": "/opt/ds/model/deployed_model/ocid1.datasciencemodel.oc1.iad.<ocid>/",
        "PARAMS": "--served-model-name test_model_name --disable-custom-all-reduce --seed 42 --max-model-len 4096 --max-lora-rank 32 --enable_lora",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080",
        "AQUA_TELEMETRY_BUCKET_NS": "ociodscdev",
        "AQUA_TELEMETRY_BUCKET": "service-managed-models"
    },
    "cmd": []
}
```

## Manage Stacked Deployments

### List Stacked Deployments

To list all AQUA deployments (all Stacked, MultiModel and single-model) within a specified compartment or project, or to get detailed information on a specific Stacked deployment, kindly refer to the [AQUA CLI tips](cli-tips.md) documentation.

Note: Stacked deployments are identified by the tag `"aqua_stacked_model": "true",` associated with them.

### Edit Stacked Deployments

#### Usage

```bash
ads aqua deployment update [OPTIONS]
```

#### Required Parameters

`--model_deployment_id [str]`

The model deployment OCID to be updated.

#### Optional Parameters

`--models [str]`

The String representation of a JSON array, where each object defines a model OCID, model name and its associating fine tuned weights. The model names are used to reference specific models during inference requests and support a [maximum length of 32 characters](https://docs.oracle.com/en-us/iaas/Content/data-science/using/models-mms-top.htm#models-mms-key-concepts). Only **one** base model is allowed for updating stacked deployment <br>
Example: `'[{"model_id":"<model_ocid>", "model_name":"<model_name>", "fine_tune_weights": [{"model_id": "<ft_ocid>", "model_name":"<ft_name>"},{"model_id":"<ft_ocid>", "model_name": "<ft_name>"}]}]'` for  `VM.GPU.A10.2` shape. <br>

`--display_name [str]`

The name of model deployment.

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

`--bandwidth_mbps [int]`

The bandwidth limit on the load balancer in Mbps.

`--memory_in_gbs [float]`

Memory (in GB) for the selected shape.

`--ocpus [float]`

OCPU count for the selected shape.

`--freeform_tags [dict]`

Freeform tags for model deployment.

`--defined_tags [dict]`
Defined tags for model deployment.

#### Example

##### Edit Stacked deployment with `/v1/completions`

```bash
ads aqua deployment update \
  --model_deployment_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>" \
  --models '[{"model_id":"ocid1.datasciencemodel.oc1.iad.<ocid>", "model_name":"test_updated_model_name"}]' \
  --display_name "updated_modelDeployment_stacked_model"

```

##### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "updated_modelDeployment_stacked_model",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodelgroup.oc1.iad.<ocid>",
    "models": [],
    "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "state": "UPDATING",
    "description": null,
    "created_on": "2025-10-13 17:48:53.416000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": null,
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "task": "text_generation",
        "aqua_model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "BASE_MODEL": "service_models/Meta-Llama-3.1-8B-Instruct/5206a32/artifact",
        "VLLM_ALLOW_RUNTIME_LORA_UPDATING": "true",
        "MODEL": "/opt/ds/model/deployed_model/ocid1.datasciencemodel.oc1.iad.<ocid>/",
        "PARAMS": "--served-model-name test_updated_model_name --disable-custom-all-reduce --seed 42 --max-model-len 4096 --max-lora-rank 32 --enable_lora",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080",
        "AQUA_TELEMETRY_BUCKET_NS": "ociodscdev",
        "AQUA_TELEMETRY_BUCKET": "service-managed-models"
    },
    "cmd": []
}
```

# Stacked Model Inferencing

The only change required to infer a specific model from a Stacked deployment is to update the value of `"model"` parameter in the request payload. The values for this parameter can be found in the Model Deployment details, under the field name `"model_name"`. This parameter segregates the request flow, ensuring that the inference request is directed to the correct model within the Stacked deployment.

## Using oci-cli

```bash
oci raw-request \
  --http-method POST \
  --target-uri <model_deployment_url>/predict \
  --request-body '{
    "model": "<model_name>",
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8
  }' \
  --auth <auth_method>

```

Note: Currently `oci-cli` does not support streaming response, use Python or Java SDK instead.

## Using Python SDK (without streaming)

```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

model = "<model_name>"

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": model, # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}

res = requests.post(endpoint, json=body, auth=auth, headers={}).json()

print(res)
```

## Using Python SDK (with streaming)

To consume streaming Server-sent Events (SSE), install [sseclient-py](https://pypi.org/project/sseclient-py/) using `pip install sseclient-py`.

```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file
import sseclient # pip install sseclient-py

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

model = "<model_name>"

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": model, # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
    "stream": True,
}

headers={'Content-Type':'application/json','enable-streaming':'true', 'Accept': 'text/event-stream'}
response = requests.post(endpoint, json=body, auth=auth, stream=True, headers=headers)

print(response.headers)

client = sseclient.SSEClient(response)
for event in client.events():
    print(event.data)

# Alternatively, we can use the below code to print the response.
# for line in response.iter_lines():
#    if line:
#        print(line)
```

## Using Python SDK for /v1/chat/completions endpoint

To access the model deployed with `/v1/chat/completions` endpoint for inference, update the body and replace `prompt` field
with `messages`.

```python
...
body = {
    "model": "<model_name>", # this is a constant
    "messages":[{"role":"user","content":[{"type":"text","text":"Who wrote the book Harry Potter?"}]}],
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
...
```

## Using Java (with streaming)

```java
/**
 * The OCI SDK must be installed for this example to function properly.
 * Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm
 */
package org.example;

import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.SessionTokenAuthenticationDetailsProvider;
import com.oracle.bmc.http.ClientConfigurator;
import com.oracle.bmc.http.Priorities;
import com.oracle.bmc.http.client.HttpClient;
import com.oracle.bmc.http.client.HttpClientBuilder;
import com.oracle.bmc.http.client.HttpRequest;
import com.oracle.bmc.http.client.HttpResponse;
import com.oracle.bmc.http.client.Method;
import com.oracle.bmc.http.client.jersey.JerseyHttpProvider;
import com.oracle.bmc.http.client.jersey.sse.SseSupport;
import com.oracle.bmc.http.internal.ParamEncoder;
import com.oracle.bmc.http.signing.RequestSigningFilter;

import javax.ws.rs.core.MediaType;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class RestExample {

    public static void main(String[] args) throws Exception {
        String configurationFilePath = "~/.oci/config";
        String profile = "DEFAULT";

        // Pre-Requirement: Allow setting of restricted headers. This is required to allow the SigningFilter
        // to set the host header that gets computed during signing of the request.
        System.setProperty("sun.net.http.allowRestrictedHeaders", "true");

        final AuthenticationDetailsProvider provider =
                new SessionTokenAuthenticationDetailsProvider(configurationFilePath, profile);

        // 1) Create a request signing filter instance using SessionTokenAuth Provider.
        RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromAuthProvider(
                provider);

      //  1) Alternatively, RequestSigningFilter can be created from a config file.
      //  RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromConfigFile(configurationFilePath, profile);

        // 2) Create a Jersey client and register the request signing filter.
        // Refer to this page https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkexamples.htm for information regarding the compatibility of the HTTP client(s) with OCI SDK version.

        HttpClientBuilder builder = JerseyHttpProvider.getInstance()
                .newBuilder()
                .registerRequestInterceptor(Priorities.AUTHENTICATION, requestSigningFilter)
                .baseUri(
                        URI.create(
                                "${modelDeployment.modelDeploymentUrl}/")
                                + ParamEncoder.encodePathParam("predict"));
        // 3) Create a request and set the expected type header.

        String jsonPayload = "{}";  // Add payload here with respect to your model example shown in next line:

        // 4) Setup Streaming request
        Function<InputStream, List<String>> generateTextResultReader = getInputStreamListFunction();
        SseSupport sseSupport = new SseSupport(generateTextResultReader);
        ClientConfigurator clientConfigurator = sseSupport.getClientConfigurator();
        clientConfigurator.customizeClient(builder);

        try (HttpClient client = builder.build()) {
            HttpRequest request = client
                    .createRequest(Method.POST)
                    .header("accepts", MediaType.APPLICATION_JSON)
                    .header("content-type", MediaType.APPLICATION_JSON)
                    .header("enable-streaming", "true")
                    .body(jsonPayload);

            // 5) Invoke the call and get the response.
            HttpResponse response = request.execute().toCompletableFuture().get();

            // 6) Print the response headers and body
            Map<String, List<String>> responseHeaders = response.headers();
            System.out.println("HTTP Headers " + responseHeaders);

            InputStream responseBody = response.streamBody().toCompletableFuture().get();
            try (
                    final BufferedReader reader = new BufferedReader(
                            new InputStreamReader(responseBody, StandardCharsets.UTF_8)
                    )
            ) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
    }

    private static Function<InputStream, List<String>> getInputStreamListFunction() {
        Function<InputStream, List<String>> generateTextResultReader = entityStream -> {
            try (BufferedReader reader =
                         new BufferedReader(new InputStreamReader(entityStream))) {
                String line;
                List<String> generatedTextList = new ArrayList<>();
                while ((line = reader.readLine()) != null) {
                    if (line.isEmpty() || line.startsWith(":")) {
                        continue;
                    }
                    generatedTextList.add(line);
                }
                return generatedTextList;
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }
        };
        return generateTextResultReader;
    }
}

```

# Stacked Model Evaluation

## Create Model Evaluations

### Description

Creates a new evaluation model using an existing Aqua Stacked deployment. For Stacked deployment, evaluations must be created separately for each model using the same model deployment OCID.

### Usage

```bash
ads aqua evaluation create [OPTIONS]
```

### Required Parameters

`--evaluation_source_id [str]`

The evaluation source id. Must be Stacked deployment OCID.

`--evaluation_name [str]`

The name for evaluation.

`--dataset_path [str]`

The dataset path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/path/to/the/dataset.jsonl`

`--report_path [str]`

The report path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/report/path/`

`--model_parameters [str]`

The parameters for the evaluation. The `"model"` is required evaluation param in case of Stacked deployment.

`--shape_name [str]`

The shape name for the evaluation job infrastructure. <br>
Example: `VM.Standard.E3.Flex, VM.Standard.E4.Flex, VM.Standard3.Flex, VM.Optimized3.Flex`.

`--block_storage_size [int]`

The storage for the evaluation job infrastructure.

### Optional Parameters

`--compartment_id [str]`

The compartment OCID where evaluation is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where evaluation is to be created. If not provided, then it defaults to user's project.

`--evaluation_description [str]`

The description of the evaluation. Defaults to None.

`--memory_in_gbs [float]`

The memory in gbs for the flexible shape selected.

`--ocpus [float]`

The ocpu count for the shape selected.

`--experiment_id [str]`

The evaluation model version set id. If provided, evaluation model will be associated with it. Defaults to None. <br>

`--experiment_name [str]`

The evaluation model version set name. If provided, the model version set with the same name will be used if exists, otherwise a new model version set will be created with the name.

`--experiment_description [str]`

The description for the evaluation model version set.

`--log_group_id [str]`

The log group id for the evaluation job infrastructure. Defaults to None.

`--log_id [str]`

The log id for the evaluation job infrastructure. Defaults to None.

`--metrics [list]`

The metrics for the evaluation, currently BERTScore and ROGUE are supported. <br>
Example: `'[{"name": "bertscore", "args": {}}, {"name": "rouge", "args": {}}]`

`--force_overwrite [bool]`

A flag to indicate whether to force overwrite the existing evaluation file in object storage if already present. Defaults to `False`.

### Example

```bash
ads aqua evaluation create \
    --evaluation_source_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>" \
    --evaluation_name "test_evaluation" \
    --dataset_path "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl" \
    --report_path "oci://<bucket>@<namespace>/report/path/" \
    --model_parameters '{"model":"<model_name>","max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}' \
    --shape_name "VM.Standard.E4.Flex" \
    --block_storage_size 50 \
    --metrics '[{"name": "bertscore", "args": {}}, {"name": "rouge", "args": {}}]'
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "name": "test_evaluation",
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
        "aqua_service_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Mistral-7B-v0.1",
        "OCI_AQUA": ""
    }
}
```

For other operations related to **Evaluation**, such as listing evaluations and retrieving evaluation details, please refer to [AQUA CLI tips](cli-tips.md)

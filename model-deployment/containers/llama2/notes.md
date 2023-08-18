docker run --gpus all --shm-size 1g -e HUGGING_FACE_HUB_TOKEN=$token -e -p 8080:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:0.9.3 --model-id $model

192.29.53.151

curl 192.29.53.151:5001/predict \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
    -H 'Content-Type: application/json'


curl 127.0.0.1:5001/predict \
    -X POST \
    -d '{"inputs":"what are some good skills deep learning expert. Give us some tips on how to structure interview with some coding example?","parameters":{"max_new_tokens":250}}' \
    -H 'Content-Type: application/json'

MD Environment Variables
------------------------

TOKEN_FILE=/opt/ds/model/deployed_model/token
PARAMS="--model-id meta-llama/Llama-2-7b-chat-hf --max-batch-prefill-tokens 1024 "
STORAGE_SIZE_IN_GB=950

DUMMY="dummy"

#meta-llama/Llama-2-7b-chat-hf --quantize bitsandbytes
# --model-id meta-llama/Llama-2-7b-chat-hf --max-batch-prefill-tokens 1024 
# --model-id meta-llama/Llama-2-13b-chat-hf --max-batch-prefill-tokens 1024
# --model-id meta-llama/Llama-2-13b-chat-hf --max-batch-prefill-tokens 1024 --quantize bitsandbytes --max-batch-total-tokens 4096

http_proxy="http://10.68.69.53:80"
https_proxy="http://10.68.69.53:80"
no_proxy="oraclecorp.com,127.0.0.1,localhost,10.89.228.16,10.242.12.81,10.89.228.14"

oci session authenticate --profile-name custboat --region us-ashburn-1

# This uses the OCI-CLI's raw-request feature. More documentation is available here: https://docs.oracle.com/en-us/iaas/tools/oci-cli/2.12.11/oci_cli_docs/cmdref/raw-request.html
# The OCI-CLI is pre-installed in the Cloud Shell environment. More information about Cloud Shell is available here: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cloudshellintro.htm

oci raw-request --http-method POST --target-uri https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqay7so6w2bpwreqxisognml72kdqi4qcjdtnpfykh4xtsq/predict --request-body '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":200}}' --profile custboat --auth security_token



"2023/07/31 16:25:30 [error] 11#11: *4 connect() failed (111: Connection refused) while connecting to upstream, client: 172.19.0.4, server: , request: \"POST /predict HTTP/1.1\", upstream: \"http://127.0.0.1:80/generate\", host: \"10.202.89.3\""



oci raw-request --http-method POST --target-uri https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqa2rdur35ganco2akwhot23rqd54kcpz4mv2ecs5erkdfq/predict --request-body '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":200}}' --profile custboat --auth security_token



oci raw-request --http-method POST --target-uri https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqaj5a53ebpi2zutlf733n22us2lgycd4xesvsn6pzecisa/predict--request-body '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":200}}' --profile custboat --auth security_token


# VLLM

# Parameters - n=1, best_of=1, presence_penalty=0.0, frequency_penalty=0.0, temperature=0.7, top_p=1.0, top_k=-1, use_beam_search=False, stop=[], ignore_eos=False, max_tokens=200, logprobs=None
```
curl http://localhost:80/generate \
    -d '{
        "prompt": "What is Deep Learning?",
        "use_beam_search": false,
        "n": 1,
        "temperature": 0.7,
        "top_p":0.8,
        "max_tokens":200
    }' 
```
```
curl http://localhost:5001/predict \
    -d '{
        "prompt": "What is Deep Learning?",
        "use_beam_search": false,
        "n": 1,
        "temperature": 0.7,
        "top_p":0.8,
        "max_tokens":200
    }' 


```


oci raw-request --http-method POST --target-uri https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqaxfdj6ir53jkmohe6iush7zlq6yjndkv3pic3dnhgwvma/predict --request-body '{"inputs":"Write a python program to randomly select item from a predefined list","parameters":{"max_new_tokens":200}}' --profile custboat --auth security_token

curl http://localhost:5001/predict \
    -d '{
        "prompt": "Write a python program to randomly select item from a predefined list?",
        "use_beam_search": false,
        "n": 1,
        "temperature": 0.7,
        "top_p":0.8,
        "max_tokens":200
    }' 

curl 127.0.0.1:5001/predict \
    -X POST \
    -d '{"inputs":"Write a python program to randomly select item from a predefined list","parameters":{"max_new_tokens":250}}' \
    -H 'Content-Type: application/json'


oci raw-request --http-method POST \
--target-uri https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqafjhabf7dv4kcylmdt52fyyw7yw7n3dnqa3baqyd4d6oq/predict --request-body '{
        "prompt": "Write a python program to randomly select item from a predefined list?",
        "use_beam_search": false,
        "n": 1,
        "temperature": 0.7,
        "top_p":0.8,
        "max_tokens":200
    }' \
    --profile custboat --auth security_token
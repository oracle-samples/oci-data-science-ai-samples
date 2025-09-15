# AI Translation

## Overview

The AI Text Translation Solution delivers fast, accurate language translation powered by state-of-the-art Large Language Models (LLM). By default, it leverages the powerful meta.llama-3.3-70b-instruct model from the OCI Generative AI Service , but you can specify alternative LLMs or connect any OpenAI-compatible model endpoint.

The solution includes REST APIs and Playground UI for experimentation.

## Features

🌐 APIs for translation and language management  
🎛️ Playground UI for rapid hands-on exploration  
📝 Single & Batch Translation support  
🚀 Streaming & Async translation modes  
🔗 Flexible model selection: supports OCI Generative AI and any OpenAI-compatible API

## Deployment
This application can be  deployed using an [Oracle Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm) (ORM) stack as a solution on AI Hub.  To create and deploy the solution, click the button below:

[![Deploy to Oracle Cloud][magic_button]][magic_stack]

## APIs

The APIs include:
* Listing the supported languages
* Text translation supporting streaming and async operations
* Start batch Translation Job

Please see the API reference `/api/docs` for more details and try them out.

[magic_button]: https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg
[magic_stack]: https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-samples/oci-data-science-ai-samples/releases/download/1.0/ai-translation.zip

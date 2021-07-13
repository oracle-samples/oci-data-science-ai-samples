# Model Deploy E2E Simple Demo 

This notebook provides a simple E2E demo for model deploy.

## Overview

You deploy a sklearn random forest model trained on synthetic data. The model is deployed programmatically 
with the OCI Python SDK and invoked with the same SDK. 

### Instructions 

* You can use either resource principals or the config+key authn mechanism to create or invoke the model. The notebook allows for both options. 
* Make sure you read through the notebook first and replace some of the variables with your own values (e.g. <your-deployment-name>)
* By default, logs are not emitted to the Logging service. However, you can set it up yourself by creating custom logs for both predict and access logs. 

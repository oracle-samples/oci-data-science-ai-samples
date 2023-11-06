# Introduction

This codes showcase how to use [Oracle Fn (Functions)](https://fnproject.io/) to execute Model deployment predict endpoint.

## Pre-Requisites

To be able to test the code described on this page, ensure you have access to the Oracle Data Science Model Deploy in your tenancy as well as Oracle Cloud Applications (aka Functions).

## Local Enviroment Setup

To be able to run this example, you have to install OCI SDK and configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm).

The OCI API Auth Token is used for the OCI CLI and Python SDK, as well as all other OCI SDK supported languages. Follow the guidance from the online documentation to configure it: <https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm>

At the high level the instructions are:

- (1) `login` into your Oracle Cloud
- (2) `select your account` from the top right dropdown menu
- (3) generate a new `API Auth Key`
- (4) download the private key and store it into your `$HOME/.oci` folder on your local machine
- (5) copy the suggested configuration and store it into config file under your home directy `$HOME/.oci/config`
- (6) change the `$HOME/.oci/config` with the suggested configuration in (5) to point to your private key
- (7) test the SDK or CLI

For more detailed explanations, follow the instructions from our public documentation.

### Install Desktop Container Management

This example requires a desktop tool to build, run, launch and push the containers. We support:

- [Docker Desktop](<https://docs.docker.com/get-docker>)
- [Rancher Desktop](<https://rancherdesktop.io/>)

### Install and Configure Oracle Functions

To be able to execute this example you have to install the configure Oracle Fn on your local environment.

- Install Oracle Fn <https://fnproject.io/tutorials/install/>
- Create new context: ```fn create context <your-tenancy-name> --provider oracle```
- Update the Fn context to point to your region, for example: ```fn update context api-url https://functions.<your-region>.oci.oraclecloud.com```
- Update the Fn registry to point to your OCIR: ```fn update context registry <region-key>.ocir.io/<your-tenancy-namespace>/<your-repo-name-prefix>```
- Update the Fn contex to point to your compartment: ```fn update context oracle.compartment-id <your-compartment-ocid>```

# Create OCI Function for invoking Model Deployment predict endpoint
This project helps create a function that will be used as a backend for API Gateway. API Gateway endpoint can then be used as a proxy server infront of Model deployment endpoint. Refer [page](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatingfirst.htm) to refer details about creating a sample function.
For more examples, refer functions examples [repo](https://github.com/oracle-samples/oracle-functions-samples).

# Adding Function as API Gateway Backend
Refer [page](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewayusingfunctionsbackend.htm) to find details about how to use function as API Gateway.

# Build using fn cli
```bash
fn -v deploy --app <app-name>
```

# oci-cli based function invocation
```bash
oci fn function invoke --function-id <function-ocid> --file "-" --body '{"ENDPOINT":"<predict-url>", "PAYLOAD": "<json-payload>"}'
```

## Sample:
```bash
oci fn function invoke --function-id <function-ocid> --file "-" --body '{"ENDPOINT":"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/<md-ocid>/predict", "PAYLOAD": "{\"index\": \"1\"}"}'
```

# fn cli based invocation
```bash
fn invoke <app-name> <function-name>
```

## Sample:
```bash
echo -n '{"ENDPOINT":"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/<md-ocid>/predict", "PAYLOAD": "{\"index\": \"1\"}"}' | fn invoke <app-name> <function-name>
```

# More information
The sample code in [func.py](./func.py) also shows how to get headers and request body. Required headers can also be passed to downstream call, if needed.
Other ways of function invocation can be found [here](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinvokingfunctions.htm)

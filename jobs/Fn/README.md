# Introduction

This codes showcase how to use [Oracle Fn (Functions)](https://fnproject.io/) to execute Job Runs.

> Functions can access the Job Runs only if your dynamic group and policies are properly configured.

## Use Cases

__When to use Oracle Functions to start OCI Data Science Jobs?__

Oracle Functions can be triggered from the OCI Events Service <https://docs.oracle.com/en-us/iaas/Content/Events/Concepts/eventsoverview.htm>.

Oracle Cloud Infrastructure Events enables you to create automation based on the state changes of resources throughout your tenancy. Use Events to allow your development teams to automatically respond when a resource changes its state.

Here are some examples of how you might use Events:

- Start a Job on specific database event
- Start a Job when files are uploaded or updated to an Object Storage bucket

## Pre-Requisites

To be able to test the code described on this page, ensure you have access to the Oracle Data Science Jobs in your tenancy as well as Oracle Cloud Applications (aka Functions).

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

### Dynamic Group

For the resource principal in the Function to have access to Jobs and Job Run resources, make sure that you first modify your existing OCI Data Science dynamic group and add the Function resource type. For this you would need to add the following rule in your Dynamic Group.

```xml
all {resource.type='fnfunc'}
```

### Policies

No additional policies required, however make sure that you have the Jobs policies in place as described in our public documentation or the [README.md](../README.md) for jobs.

## Step by Step Guide

This sample contains following files:

- `Dockerfile` - to build the function container
- `func.py` - Oracle Fn code
- `func.yaml` - Oracle Fn configuration
- `jobrunner.py` - simple OCI Python SDK implementation to start OCI Data Science Job Runs
- `requirements.txt` - function required libraries for the example
- `rp.py` - OCI SDK resource principal detector
- `testjobrunner.py` - testing the job runner class, can be used for local testing

### Local Code Test

Builds for local testing, does not copy the code into the image.

```bash
docker build --build-arg type=local -t fnjobrun .
```

Run against the container image, mount the code and pass your comparment, project and job OCID to the runner to start the job. Notice the `$HOME/.oci` is the location of your API Auth Configuration in your local environment.

```bash
docker run --rm \
-e JOB_COMPARTMENT_OCID='ocid1.compartment.oc1..<>' \
-e PROJECT_OCID='ocid1.datascienceproject.oc1.iad.<>' \
-e JOB_OCID="ocid1.datasciencejob.oc1.iad.<>" \
-v $HOME/.oci:/home/datascience/.oci \
-v $PWD:/app \
fnjobrun python -u /app/testjobrunner.py
```

### Local Function Test

> In the file `func.py` you have to `replace` in the job_run function the parameters with your own project, compartment and job OCIDs from your tenancy!

Since we are using the OCI SDK locally, the Function would need access to our API Key to be able to start the Job Run in your tenancy. For that purpose, you have to prepare the `/Fn` project, by creating an local `.oci` folder and copy and past your OCI `config` and `private.pem` key, so that those can be used during the local testing. Unfortunately, we haven't found a way to mount those directly to the Fn Server or the function.

> `Notice` that your API Auth Key does not need to be in the function, when you deploy it, this is only for local testing.

- Create folder in this project to store the config and key

```bash
mkdir .oci
cd .oci
```

- Copy your current OCI API config and key into the local folder

```bash
cp $HOME/.oci/config .
cp $HOME/.oci/your-oci-private-key.pem .
```

> You do not need to change the `key_file` in the `config`, as long as it starts with `~/.oci/your-oci-private-key.pem`

- Start the Fn server.

```bash
fn -v start --log-level debug
```

- Use the local context

```bash
fn use context default
```

- Create local Fn App

```bash
fn create app jobs
```

- Verify the app exist

```bash
fn list apps
```

- Build and deploy the app locally (notice from within the `/Fn` folder)

```bash
fn -v deploy --app jobs --local --build-arg type=fnl
```

- Test the function

```bash
fn invoke jobs runjob
```

This should start the Job Run in your tenancy.

---
*__:scream: If you enounter folloing error, when using Rancher Desktop__*
`Error when invoking the function`: Error invoking function. status: 502 message: Container failed to initialize, please ensure you are using the latest fdk and check the logs

`Error shown in the Fn Server`: PermissionError: [Errno 1] Operation not permitted\n

*__:sparkles: Solution__*
This issue happens when Rancher Desktop is used, workaround is provided in the following thread: <https://github.com/fnproject/fn/issues/1577>

Run following command to start your local Fn server instead:

```bash
docker run --rm -i --name fnserver \
-v /tmp/iofs:/iofs \
-e FN_IOFS_DOCKER_PATH=/tmp/iofs \
-e FN_IOFS_PATH=/iofs \
-v /tmp/data:/app/data \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $HOME/.oci:/home/datascience/.oci \
--privileged \
-p 8080:8080 \
--entrypoint ./fnserver \
-e FN_LOG_LEVEL=DEBUG fnproject/fnserver:latest
```

### Inspect the Container Image Content

To inspect the Function container image content.

```bash
docker run -it --entrypoint sh fnlvp/runjob:0.0.<version>
cd /home/datascience/
ls -alsh
```

## Deploy the Function

Make sure that you have your own context configured and pointing to your tenancy OCID, as shown at the beggining of this guide!

```bash
fn use context <your-tenancy-context>
```

- Create local Fn App

```bash
fn create app jobs --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'
```

For more information follow <https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatingapps.htm>

- Verify the app exist

```bash
fn list apps
```

- Build and deploy the app locally (notice from within the `/Fn` folder)

```bash
fn -v deploy --app jobs --build-arg type=fn
```

- Test the function

```bash
fn invoke jobs runjob
```

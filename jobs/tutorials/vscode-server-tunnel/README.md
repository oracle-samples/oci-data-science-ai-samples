# Introduction

The [Visual Studio Code Remote - Tunnels](https://code.visualstudio.com/docs/remote/tunnels) extension lets you connect to a remote machine, like a desktop PC or virtual machine (VM), via a secure tunnel. You can connect to that machine from a VS Code client anywhere, without the requirement of SSH, including also using the Oracle Cloud Infrastructure Data Science Jobs.

The tunneling securely transmits data from one network to another. This can eliminate the need for source code to be on your VS Code client machine since the extension runs commands and other extensions directly on the OCI Job remote machine.

## Requirements

This example requires a container client CLI to build and test your container image and push it to the Oracle Cloud Container Registry

- Install [Docker](<https://docs.docker.com/get-docker>) **or** [Rancher Desktop](<https://rancherdesktop.io/>) as docker alternative

## Build and Run

You can test this example locally to verify it is running, then execute as a job.

### Build and run locally

Builds the docker image for a quick local run.

```bash
docker build --build-arg type=remote -t vscode .
```

:exclamation:On Apple Silicon

```bash
docker buildx build --platform linux/amd64 --build-arg type=remote -t vscode .
```

To run it:

```bash
docker run --rm vscode
```

This will produce an output similar to:

```bash
opening code tunnel
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   133  100   133    0     0    197      0 --:--:-- --:--:-- --:--:--   197
100 6166k  100 6166k    0     0  4395k      0  0:00:01  0:00:01 --:--:-- 11.5M
*
* Visual Studio Code Server
*
* By using the software, you agree to
* the Visual Studio Code Server License Terms (https://aka.ms/vscode-server-license) and
* the Microsoft Privacy Statement (https://privacy.microsoft.com/en-US/privacystatement).
*
To grant access to the server, please log into https://github.com/login/device and use code XXXX-XXXX
```

This requires you to open the link `https://github.com/login/device`, login with your GitHub account and use the code `XXXX-XXXX` to verify and authorize the tunneling.

Once this is complete, following would appear int the logs:

```bash
[2023-02-28 12:39:53] info Creating tunnel with the name: nice-seedeater

Open this link in your browser https://vscode.dev/tunnel/nice-seedeater/aiapps
```

**Notice** the link would be different for you! Copy the link and open it in your browser. This would load the VSCode Editor and enables to work directly against your container.

### Build and run as a Job

To run the job on the OCI Data Science Service

#### OCIR Login

You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before, to been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once. You can find all the Oracle Cloud Regions Keys at [Regions Documentation Page](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)

```bash
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

#### Tag & Push

Tag the container to the location of the OCIR you wish to push it later. You could also build the container with that tag directly, if you like to save a step.

```bash
docker tag <tag>:<version> <region>.ocir.io/<namespace>/<tag>:<version>
```

**Replace** the `<region>`, `<namespace>`, `<tag>` and `<version>`

Example:

```bash
docker tag vscode:latest iad.ocir.io/mytenancy/vscode:1.0
```

Then push the container

```bash
docker push iad.ocir.io/mytenancy/vscode:1.0
```

#### Run as a JOB

Create a job and use following job environment variable, poiting to the location of the container image in your OCIR.

`CONTAINER_CUSTOM_IMAGE=<region>.ocir.io/<namespace>/<tag>:<version>`

For example:
`CONTAINER_CUSTOM_IMAGE=iad.ocir.io/datadatascience/byoc:1.0`

**Notice** that logging should be enabled for the job, to reveal the code required to authorize the tunnel. Additionally use either Default Networking or a custom private subnet with configured NAT networking that enables access to the Internet.

:exclamation: Make sure the policy for the Jobs Resource Principal is configured allowing to read from the Oracle Container Registry from the compartment where the image was stored.

> Allow dynamic-group {YOUR-DYNAMIC-GROUP-NAME} to read repos in compartment {YOUR-COMPARTMENT-NAME}

Once the job is up and running, you will notice in the logs, the authentication code appears, you can copied and use it to authorize the tunnel, few seconds later the link for the tunnel would appear.

![vscode tunnel in the oci job](../assets/images/vscde-server-tunnel-job.png)

Copy the link and open it in a browser, which should load the VSCode Editor and reveals the code inside the job, enabling direct debugging and coding.

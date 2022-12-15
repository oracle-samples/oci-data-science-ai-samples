# Bring Your Own Container with Jobs

You can build and use your own container for use when you create a job and job runs. To run the job, you have to make your own Dockerfile, and build an image. In this example the `Dockerfile` is designed so that you can make local and remote builds.

You use the local build when you test locally against your code. During the local development, you don't need to build a new image for every code change. Use the remote option to run the Dockerfile when you think your code is complete, and you want to run it as a job.

## Prerequisite

- Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally
- Install [Docker](<https://docs.docker.com/get-docker>) **or** [Rancher Desktop](<https://rancherdesktop.io/>) as docker alternative

## Build and Run

### Build to test run locally

Builds the docker image but does not include the code for quick run, debug etc.

```bash
docker build --build-arg type=local -t byoc .
```

:exclamation:On Apple Silicon

```bash
docker buildx build --platform linux/amd64 --build-arg type=local -t byoc .
```

### Run local test with the code location mounted

:exclamation:Notice the we mount your `./oci` api auth key to the docker home user directory. If youse different user in the docker container you have to change the `/home/datascience/.oci` path. For example if you use root account, change to `/root/.oci`

```bash
docker run --rm -v $HOME/.oci:/home/datascience/.oci \
 -v $PWD:/app byoc python /app/job_logs.py
```

### Build to run as a Job

Builds the docker with the code in the image ready to run as job. Notice we change now the type to `remote`. The variable behivour is configured in the `Dockerfile`

```bash
docker build --build-arg type=remote -t byoc .
```

:exclamation:On Apple Silicon

```bash
docker buildx build --platform linux/amd64 --build-arg type=remote -t byoc .
```

### Run local test with the code in the container

:exclamation:Notice even when the container was build using the `remote` option to store the code in the image, for a local run the OCI API Auth Key is still required.

```bash
docker run --rm -v $HOME/.oci:/home/datascience/.oci -v $PWD:/app byoc
```

### To browse the container code

In you case you want to have a look into the container the assets inside:

```bash
docker run -it byoc sh
ls
exit
```

## OCIR Login

You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

```bash
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

## Tag & Push

:exclamation:Build the image with the `type=remote` option before tagging and pushing.

Tag the container to the location of the OCIR you would push it later.

```bash
docker tag <tag>:<version> <region>.ocir.io/<namespace>/<tag>:<version>
```

**Replace** the `<region>`, `<namespace>`, `<tag>` and `<version>` with yours.

Example:

```bash
docker tag byoc:latest iad.ocir.io/datadatascience/byoc:1.0
```

Then push the container to the tagged location

```bash
docker push iad.ocir.io/datadatascience/byoc:1.0
```

## Run as a JOB

Create a job and use following job environment variable, poiting to the location of the container image in your OCIR.

`CONTAINER_CUSTOM_IMAGE=iad.ocir.io/datadatascience/byoc:1.0`

:exclamation:Make sure Jobs has a policy for the resource principal allowing to read the Oracle Container Registry from the compartment where the image was stored

> Allow dynamic-group {YOUR-DYNAMIC-GROUP-NAME} to read repos in compartment {YOUR-COMPARTMENT-NAME}

## Optional

Instead of hardcoding the ENTRYPOINT and the CMD in the Dockerfile, you can also pass those using following environment variables:

- `CONTAINER_ENTRYPOINT` - the container image entrypoints as a list of strings: `"ls", "-l"`
- `CONTAINER_CMD` - the container run CMD as a list of strings: `"ls", "-l", "-a", "-h"`

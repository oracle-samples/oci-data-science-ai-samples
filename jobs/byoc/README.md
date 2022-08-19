# Bring Your Own Container with Jobs

You can build and use your own container for use when you create a job and job runs. To run the job, you have to make your own Dockerfile, and build an image. In this example the `Dockerfile` is designed so that you can make local and remote builds.

You use the local build when you test locally against your code. During the local development, you don't need to build a new image for every code change. Use the remote option to run the Dockerfile when you think your code is complete, and you want to run it as a job.

## Build

### To run locally

Builds the docker image but does not include the code for quick run, debug etc.

```bash
docker build --build-arg type=local -t byoc .
```

### To run as a Job

Builds the docker with the code in the image ready to run as job.

```bash
docker build --build-arg type=remote -t byoc .
```

## RUN

:exclamation:  Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to run locally

### Local testing with the code location mounted

:exclamation:  Notice the we mount your `./oci` api auth key to the docker home user directory. If youse different user in the docker container you have to change the `/home/datascience/.oci` path. For example if you use root account, change to `/root/.oci`

```bash
docker run --rm -v $HOME/.oci:/home/datascience/.oci -v $PWD:/app byoc python /app/job_logs.py
```

### Local testing with the code is in the container

:exclamation:  Notice even when the container was build using the `remote` option to store the code in the image, for a local run the OCI API Auth Key is still required.

```bash
docker run --rm -v $HOME/.oci:/home/datascience/.oci -v $PWD:/app byoc
```

### Enter and browse the container code

```bash
docker run -it byoc sh
ls
exit
```

## TAG & PUSH

:exclamation: Build the image with the `type=remote` option before tagging and pushing.

Tag the image to the location of your OCIR in Oracle Cloud and push it. You may need to `docker login` to the Oracle Cloud OCIR repor first, if you haven't done so before been able to push the image. To login you have to use your `Auth Token` that can be created under your Oracle Cloud Account->Auth Token. `You need to login only once!`

```bash
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

```bash
docker tag byoc:latest iad.ocir.io/bigdatadatasciencelarge/byoc:1.0
```

```bash
docker push iad.ocir.io/bigdatadatasciencelarge/byoc:1.0
```

## Run as a JOB

Create a job and use following job environment variable, poiting to the location of the container image in your OCIR.

CONTAINER_CUSTOM_IMAGE=iad.ocir.io/bigdatadatasciencelarge/byoc:1.0

:exclamation: Make sure Jobs has a policy for the resource principal allowing to read the OCIR from the compartment where the image was stored

> Allow dynamic-group {YOUR-DYNAMIC-GROUP-NAME} to read repos in compartment {YOUR-COMPARTMENT-NAME}

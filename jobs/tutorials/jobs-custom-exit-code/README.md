# Job with Custom Exist Code

In some situations we would like to exit the job run with custom specified exit code.

`NOTICE:` the exits error code has to be of type `Number`
`IMPORTANT`: the exit code has to be between 1 and 255

This folder contains following samples:

- fail-with-code.py - with hard coded error code
- fail-code-exit.py - set your own error code
- shell-with-exit.sh - demonstrates exit code usage in shell script

Build to test and run locally

```bash
docker build --build-arg type=local -t exit-code .
docker run --rm -v $PWD:/app exit-code python /app/fail-with-code.py
```

Build to run as a job

```bash
docker build --build-arg type=remote -t exit-code .
docker run --rm -v $PWD:/app exit-code
```

Tag and push to OCIR

```bash
docker tag exit-code:latest <region>.ocir.io/<tenancy>/<repository>:<tag>
docker push <region>.ocir.io/<tenancy>/<repository>:<tag>
```

Create a Data Science Job and set the OCIR URI to the pushed container image

`CONTAINER_CUSTOM_IMAGE=<region>.ocir.io/<tenancy>/<repository>:<tag>`

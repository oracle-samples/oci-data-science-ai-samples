# Jobs With Custom Exit Code

Sometimes it might be useful to return a special exit code with the job, a code that the customer can specify, depending on internal error. Jobs now enables to exit with the job code with customer specified exit code that will appear in the lifecycle detail, example:

![job with custom exit code in OCI console](assets/images/job-exit-code.png)

## Requirements

- the exit code has to be from type Number
- the exit code has to be a Number between 1-255

<span style="background:lightgreen; padding:5px; border-radius:7px"> :bulb: This feature works with `Python Code` and/or `Shell Scripts` as well as `BYOC` (Bring Your Own Container) Jobs! </span>

## Examples

:large_orange_diamond: <span style="background:lightblue; padding:5px; border-radius:7px">`Python` Custom Exit Code Sample</span>

```python
import sys
 
print("Going to exit with 64 :D")
 
# Max allowed 255 error code
sys.exit(64)
```

:large_orange_diamond: <span style="background:lightblue; padding:5px; border-radius:7px">`Python` Custom Exit Code with Environment Variables</span>

```python
import os, sys
from datetime import datetime
 
# Max 255 error code
SUCCESS = 255
 
# Set custom code, NOTICE the code has to be Number
ERROR_CODE = int(os.environ.get("CODE", SUCCESS))
 
print(f'Job Run {datetime.now().strftime("%m-%d-%Y-%H:%M:%S")}')
 
if ERROR_CODE != SUCCESS:
    print(f"Job should exit with code:  ({ERROR_CODE})")
    sys.exit(ERROR_CODE)
else:
    print("Job Done.")
```

:large_orange_diamond: <span style="background:lightblue; padding:5px; border-radius:7px">`Shell` Script With Custom Exit Code</span>

```bash
#!/bin/bash
var=$1
if [ -z "$var" ]
then
      echo "no argument provided"
      exit 100
else
      while [ "$1" != "" ]; do
        echo "Received: ${1}" && shift;
      done
fi
```

:heavy_exclamation_mark: <span style="background:orange; padding:5px; border-radius:7px"> `Notice` that if you execute a code with shell script, you have to catch the exit code and raised it up, otherwise the JobRun end showing successful run.</span>

```bash
#!/bin/bash
python job_logs.py $0
 
exit_status=$?
echo $exit_status
 
exit $exit_status
```

:large_orange_diamond: <span style="background:lightblue; padding:5px; border-radius:7px">`BYOC` Jobs</span>

Custom exit codes works also with BYOC, example Dockerfile:

```Dockerfile
ARG type
 
FROM python:3.8-slim AS base
 
ENV DATASCIENCE_USER datascience
ENV DATASCIENCE_UID 1000
ENV HOME /home/$DATASCIENCE_USER
 
RUN python -m pip install \
    parse \
    oci
 
 
FROM base AS run-type-local
# nothing to see here
 
FROM base AS run-type-remote
COPY fail-with-code.py .
CMD ["python", "fail-with-code.py"]
 
FROM run-type-${type} AS final
```

`Build the container to test and run locally`

```bash
docker build --build-arg type=local -t exit-code .
docker run --rm -v $PWD:/app exit-code python /app/fail-with-code.py
```

`Build the container to run as a job`

```bash
docker build --build-arg type=remote -t exit-code .
docker run --rm -v $PWD:/app exit-code
```

`Tag and push to OCIR`

```bash
docker tag exit-code:latest <region>.ocir.io/<tenancy>/<repository>:<tag>
docker push <region>.ocir.io/<tenancy>/<repository>:<tag>
```

Create a Data Science Job and set the OCIR URI to the pushed container image

`CONTAINER_CUSTOM_IMAGE=<region>.ocir.io/<tenancy>/<repository>:<tag>`

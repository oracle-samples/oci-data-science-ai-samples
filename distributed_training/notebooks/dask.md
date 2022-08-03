# Developer Guide

## Steps to run Distributed Dask

All the docker image related artifacts are located under - `oci_dist_training_artifacts/dask/v1/`


### 1. Prepare Docker Image

The instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework dask`

All files in the current directory is copied over to `/code` folder inside docker image. 

For example, you can have the following grid search script saved as train.py:

```
from dask.distributed import Client
from sklearn.datasets import make_classification
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

import pandas as pd
import joblib
import os
import argparse

default_n_samples = int(os.getenv("DEFAULT_N_SAMPLES", "1000"))

parser = argparse.ArgumentParser()
parser.add_argument("--n_samples", default=default_n_samples, type=int, help="size of dataset")
parser.add_argument("--cv", default=3, type=int, help="number of cross validations")
args, unknownargs = parser.parse_known_args()

# Using environment variable to fetch the SCHEDULER_IP is important.
client = Client(f"{os.environ['SCHEDULER_IP']}:{os.environ.get('SCHEDULER_PORT','8786')}")

X, y = make_classification(n_samples=args.n_samples, random_state=42)

with joblib.parallel_backend("dask"):
    GridSearchCV(
        SVC(gamma="auto", random_state=0, probability=True),
        param_grid={
            "C": [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            "kernel": ["rbf", "poly", "sigmoid"],
            "shrinking": [True, False],
        },
        return_train_score=False,
        cv=args.cv,
        n_jobs=-1,
    ).fit(X, y)

```

**Note**: Whenever you change the code, you have to build, tag and push the image to repo. If you change the tag, it needs to be updated inside the cluster definition yaml.

The required python dependencies are provided inside `oci_dist_training_artifacts/dask/v1/environment.yaml`.  If you code required additional dependency, update the `environment.yaml` file. 

**Note**: While updating `environment.yaml` do not remove the existing libraries. You can append to the list.

Building docker image - 

Update the TAG and the IMAGE_NAME as per your needs - 

```
export IMAGE_NAME=<region.ocir.io/my-tenancy/image-name>
export TAG=latest
```

```
docker build -t $IMAGE_NAME:$TAG \
    -f oci_dist_training_artifacts/dask/v1/Dockerfile .

```

If you are behind proxy, use this command - 

```
docker build  --build-arg no_proxy=$no_proxy \
              --build-arg http_proxy=$http_proxy \
              --build-arg https_proxy=$http_proxy \
              -t $IMAGE_NAME:$TAG \
              -f oci_dist_training_artifacts/dask/v1/Dockerfile .
```

Push the docker image - 

```
docker push $IMAGE_NAME:$TAG
```

### 2. Test locally with help of `docker-compose`

Create `docker-compose.yaml` file and copy the following content. Update the object storage path for `OCI__WORK_DIR`

**Note** For local testing only `WORKER_COUNT=1` is supported.

Once the docker-compose.yaml is created, you can start the containers by running - 

```
docker compose up
```
You can learn more about docker compose [here](https://docs.docker.com/compose/)


```
export WORK_DIR=oci://<my-bucket>@<my-tenancy>/prefix
```
Alternative to exporting variable is to define it inline - 

```
IMAGE_NAME=iad.ocir.io/<tenancy>/<repo-name> TAG=<TAG> WORK_DIR=oci://<my-bucket>@<tenancy>/<prefix> docker compose up
```

```
#docker-compose.yaml for distributed dask testing
# The cleanup step will delete all the files in the WORK_DIR left over from the previous run

version: "0.1"
services:
  cleanup:
      image: $IMAGE_NAME:$TAG
      network_mode: host
      entrypoint: /etc/datascience/cleanup.sh
      volumes:
          - ~/.oci:/home/datascience/.oci
      environment:
          OCI_IAM_TYPE: api_key
          OCI_CONFIG_PROFILE: DEFAULT
          OCI__WORK_DIR: $WORK_DIR
  scheduler:
      image: $IMAGE_NAME:$TAG
      network_mode: host
      depends_on:
          - cleanup
      volumes:
          - ~/.oci:/home/datascience/.oci
      environment:
          OCI__MODE: MAIN
          OCI__START_ARGS: --port 8786
          OCI__CLUSTER_TYPE: DASK
          OCI__ENTRY_SCRIPT: gridsearch.py
          OCI__ENTRY_SCRIPT_KWARGS: "--cv 5"
          DEFAULT_N_SAMPLES: 100
          OCI__WORK_DIR: $WORK_DIR
          OCI_IAM_TYPE: api_key
          OCI_CONFIG_PROFILE: DEFAULT
          OCI__EPHEMERAL: 1
          OCI__WORKER_COUNT: 1

  worker-0:
      image: $IMAGE_NAME:$TAG
      network_mode: host
      depends_on:
          - cleanup
      volumes:
          - ~/.oci:/home/datascience/.oci
      environment:
          OCI__MODE: WORKER
          OCI__CLUSTER_TYPE: DASK
          OCI__ENTRY_SCRIPT: gridsearch.py
          OCI__ENTRY_SCRIPT_ARGS: 50
          NAMED_OCI__ENTRY_SCRIPT_ARGS: "--cv 5"
          DEFAULT_N_SAMPLES: 100
          OCI__WORK_DIR: $WORK_DIR
          OCI__START_ARGS: --worker-port 8700:8800 --nanny-port 3000:3100 --death-timeout 10 --nworkers 1 --nthreads 1 --death-timeout 60
          OCI_IAM_TYPE: api_key
          OCI_CONFIG_PROFILE: DEFAULT
          OCI__EPHEMERAL: 1
          OCI__WORKER_COUNT: 1
```
### 3. Create yaml file to define your cluster. 

Cluster is specified using yaml file. Below is an example to bring up 2 worker nodes and 1 scheduler node. The code to run is `gridserach.py`. All code is assumed to be present inside `/code` directory within the container.

Please refer to the [documentation](http://10.209.39.50:8000/user_guide/model_training/distributed_training/dask/creating.html) for more details.

```
# Example train.yaml for defining dask cluster

kind: distributed
apiVersion: v1.0
spec:
  infrastructure:
    kind: infrastructure
    type: dataScienceJob
    apiVersion: v1.0
    spec:
      projectId: oci.xxxx.<project_ocid>
      compartmentId: oci.xxxx.<compartment_ocid>
      displayName: my_distributed_training
      logGroupId: oci.xxxx.<log_group_ocid>
      logId: oci.xxx.<log_ocid>
      subnetId: oci.xxxx.<subnet-ocid>
      shapeName: VM.Standard2.4
      blockStorageSize: 50
  cluster:
    kind: dask
    apiVersion: v1.0
    spec:
      image: my-region.ocir.io/my-tenancy/dask-cluster-examples:dev
      workDir: "oci://my-bucket@my-namespace/daskexample/001"
      name: GridSearch Dask
      main:
          config:
      worker:
          config:
          replicas: 2
  runtime:
    kind: python
    apiVersion: v1.0
    spec:
      entryPoint: "gridsearch.py"
      kwargs: "--cv 5"
      env:
        - name: DEFAULT_N_SAMPLES
          value: 5000
```

### 4. Dry Run to validate the Yaml definition 

```
ads opctl run -f train.yaml --dry-run
```

This will print the Job and Job run configuration without launching the actual job.

### 5. Start Distributed Job

This will run the command and also save the output to `info.yaml`. You could use this yaml for checking the runtime details of the cluster - scheduler ip.

```
ads opctl run -f train.yaml | tee info.yaml
```

### 6. Tail the logs

This command will stream the log from logging infrastructure that you provided while defining the cluster inside `train.yaml` in the example above.

```
ads opctl watch <job runid>
```

### 7. Check runtime configuration, run - 

```
ads opctl distributed-training show-config -f info.yaml
```

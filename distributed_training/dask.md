# Developer Guide

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

## Steps to run Distributed Dask

All the docker image related artifacts are located under - `oci_dist_training_artifacts/dask/v1/`

### Prerequisite

You need to install [ads](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html#).

```bash
python3 -m pip install oracle-ads[opctl]
```

This guide uses ```ads opctl``` for creating distributed training jobs. Refer [distributed_training_cmd.md](distributed_training_cmd.md) for supported commands and options for distributed training.

### 1. Prepare Docker Image

The instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework dask`

All files in the current directory is copied over to `/code` folder inside docker image.

For example, you can have the following grid search script saved as train.py;

<details>
<summary><b>gridsearch.py</b> <== click to open</summary>

```python
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

# Using environment variable to fetch the SCHEDULER_IP is important

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

</details>
&nbsp;

**Note**: Whenever you change the code, you have to build, tag and push the image to repo. This is automatically done in ```ads opctl run``` cli command.

The required python dependencies are provided inside `oci_dist_training_artifacts/dask/v1/environment.yaml`.  If you code required additional dependency, update the `environment.yaml` file.

While updating `environment.yaml` do not remove the existing libraries. You can append to the list.

Set the TAG and the IMAGE_NAME as per your needs. `IMAGE_NAME` refers to your Oracle Cloud Container Registry you created in the [Getting Stared Guide](README.md). `MOUNT_FOLDER_PATH` is the root directory of your project code, but you can use `.` in case you executed all of the `ads opctl run` commands directly from your root project folder.

```bash
export IMAGE_NAME=<region>.ocir.io/<namespace>/<repository-name>
export TAG=latest
export MOUNT_FOLDER_PATH=.
```

**Replace** the `<region>` with the name of the region where you created your repository and you will run your code, for example `iad` for Ashburn. **Replace** the `<namespace>` with the namespace you see in your Oracle Cloud Container Registry, when you created your repository. **Replace** the `<repository-name>` with the name of the repository you used to create it.

Build the container image.

```bash
ads opctl distributed-training build-image \
  -t $TAG \
  -reg $IMAGE_NAME \
  -df oci_dist_training_artifacts/dask/v1/Dockerfile \
  -s $MOUNT_FOLDER_PATH
```

If you are behind proxy, ads opctl will automatically use your proxy settings( defined via ```no_proxy```, ```http_proxy``` and ```https_proxy```).

### 2. Create yaml file to define your cluster

Cluster is specified using yaml file. Below is an example to bring up 2 worker nodes and 1 scheduler node. The code to run is `gridserach.py`. All code is assumed to be present inside `/code` directory within the container.

Please refer to the [documentation](http://10.209.39.50:8000/user_guide/model_training/distributed_training/dask/creating.html) for more details.

```yaml
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
      image: "@image"
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

**Note**: make sure that the `workDir` points to your object storage bucket at OCI.

For `flex shapes` use following in the `train.yaml` file

```yaml
shapeConfigDetails:
    memoryInGBs: 22
    ocpus: 2
shapeName: VM.Standard.E3.Flex
```

### 3. Local Testing

Before triggering the job run, you can test the docker image and verify the training code, dependencies etc.

#### 3a. Test locally with stand-alone run (Recommended)

In order to test the training code locally, use the following command. With ```-b local``` flag, it uses a local backend. Further when you need to run this workload on odsc jobs, simply use ```-b job```
flag instead (default).

```bash
ads opctl run \
  -f train.yaml \
  -b local
```

If your code requires to use any oci services (like object bucket), you need to mount oci keys from your local host machine onto the docker container. This is already done for you assuming the typical location of oci keys ```~/.oci```. You can modify it though, in-case you have keys at a different location. You need to do this in the ```config.ini``` file.

```init
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

**Note**: The training script location (entrypoint) and associated args will be picked up from the runtime ```train.yaml```.
**Note**:

For detailed explanation of local run, Refer this [distributed_training_cmd.md](distributed_training_cmd.md)

You can also test in a clustered manner using docker-compose. Next section.

### 3b. Test locally with `docker-compose` based cluster

Create `docker-compose.yaml` file and copy the content from the example compose file below.

**Note** For local testing only `WORKER_COUNT=1` is supported.

<details>
<summary><b>docker-compose.yaml</b></summary>

```yaml
# docker-compose.yaml for distributed dask testing

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

</details>
&nbsp;

Set your `WORK_DIR` and `IMAGE_NAME` to be used with the docker-compose.yml.

```bash
export WORK_DIR=oci://<my-bucket>@<my-tenancy>/prefix
export TAG=<TAG>
export WORK_DIR=oci://<my-bucket>@<tenancy>/<prefix>
```

Alternativly you can set those directly into the `docker-compose.yml` file

```yaml
image: iad.ocir.io/<tenancy>/<repo-name>:<tag>
OCI__WORK_DIR: oci://<my-bucket>@<tenancy>/<prefix>
```

Once the `docker-compose.yaml` is created, you can start the containers by running:

```bash
docker compose up
```

You can learn more about docker compose [here](https://docs.docker.com/compose/)

### 4. Dry Run to validate the Yaml definition

```bash
ads opctl run -f train.yaml --dry-run
```

This will print the Job and Job run configuration without launching the actual job.

### 5. Start Distributed Job

This will run the command and also save the output to `info.yaml`. You could use this yaml for checking the runtime details of the cluster - scheduler ip.

```bash
ads opctl run -f train.yaml | tee info.yaml
```

### 6. Tail the logs

This command will stream the log from logging infrastructure that you provided while defining the cluster inside `train.yaml` in the example above.

```bash
ads opctl watch <job runid>
```

### 7. Check runtime configuration, run -

```bash
ads opctl distributed-training show-config -f info.yaml
```

### 8. Saving Artifacts to Object Storage Buckets

In case you want to save the artifacts generated by the training process (model checkpoints, TensorBoard logs, etc.) to an object bucket
you can use the 'sync' feature. The environment variable ``OCI__SYNC_DIR`` exposes the directory location that will be automatically synchronized
to the configured object storage bucket location. Use this directory in your training script to save the artifacts.

To configure the destination object storage bucket location, use the following settings in the workload yaml file(train.yaml).

```yaml
  - name: SYNC_ARTIFACTS
    value: 1
  - name: WORKSPACE
    value: "<bucket_name>"
  - name: WORKSPACE_PREFIX
    value: "<bucket_prefix>"
```

**Note**: Change ``SYNC_ARTIFACTS`` to ``0`` to disable this feature.
Use ``OCI__SYNC_DIR`` env variable in your code to save the artifacts. Example:

```python
with open(os.path.join(os.environ.get("OCI__SYNC_DIR"),"results.txt"), "w") as rf:
    rf.write(f"Best Params are: {grid.best_params_}, Score is {grid.best_score_}")
```

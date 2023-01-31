# Developer Guide

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

## Steps to run Distributed Tensorflow

All the container image related artifacts are located under  `oci_dist_training_artifacts/tensorflow/v1/`

### Prerequisite

This guide uses `ads[opctl]` for creating and running distributed training jobs. Make sure that you follow the [Getting Started Guide](README.md) first.

Refer our [distributed training guide](distributed_training_cmd.md) for supported commands and options for distributed training.

### Prepare the Project

The instruction assumes that you are running this within the folder where you initlize your tensorflow distributed training project. If you haven't done so yet, please run following command:

Create project folder and enter the folder:

```bash
mkdir dt-tf
cd dt-tf
```

Initialize the Tensorflow distributed training project in the folder.

```bash
ads opctl distributed-training init --framework tensorflow
```

You can also initialize existing projects.

### Setup Sample Code

Use the following training Tensorflow scripts for `MultiWorkerMirroredStrategy`.

Saved the following script as `mnist.py`:

<details>
<summary><b>mnist.py</b> <= click to open and copy</summary>

```python
# Script adapted from tensorflow tutorial: https://www.tensorflow.org/tutorials/distribute/multi_worker_with_keras

# ==============================================================================

import tensorflow as tf
import tensorflow_datasets as tfds
import os
import sys
import time
import ads
from ocifs import OCIFileSystem
from tensorflow.data.experimental import AutoShardPolicy

BUFFER_SIZE = 10000
BATCH_SIZE_PER_REPLICA = 64

if '.' not in sys.path:
    sys.path.insert(0, '.')


def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def create_dirs(task_type="worker", task_id=0):
    artifacts_dir = os.environ.get("OCI__SYNC_DIR", "/opt/ml")
    model_dir = artifacts_dir + "/model"
    print("creating dirs for Model: ", model_dir)
    create_dir(model_dir)
    checkpoint_dir = write_filepath(artifacts_dir, task_type, task_id)
    return artifacts_dir, checkpoint_dir, model_dir

def write_filepath(artifacts_dir, task_type, task_id):
    if task_type == None:
        task_type = "worker"
    checkpoint_dir = artifacts_dir + "/checkpoints/" + task_type + "/" + str(task_id)
    print("creating dirs for Checkpoints: ", checkpoint_dir)
    create_dir(checkpoint_dir)
    return checkpoint_dir


def scale(image, label):
    image = tf.cast(image, tf.float32)
    image /= 255
    return image, label


def get_data(data_bckt=None, data_dir="/code/data", num_replicas=1, num_workers=1):
    if data_bckt is not None and not os.path.exists(data_dir + '/mnist'):
        print(f"downloading data from {data_bckt}")
        ads.set_auth(os.environ.get("OCI_IAM_TYPE", "resource_principal"))
        authinfo = ads.common.auth.default_signer()
        oci_filesystem = OCIFileSystem(**authinfo)
        lck_file = os.path.join(data_dir, '.lck')
        if not os.path.exists(lck_file):
            os.makedirs(os.path.dirname(lck_file), exist_ok=True)
            open(lck_file, 'w').close()
            oci_filesystem.download(data_bckt, data_dir, recursive=True)
        else:
            print(f"data downloaded by a different process. waiting")
            time.sleep(30)

    BATCH_SIZE = BATCH_SIZE_PER_REPLICA * num_replicas * num_workers
    print("Now printing data_dir:", data_dir)
    datasets, info = tfds.load(name='mnist', with_info=True, as_supervised=True, data_dir=data_dir)
    mnist_train, mnist_test = datasets['train'], datasets['test']
    print("num_train_examples :", info.splits['train'].num_examples, " num_test_examples: ",
          info.splits['test'].num_examples)

    train_dataset = mnist_train.map(scale).cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE)
    test_dataset = mnist_test.map(scale).batch(BATCH_SIZE)
    train = shard(train_dataset)
    test = shard(test_dataset)
    return train, test, info


def shard(dataset):
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = AutoShardPolicy.DATA
    return dataset.with_options(options)


def decay(epoch):
    if epoch < 3:
        return 1e-3
    elif epoch >= 3 and epoch < 7:
        return 1e-4
    else:
        return 1e-5


def get_callbacks(model, checkpoint_dir="/opt/ml/checkpoints"):
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    class PrintLR(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            print('\nLearning rate for epoch {} is {}'.format(epoch + 1, model.optimizer.lr.numpy()), flush=True)

    callbacks = [
        tf.keras.callbacks.TensorBoard(log_dir='./logs'),
        tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix,
                                           # save_weights_only=True
                                           ),
        tf.keras.callbacks.LearningRateScheduler(decay),
        PrintLR()
    ]
    return callbacks


def build_and_compile_cnn_model():
    print("TF_CONFIG in model:", os.environ.get("TF_CONFIG"))
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10)
    ])

    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  optimizer=tf.keras.optimizers.Adam(),
                  metrics=['accuracy'])
    return model
```

</details>
&nbsp;

Save the following script as `train.py`:

<details>
<summary><b>train.py</b> <= click to open and copy</summary>

```python
import tensorflow as tf
import argparse
import mnist


print(tf.__version__)

parser = argparse.ArgumentParser(description='Tensorflow Native MNIST Example')
parser.add_argument('--data-dir',
                    help='location of the training dataset in the local filesystem (will be downloaded if needed)',
                    default='/code/data')
parser.add_argument('--data-bckt',
                    help='location of the training dataset in an object storage bucket',
                    default=None)

args = parser.parse_args()

artifacts_dir, checkpoint_dir, model_dir = mnist.create_dirs()

strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

train_dataset, test_dataset, info = mnist.get_data(data_bckt=args.data_bckt, data_dir=args.data_dir,
                                                   num_replicas=strategy.num_replicas_in_sync)
with strategy.scope():
    model = mnist.build_and_compile_cnn_model()

model.fit(train_dataset, epochs=2, callbacks=mnist.get_callbacks(model, checkpoint_dir))

model.save(model_dir, save_format='tf')
```

</details>
&nbsp;

All the files from your root project directory will be copied to the `/code` folder inside container image.

### Build the Container Image

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
  -df oci_dist_training_artifacts/tensorflow/v1/Dockerfile \
  -s $MOUNT_FOLDER_PATH
```

> If you work behind proxy, `ads opctl` will **automatically** use your proxy settings (defined via `no_proxy`, `http_proxy` and `https_proxy`).

Note that whenever you change the code, you have to build, tag and push the image to Oracle Cloud Container Registry. This is automatically done with the `ads opctl run` command.

> The python dependencies are set inside the conda environment file. If your code requires additional dependency, update this file:
`oci_dist_training_artifacts/tensorflow/v1/environments.yaml`.
>
> While updating `environments.yaml` do not remove the existing libraries. You can append to the list.

### Define your cluster

To run the distributed training, you have to define your multi-node cluster in your `train.yaml` file.

In the example below, we bring up 1 worker node and 1 chief-worker node. The training code to run is `train.py`. All your training code is assumed to be located inside `/code` directory within the container, which the `ads opctl run` command should do by default.

Additionally, you can also put any data files inside the `/code` directory (and pass on the location ex `'/code/data/**'` as an argument to your training script using the `runtime->spec->args` property as shown below).

Save the following `train.yaml` file in your root project directory, and modify the infrastructure, cluster and runtime section with your settings.

```yaml
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
      displayName: HVD-Distributed-TF
      logGroupId: oci.xxxx.<log_group_ocid>
      subnetId: oci.xxxx.<subnet-ocid>
      shapeName: VM.Standard2.4
      blockStorageSize: 50
  cluster:
    kind: TENSORFLOW
    apiVersion: v1.0
    spec:
      image: "@image"
      workDir:  "oci://<bucket_name>@<bucket_namespace>/<bucket_prefix>"
      name: "tf_multiworker"
      config:
        env:
          - name: WORKER_PORT #Optional. Defaults to 12345
            value: 12345
          - name: SYNC_ARTIFACTS #Mandatory: Switched on by Default.
            value: 1
          - name: WORKSPACE #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket to sync generated artifacts to.
            value: "<bucket_name>"
          - name: WORKSPACE_PREFIX #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket folder to sync generated artifacts to.
            value: "<bucket_prefix>"
      main:
        name: "chief"
        replicas: 1 #this will be always 1.
      worker:
        name: "worker"
        replicas: 1 #number of workers. This is in addition to the 'chief' worker. Could be more than 1
  runtime:
    kind: python
    apiVersion: v1.0
    spec:
      entryPoint: "/code/train.py" #location of user's training script in the container image.
      args:  #any arguments that the training script requires.
          - --data-dir    # assuming data folder has been bundled in the container image.
          - /code/data/
      env:
```

**Note** that you have to setup the `workDir` property to point to your object storage bucket, that will be used to synchronize the cluster. Additionally the `WORKSPACE` and the `WORKSPACE_PREFIX` have to be set as well to point to object storage folder within the `workDir` that will be used to sync the logs. If those folders does not exist, our utility service will create them automatically, as long as the `manage` policy was configured for the job runs resource principal, as shown in the getting started guide.

For `flex shapes` use following in the `train.yaml` file

```yaml
shapeConfigDetails:
    memoryInGBs: 22
    ocpus: 2
shapeName: VM.Standard.E3.Flex
```

**Your project structure should look like this:**

```ini
.
├── oci_dist_training_artifacts
│   ├── tensorflow
│   │   ├── v1
│   │   │   ├── Constants.py
│   │   │   ├── Docker.cpu
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── environments.yaml
│   │   │   ├── local_test.sh
│   │   │   ├── run.py
│   │   │   ├── run.sh
│   │   │   ├── tensorflow_cluster.py
├── train.py
├── mnist.py
├── train.yaml
├── config.ini
├── ...
```

`Notice` that the `config.ini` was automatically generated from the `ads opctl run` command.

### Local Test

Before triggering the distributed job run, you can test your code in the container image and verify the training code, dependencies etc. locally. For this you have following options.

#### a. Test locally with stand-alone run (Recommended)

In order to test the training code locally, use the following command with the `-b local` flag.

```bash
ads opctl run \
        -f train.yaml \
        -b local
```

If your code requires to use any OCI Services also during the local test (like object storage, database, AI Service etc.), you need to mount your OCI API Keys from your local host machine onto the container. This is already done for you automatically, assuming the typical location of the OCI Keys `~/.oci`. You can modify the default behaviour, in-case you have the keys at a different location, by changing the `oci_key_mnt` property in the `config.ini` file.

```ini
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

> The training script location (entrypoint) and associated args will be picked up from the `train.yaml` file.
> For detailed explanation of local run, refer this [distributed training cmd guide](distributed_training_cmd.md)

#### b. Test locally with `docker-compose` (optional)

You can also test locally in a clustered manner using docker-compose. Create `docker-compose.yml` file in your root project folder and copy the following content:

<details>
<summary><b>docker-compose.yml</b> <== click to open</summary>

```yaml
#docker-compose.yaml for distributed tensorflow testing
services:
  chief:
    environment:
      WORKER_PORT: 12345
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: TENSORFLOW
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /code/data/
      OCI__MODE: MAIN
      OCI__WORKER_COUNT: '1'
      OCI__WORK_DIR: /work_dir
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/home/oci_dist_training/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
      - ./:/code
  worker-0:
    environment:
      WORKER_PORT: 23456
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: TENSORFLOW
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /code/data/
      OCI__MODE: WORKER
      OCI__WORKER_COUNT: '1'
      OCI__WORK_DIR: /work_dir
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/home/oci_dist_training/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
      - ./:/code
```

</details>
&nbsp;

Once the `docker-compose.yml` is created, you can start the local cluster by running:

```bash
docker compose up --remove-orphans
```

You can learn more about docker compose [here](https://docs.docker.com/compose/).

>💡Things to keep in mind:
>
>- You can mount your training script directory to `/code` like the above docker-compose (`./:/code`). This way there's no need to build the container image every time you change training script during local development
>- Pass in any parameters that your training script requires in `OCI__ENTRY_SCRIPT_ARGS`.
>- During multiple runs, delete your all mounted folders as appropriate; especially `OCI__WORK_DIR`
>- `OCI__WORK_DIR` can be a location in object storage or a local folder like `OCI__WORK_DIR: /work_dir`.
>- In case you want to use a config_profile other than DEFAULT, please change it in `OCI_CONFIG_PROFILE` env variable.

### Dry Run to Validate the Yaml Definition

To check if your yaml cluster definition was properly set, you can run:

```bash
ads opctl run -f train.yaml --dry-run
```

This will print the Job and Job Run configuration without launching the actual job.

### Start the Distributed Trainig Job

Following will run the distributed training job cluster and also save the output to `info.yaml`. You could use the yaml for checking the runtime details of the cluster.

```bash
ads opctl run -f train.yaml | tee info.yaml
```

### Check the Runtime configuration

```bash
ads opctl distributed-training show-config -f info.yaml
```

### Tail the logs

This command will stream the logs from OCI Logging that you provided while defining the cluster inside `train.yaml` in the example above.

```bash
ads opctl watch <job runid>
```

### Saving Artifacts to Object Storage

To save the artifacts generated by the training process (model checkpoints, TensorBoard logs, etc.) to an object bucket you can use the `'sync'` feature. The environment variable ``OCI__SYNC_DIR`` exposes the directory location that will be automatically synchronized to the configured object storage bucket location. Use this directory in your training script to save the artifacts.

To configure the destination object storage bucket location, use the following settings in the cluster yaml file definition (`train.yaml`).

```yaml
    - name: SYNC_ARTIFACTS
      value: 1
    - name: WORKSPACE
      value: "<bucket_name>"
    - name: WORKSPACE_PREFIX
      value: "<bucket_prefix>"
```

To disable this feature, change `SYNC_ARTIFACTS` to `0`. Use `OCI__SYNC_DIR` environment variable in your code to save the artifacts.

>**Example:**
>`tf.keras.callbacks.ModelCheckpoint(os.path.join(os.environ.get("OCI__SYNC_DIR"),"ckpts",'checkpoint-{epoch}.h5'))`

### Other Tensorflow Strategies Supported

Tensorflow has two multi-worker strategies: `MultiWorkerMirroredStrategy` and `ParameterServerStrategy`. Following shows changes that you would need to do to run `ParameterServerStrategy` workload.

#### a. ParameterServerStrategy

You can have the following training Tensorflow script for `ParameterServerStrategy` saved as `train.py` (just like mnist.py and train.py in case of ```MultiWorkerMirroredStrategy```):

<details>
<summary><b>ParameterServerStrategy train.py</b> <= click to open and copy</summary>

```python
# Script adapted from tensorflow tutorial: https://www.tensorflow.org/tutorials/distribute/parameter_server_training

import os
import tensorflow as tf
import json
import multiprocessing

NUM_PS = len(json.loads(os.environ['TF_CONFIG'])['cluster']['ps'])
global_batch_size = 64


def worker(num_workers, cluster_resolver):
    # Workers need some inter_ops threads to work properly.
    worker_config = tf.compat.v1.ConfigProto()
    if multiprocessing.cpu_count() < num_workers + 1:
        worker_config.inter_op_parallelism_threads = num_workers + 1

    for i in range(num_workers):
        print("cluster_resolver.task_id: ", cluster_resolver.task_id, flush=True)

        s = tf.distribute.Server(
            cluster_resolver.cluster_spec(),
            job_name=cluster_resolver.task_type,
            task_index=cluster_resolver.task_id,
            config=worker_config,
            protocol="grpc")
        s.join()


def ps(num_ps, cluster_resolver):
    print("cluster_resolver.task_id: ", cluster_resolver.task_id, flush=True)
    for i in range(num_ps):
        s = tf.distribute.Server(
            cluster_resolver.cluster_spec(),
            job_name=cluster_resolver.task_type,
            task_index=cluster_resolver.task_id,
            protocol="grpc")
        s.join()


def create_cluster(cluster_resolver, num_workers=1, num_ps=1, mode="worker"):
    os.environ["GRPC_FAIL_FAST"] = "use_caller"

    if mode.lower() == 'worker':
        print("Starting worker server...", flush=True)
        worker(num_workers, cluster_resolver)
    else:
        print("Starting ps server...", flush=True)
        ps(num_ps, cluster_resolver)

    return cluster_resolver, cluster_resolver.cluster_spec()


def decay(epoch):
    if epoch < 3:
        return 1e-3
    elif epoch >= 3 and epoch < 7:
        return 1e-4
    else:
        return 1e-5

def get_callbacks(model):
    class PrintLR(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            print('\nLearning rate for epoch {} is {}'.format(epoch + 1, model.optimizer.lr.numpy()), flush=True)

    callbacks = [
        tf.keras.callbacks.TensorBoard(log_dir='./logs'),
        tf.keras.callbacks.LearningRateScheduler(decay),
        PrintLR()
    ]
    return callbacks

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_artificial_data():
    x = tf.random.uniform((10, 10))
    y = tf.random.uniform((10,))

    dataset = tf.data.Dataset.from_tensor_slices((x, y)).shuffle(10).repeat()
    dataset = dataset.batch(global_batch_size)
    dataset = dataset.prefetch(2)
    return dataset



cluster_resolver = tf.distribute.cluster_resolver.TFConfigClusterResolver()
if not os.environ["OCI__MODE"] == "MAIN":
    create_cluster(cluster_resolver, num_workers=1, num_ps=1, mode=os.environ["OCI__MODE"])
    pass

variable_partitioner = (
    tf.distribute.experimental.partitioners.MinSizePartitioner(
        min_shard_bytes=(256 << 10),
        max_shards=NUM_PS))

strategy = tf.distribute.ParameterServerStrategy(
    cluster_resolver,
    variable_partitioner=variable_partitioner)

dataset = get_artificial_data()

with strategy.scope():
    model = tf.keras.models.Sequential([tf.keras.layers.Dense(10)])
    model.compile(tf.keras.optimizers.SGD(), loss="mse", steps_per_execution=10)

callbacks = get_callbacks(model)
model.fit(dataset, epochs=5, steps_per_epoch=20, callbacks=callbacks)

```

</details>
&nbsp;

#### b. Cluster Yaml Configuration

The only difference here is that the parameter server `train.yaml` also needs to have `ps` worker-pool. This will create dedicated instance(s) for Tensorflow Parameter Server.

Use the following `train.yaml` for ParameterServerStrategy.

<details>
<summary>ParameterServerStrategy <b>train.yaml</b> <= click to open and copy</summary>

```yaml
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
      displayName: Distributed-TF
      logGroupId: oci.xxxx.<log_group_ocid>
      subnetId: oci.xxxx.<subnet-ocid>
      shapeName: VM.Standard2.4
      blockStorageSize: 50
  cluster:
    kind: TENSORFLOW
    apiVersion: v1.0
    spec:
      image: "@image"
      workDir:  "oci://<bucket_name>@<bucket_namespace>/<bucket_prefix>"
      name: "tf_ps"
      config:
        env:
          - name: WORKER_PORT #Optional. Defaults to 12345
            value: 12345
          - name: SYNC_ARTIFACTS #Mandatory: Switched on by Default.
            value: 1
          - name: WORKSPACE #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket to sync generated artifacts to.
            value: "<bucket_name>"
          - name: WORKSPACE_PREFIX #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket folder to sync generated artifacts to.
            value: "<bucket_prefix>"
      main:
        name: "coordinator"
        replicas: 1 #this will be always 1.
      worker:
        name: "worker"
        replicas: 1 #number of workers; any number > 0
      ps:
        name: "ps" # number of parameter servers; any number > 0
        replicas: 1
  runtime:
    kind: python
    apiVersion: v1.0
    spec:
      entryPoint: "/code/train.py" #location of user's training script in the container image.
      args:  #any arguments that the training script requires.
      env:
```

</details>
&nbsp;

For `flex shapes` use following in the `train.yaml` file

```yaml
shapeConfigDetails:
    memoryInGBs: 22
    ocpus: 2
shapeName: VM.Standard.E3.Flex
```

#### c. Test locally with stand-alone run. (Recommended)

For local test use again the `-b local` flag. Further when you need to run this workload on odsc jobs, simply use `-b job` flag instead (default).

```bash
ads opctl run \
        -f train.yaml \
        -b local
```

Again, if your code requires to use any OCI services (like object storage etc.), you need to mount your OCI SDK Keys from your local host machine onto the container. This is already done for you assuming the typical location of oci keys `~/.oci`. You can modify it though, in-case you have keys at a different location. To do so you have to change the location in the `config.ini` file.

```ini
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

#### d. Run the distributed training on Oracle Cloud

When you ready to run this workload on OCI Data Science Jobs, simply use `-b job` flag instead (default).

```bash
ads opctl run \
        -f train.yaml \
        -b job
```

> The training script location (entrypoint) and associated args will be picked up from the runtime `train.yaml`.
> For detailed explanation of local run, Refer this [distributed_training_cmd.md](distributed_training_cmd.md)

#### d. Local Testing using docker-compose

You can also test in a clustered manner using docker-compose. You may use the following docker-compose.yml for running ps workloads locally:

<details>
<summary><b>docker-compose.yml</b> <= click to open and copy</summary>

```yaml
version: "3"
services:
  chief:
    network_mode: "host"
    environment:
      WORKER_PORT: 12344
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: TENSORFLOW
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__MODE: MAIN
      OCI__WORKER_COUNT: '1'
      OCI__PS_COUNT: '1'
      OCI__WORK_DIR: /work_dir
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/home/oci_dist_training/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
  worker-0:
    network_mode: "host"
    environment:
      WORKER_PORT: 12345
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: TENSORFLOW
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__MODE: WORKER
      OCI__WORKER_COUNT: '1'
      OCI__PS_COUNT: '1'
      OCI__SYNC_DIR: /opt/ml
      OCI__WORK_DIR: /work_dir
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/home/oci_dist_training/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
  ps-0:
    network_mode: "host"
    environment:
      WORKER_PORT: 12346
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: TENSORFLOW
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__MODE: PS
      OCI__WORKER_COUNT: '1'
      OCI__PS_COUNT: '1'
      OCI__SYNC_DIR: /opt/ml
      OCI__WORK_DIR: /work_dir
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/home/oci_dist_training/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
```

</details>
&nbsp;

The rest of the steps remain the same and should be followed as it is.

### Profiling

At times, you may want to profile your training setup for optimization/performance tuning. Profiling typically gives a detailed analysis of cpu utilization, gpu utilization, top cuda kernels, top operators etc.

You can choose to profile your training setup using the native Tensorflow profiler or using a third party profiler such as [Nvidia Nsights](https://developer.nvidia.com/nsight-systems).

#### a. Profiling using Tensorflow Profiler

[Tensorflow Profiler](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras) is a native offering from Tensforflow for Tensorflow performance profiling.

Profiling is invoked using code instrumentation using one of the following apis.

1. [```tf.keras.callbacks.TensorBoard```](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras)
2. [```tf.profiler.experimental.Profile```](https://www.tensorflow.org/api_docs/python/tf/profiler/experimental/Profile)

Refer above links for changes that you need to do in your training script for instrumentation.

You should choose the ```OCI__SYNC_DIR``` directory to save the profiling logs. For example:

```python
options = tf.profiler.experimental.ProfilerOptions(
     host_tracer_level=2,
     python_tracer_level=1,
     device_tracer_level=1,
     delay_ms=None)
with tf.profiler.experimental.Profile(os.environ.get("OCI__SYNC_DIR") + "/logs",options=options):
    # training code 
```

In case of keras callback:

```python
tboard_callback = tf.keras.callbacks.TensorBoard(log_dir = os.environ.get("OCI__SYNC_DIR") + "/logs",
                                                 histogram_freq = 1,
                                                 profile_batch = '500,520')
model.fit(...,callbacks = [tboard_callback])
```

Also, the sync feature `SYNC_ARTIFACTS` should be enabled (`'1'`) to sync the profiling logs to the configured object storage bucket. Use Tensorboard to view logs. Refer to [tensorboard.md](tensorboard.md) guide for set-up instructions on your computer.

**The profiling logs are generated per node** and hence you will see logs for each job run. While invoking the tensorboard, point to the parent `<job_id>` directory to view all logs at once.

```bash
export OCIFS_IAM_KEY=api_key \
  tensorboard --logdir oci://my-bucket@my-namespace/path_to_job_id
```

#### b. Profiling using Nvidia Nsights

[Nvidia Nsights](https://developer.nvidia.com/nsight-systems) is a system wide profiling tool from Nvidia that can be used to profile Deep Learning workloads.

Nsights requires no change in your training code. This works on process level. You can enable this **experimental** feature in your training setup via the following configuration in the runtime yaml file.

<pre>
    spec:
      image: "@image"
      workDir:  "oci://<bucket_name>@<bucket_namespace>/<bucket_prefix>"
      name: "tf_multiworker"
      config:
        env:
          - name: WORKER_PORT #Optional. Defaults to 12345
            value: 12345
          - name: SYNC_ARTIFACTS #Mandatory: Switched on by Default.
            value: 1
          - name: WORKSPACE #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket to sync generated artifacts to.
            value: "<bucket_name>"
          - name: WORKSPACE_PREFIX #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket folder to sync generated artifacts to.
            value: "<bucket_prefix>"
          <b>- name: PROFILE #0: Off 1: On
            value: 1
          - name: PROFILE_CMD
            value: "nsys profile -w true -t cuda,nvtx,osrt,cudnn,cublas -s none -o /opt/ml/nsight_report -x true"  </b>
      main:
        name: "chief"
        replicas: 1 #this will be always 1.
      worker:
        name: "worker"
        replicas: 1 #number of workers. This is in addition to the 'chief' worker. Could be more than 1
</pre>

Refer [here](https://docs.nvidia.com/nsight-systems/UserGuide/index.html#cli-profile-command-switch-options) for `nsys profile` command options. You can modify the command within the `PROFILE_CMD` but remember this is all experimental. The profiling reports are generated per node. You need to download the reports to your computer manually or via the oci
command.

```bash
oci os object bulk-download \
  -ns <namespace> \
  -bn <bucket_name> \
  --download-dir /path/on/your/computer \
  --prefix path/on/bucket/<job_id>
```

To view the reports, you would need to install Nsight Systems app from [here](https://developer.nvidia.com/nsight-systems), then open the downloaded reports in the Nsight Systems application.

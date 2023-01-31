# Developer Guide

This instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework pytorch`.

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

## Steps to run PyTorch Distributed Data-Parallel Training

All the docker image related artifacts are located under `oci_dist_training_artifacts/pytorch/v1/`. For your reference, this guide assumes the following directory structure:

```ini
.
├── oci_dist_training_artifacts
│   ├── pytorch
│   │   ├── v1
│   │   │   ├── Dockerfile
│   │   │   ├── environment.yaml
│   │   │   ├── pytorch_cluster.py
│   │   │   ├── README.md
│   │   │   ├── run.py
│   │   │   ├── run.sh
├── train.py
├── train.yaml
├── ...
```

### Prerequisite

You need to install [ads](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html#) to run this guide.

```bash
python3 -m pip install oracle-ads[opctl]
```

This guide uses ```ads opctl``` for creating distributed training jobs. Refer [distributed_training_cmd.md](distributed_training_cmd.md) for supported commands and options for distributed training.

### 1. Prepare Docker Image

All files in the current directory will be copied over to `/code` folder inside docker image.

For example, you can have the following training script saved as `train.py`:

<details>
<summary>pytorch <b>train.py</b> <== click to open</summary>

```python
#
# Script adapted from:
# https://github.com/Azure/azureml-examples/blob/main/python-sdk/workflows/train/pytorch/cifar-distributed/src/train.py
# ==============================================================================

import datetime
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os, argparse

# define network architecture

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.conv3 = nn.Conv2d(64, 128, 3)
        self.fc1 = nn.Linear(128 *6* 6, 120)
        self.dropout = nn.Dropout(p=0.2)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 6 * 6)
        x = self.dropout(F.relu(self.fc1(x)))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# define functions

def train(train_loader, model, criterion, optimizer, epoch, device, print_freq, rank):
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data[0].to(device), data[1].to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % print_freq == 0:  # print every print_freq mini-batches
            print(
                "Rank %d: [%d, %5d] loss: %.3f"
                % (rank, epoch + 1, i + 1, running_loss / print_freq)
            )
            running_loss = 0.0

def evaluate(test_loader, model, device):
    classes = (
        "plane",
        "car",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    )

    model.eval()

    correct = 0
    total = 0
    class_correct = list(0.0 for i in range(10))
    class_total = list(0.0 for i in range(10))
    with torch.no_grad():
        for data in test_loader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            c = (predicted == labels).squeeze()
            for i in range(10):
                label = labels[i]
                class_correct[label] += c[i].item()
                class_total[label] += 1

    # print total test set accuracy
    print(
        "Accuracy of the network on the 10000 test images: %d %%"
        % (100 * correct / total)
    )

    # print test accuracy for each of the classes
    for i in range(10):
        print(
            "Accuracy of %5s : %2d %%"
            % (classes[i], 100 * class_correct[i] / class_total[i])
        )

def main(args):
    # get PyTorch environment variables
    world_size = int(os.environ["WORLD_SIZE"])
    rank = int(os.environ["RANK"])
    local_rank = int(os.environ["LOCAL_RANK"])

    distributed = world_size > 1

    if torch.cuda.is_available():
        print("CUDA is available.")
    else:
        print("CUDA is not available.")

    # set device
    if distributed:
        if torch.cuda.is_available():
            device = torch.device("cuda", local_rank)
        else:
            device = torch.device("cpu")
    else:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # initialize distributed process group using default env:// method
    if distributed:
        torch.distributed.init_process_group(
            backend=args.backend,
            timeout=datetime.timedelta(minutes=args.timeout)
        )

    # define train and test dataset DataLoaders
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    train_set = torchvision.datasets.CIFAR10(
        root=args.data_dir, train=True, download=True, transform=transform
    )

    if distributed:
        train_sampler = torch.utils.data.distributed.DistributedSampler(train_set)
    else:
        train_sampler = None

    train_loader = torch.utils.data.DataLoader(
        train_set,
        batch_size=args.batch_size,
        shuffle=(train_sampler is None),
        num_workers=args.workers,
        sampler=train_sampler,
    )

    test_set = torchvision.datasets.CIFAR10(
        root=args.data_dir, train=False, download=True, transform=transform
    )
    test_loader = torch.utils.data.DataLoader(
        test_set, batch_size=args.batch_size, shuffle=False, num_workers=args.workers
    )

    model = Net().to(device)

    # wrap model with DDP
    if distributed:
        if torch.cuda.is_available():
            model = nn.parallel.DistributedDataParallel(
                model, device_ids=[local_rank], output_device=local_rank
            )
        else:
            model = nn.parallel.DistributedDataParallel(model)

    # define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(
        model.parameters(), lr=args.learning_rate, momentum=args.momentum
    )

    # train the model
    for epoch in range(args.epochs):
        print("Rank %d: Starting epoch %d" % (rank, epoch))
        if distributed:
            train_sampler.set_epoch(epoch)
        model.train()
        train(
            train_loader,
            model,
            criterion,
            optimizer,
            epoch,
            device,
            args.print_freq,
            rank,
        )

    print("Rank %d: Finished Training" % (rank))

    if not distributed or rank == 0:
        os.makedirs(args.output_dir, exist_ok=True)
        model_path = os.path.join(args.output_dir, "cifar_net.pt")
        torch.save(model.state_dict(), model_path)

        # evaluate on full test dataset
        evaluate(test_loader, model, device)

# run script

if __name__ == "__main__":
    # setup argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir", type=str, help="directory containing CIFAR-10 dataset"
    )
    parser.add_argument("--epochs", default=10, type=int, help="number of epochs")
    parser.add_argument(
        "--batch-size",
        default=16,
        type=int,
        help="mini batch size for each gpu/process",
    )
    parser.add_argument(
        "--workers",
        default=2,
        type=int,
        help="number of data loading workers for each gpu/process",
    )
    parser.add_argument(
        "--learning-rate", default=0.001, type=float, help="learning rate"
    )
    parser.add_argument("--momentum", default=0.9, type=float, help="momentum")
    parser.add_argument(
        "--output-dir", default="outputs", type=str, help="directory to save model to"
    )
    parser.add_argument(
        "--print-freq",
        default=200,
        type=int,
        help="frequency of printing training statistics",
    )
    parser.add_argument(
        "--backend", default="gloo", type=str,
        help="distributed communication backend, should be gloo, nccl or mpi"
    )
    parser.add_argument(
        "--timeout", default=30, type=int,
        help="timeout in minutes for waiting for the initialization of distributed process group."
    )
    args = parser.parse_args()

    # call main function
    main(args)
```

</details>
&nbsp;

**Note**: Whenever you change the code, you have to build, tag and push the image to OCI container registry. This is automatically taken care in ```ads opctl run``` cli command.

The required python dependencies are provided inside `oci_dist_training_artifacts/pytorch/v1/environment.yaml`.  If you code required additional dependencies, please add them to the `environment.yaml` file.

Also, while updating `environment.yaml` do not remove the existing libraries.

Set the TAG and the IMAGE_NAME as per your needs. `IMAGE_NAME` refers to your Oracle Cloud Container Registry you created in the [Getting Stared Guide](README.md). `MOUNT_FOLDER_PATH` is the root directory of your project code, but you can use `.` in case you executed all of the `ads opctl run` commands directly from your root project folder.

```bash
export IMAGE_NAME=<region>.ocir.io/<namespace>/<repository-name>
export TAG=latest
export MOUNT_FOLDER_PATH=.
```

**Replace** the `<region>` with the name of the region where you created your repository and you will run your code, for example `iad` for Ashburn. **Replace** the `<namespace>` with the namespace you see in your Oracle Cloud Container Registry, when you created your repository. **Replace** the `<repository-name>` with the name of the repository you used to create it.

Build the docker image.

```bash
ads opctl distributed-training build-image \
  -t $TAG \
  -reg $IMAGE_NAME \
  -df oci_dist_training_artifacts/pytorch/v1/Dockerfile \
  -s $MOUNT_FOLDER_PATH
```

If you are behind proxy, ads opctl will automatically use your proxy settings( defined via ```no_proxy```, ```http_proxy``` and ```https_proxy```).

### 2. Create yaml file to define your cluster

Cluster is specified using a yaml file. Below is an example to bring up 1 master node and 2 worker nodes for training. The code to run is stored in `train.py`. All code is assumed to be present inside `/code` directory within the container.

Please refer to the [documentation](http://10.209.39.50:8000/user_guide/model_training/distributed_training/dask/creating.html) for more details.

```yaml
# Example train.yaml
kind: distributed
apiVersion: v1.0
spec:
  name: PyTorch-Distributed
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
      shapeName: VM.GPU2.1
      blockStorageSize: 50
  cluster:
    kind: PYTORCH
    apiVersion: v1.0
    spec:
      image: "@image"
      workDir: "oci://my-bucket@my-namespace/path/to/dir/"
      config:
        env:
          - name: NCCL_ASYNC_ERROR_HANDLING
            value: '1'
      main:
        name: PyTorch-Distributed-main
        replicas: 1
      worker:
        name: PyTorch-Distributed-worker
        replicas: 2
  runtime:
    kind: python
    apiVersion: v1.0
    spec:
      entryPoint: "/code/train.py"
      args:
        - --data-dir
        - /home/datascience/data
        - --output-dir
        - /home/datascience/outputs
        - --timeout
        - 5

```

**Note**: Change the `workDir` to point to the object storage bucket at OCI.

For `flex shapes` use following in the `train.yaml` file

```yaml
shapeConfigDetails:
    memoryInGBs: 22
    ocpus: 2
shapeName: VM.Standard.E3.Flex
```

### 3. Local Testing

Before triggering the job run, you can test the docker image and verify the training code, dependencies etc.

#### 3a. Test locally with stand-alone run. (Recommended)

In order to test the training code locally, use the following command. With ```-b local``` flag, it uses a local backend. Further when you need to run this workload on odsc jobs, simply use ```-b job```
flag instead (default).

```bash
ads opctl run \
  -f train.yaml
  -b local
```

If your code requires to use any oci services (like object bucket), you need to mount oci keys from your local host machine onto the docker container. This is already done for you assuming
the typical location of oci keys ```~/.oci```. You can modify it though, in-case you have keys at a different location. You need to do this in the ```config.ini``` file.

```ini
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

Note: The training script location(entrypoint) and associated args will be picked up from the runtime ```train.yaml```.
**Note**:

For detailed explanation of local run, Refer this [distributed_training_cmd.md](distributed_training_cmd.md)

You can also test in a clustered manner using docker-compose. Next section.

#### 3b. Test locally with `docker-compose` based cluster

Create a `docker-compose.yaml` file and copy the following content.

<details>
<summary><b>docker-compose.yaml</b> <== click to open</summary>

```yaml
services:
  PyTorch-Distributed-main:
    environment:
      NCCL_ASYNC_ERROR_HANDLING: '1'
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: PYTORCH
      OCI__ENTRY_SCRIPT: train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /home/datascience/data --output-dir /home/datascience/outputs
        --timeout 5
      OCI__EPHEMERAL: 1
      OCI__MODE: MAIN
      OCI__START_ARGS: ''
      OCI__WORKER_COUNT: '2'
      OCI__WORK_DIR: $WORK_DIR
      RANK: '0'
      SHAPE: VM.GPU2.1
    image: $IMAGE_NAME:$TAG
    network_mode: host
    volumes:
    - ~/.oci:/home/datascience/.oci
    - ~/.oci:/root/.oci
    - ./work_dir:/work_dir
    - ./artifacts:/opt/ml
    ports:
      - "30000:29400"
  PyTorch-Distributed-worker-0:
    environment:
      NCCL_ASYNC_ERROR_HANDLING: '1'
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: PYTORCH
      OCI__ENTRY_SCRIPT: train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /home/datascience/data --output-dir /home/datascience/outputs
        --timeout 5
      OCI__EPHEMERAL: 1
      OCI__MODE: WORKER
      OCI__START_ARGS: ''
      OCI__WORKER_COUNT: '2'
      OCI__WORK_DIR: $WORK_DIR
      RANK: '1'
      SHAPE: VM.GPU2.1
    image: $IMAGE_NAME:$TAG
    network_mode: host
    volumes:
    - ~/.oci:/home/datascience/.oci
    - ~/.oci:/root/.oci
    - ./work_dir:/work_dir
    - ./artifacts:/opt/ml
    ports:
      - "30001:29400"
  PyTorch-Distributed-worker-1:
    environment:
      NCCL_ASYNC_ERROR_HANDLING: '1'
      OCI_IAM_TYPE: api_key
      OCI__CLUSTER_TYPE: PYTORCH
      OCI__ENTRY_SCRIPT: train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /home/datascience/data --output-dir /home/datascience/outputs
        --timeout 5
      OCI__EPHEMERAL: 1
      OCI__MODE: WORKER
      OCI__START_ARGS: ''
      OCI__WORKER_COUNT: '2'
      OCI__WORK_DIR: $WORK_DIR
      RANK: '2'
      SHAPE: VM.GPU2.1
    image: $IMAGE_NAME:$TAG
    network_mode: host
    volumes:
    - ~/.oci:/home/datascience/.oci
    - ~/.oci:/root/.oci
    - ./work_dir:/work_dir
    - ./artifacts:/opt/ml
    ports:
      - "30002:29400"
```

</details>
&nbsp;

This example `docker-compose.yaml` assumes that you have OCI API key and config stored at `~/.oci`. The default profile is used for authentication.

Set an object storage path as environment variable for `OCI__WORK_DIR` -

```bash
export WORK_DIR=oci://<my-bucket>@<my-tenancy>/prefix
```

Once the `docker-compose.yaml` is created, you can start the containers by running -

```bash
docker compose up
```

You can learn more about docker compose [here](https://docs.docker.com/compose/)

### 4. Dry Run to validate the Yaml definition

The following command will print the Job and Job run configuration without launching the actual job.

```bash
ads opctl run -f train.yaml --dry-run
```

### 5. Start Distributed Job

The following command will start the training and also save the output to `info.yaml`. You could use this yaml for checking the runtime details of the cluster.

```bash
ads opctl run -f train.yaml | tee info.yaml
```

### 6. Tail the logs

This command will stream the log from logging infrastructure that you provided while defining the cluster inside `train.yaml` in the example above.

```bash
ads opctl watch <job runid>
```

### 7. Check runtime configuration

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
model_path = os.path.join(os.environ.get("OCI__SYNC_DIR"),"model.pt")
torch.save(model, model_path)
```

### 9. Profiling

At times, you may want to profile your training setup for optimization/performance tuning. Profiling typically gives a detailed analysis of cpu utilization, gpu utilization, top cuda kernels, top operators etc. You can choose to profile your training setup using the native Pytorch profiler or using a third party profiler such as [Nvidia Nsights](https://developer.nvidia.com/nsight-systems).

#### 9a. Profiling using Pytorch Profiler

[Pytorch Profiler](https://pytorch.org/docs/stable/profiler.html) is a native offering from Pytorch for Pytorch performance profiling.
Profiling is invoked using code instrumentation using the following api.
 [```torch.profiler.profile```](https://pytorch.org/docs/stable/profiler.html#torch.profiler.profile)

Refer the above link for changes that you need to do in your training script for instrumentation.

You should choose the ```OCI__SYNC_DIR``` directory to save the profiling logs. For example:

```python
prof = torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,torch.profiler.ProfilerActivity.CUDA],
        schedule=torch.profiler.schedule(
            wait=1,
            warmup=1,
            active=3,
            repeat=1),
        on_trace_ready=torch.profiler.tensorboard_trace_handler(os.environ.get("OCI__SYNC_DIR") + "/logs"),
        with_stack=False)
prof.start()

# training code
prof.end()
```

Also, the sync feature `SYNC_ARTIFACTS` should be enabled ('1') to sync the profiling logs to the configured object storage.

Thereafter, use Tensorboard to view logs. Refer this [tensorboard.md](tensorboard.md) for set-up on your computer.

On top of this you would need to install the [Pytorch Tensorboard Plugin](https://github.com/pytorch/kineto/tree/main/tb_plugin).

``
pip install torch-tb-profiler
``

**The profiling logs are generated per node** and hence you will see logs for each job run. While invoking the tensorboard, point to the parent `<job_id>` directory to view all logs at once.

```bash
export OCIFS_IAM_KEY=api_key tensorboard --logdir oci://my-bucket@my-namespace/path_to_job_id
```

#### 9b. Profiling using Nvidia Nsights

[Nvidia Nsights](https://developer.nvidia.com/nsight-systems) is a system wide profiling tool from Nvidia that can be used to profile Deep Learning workloads.

Nsights requires no change in your training code. This works on process level. You can enable this **experimental** feature (highlighted in bold) in your training setup via the following configuration in the
runtime yaml file.

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

To view the reports, you would need to install Nsight Systems app from [here](https://developer.nvidia.com/nsight-systems). Thereafter, open the downloaded reports in the Nsight Systems app.

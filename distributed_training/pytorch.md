# Developer Guide

This instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework pytorch`.

## Steps to run PyTorch Distributed Data-Parallel Training

All the docker image related artifacts are located under `oci_dist_training_artifacts/pytorch/v1/`. For your reference, this guide assumes the following directory structure:
```
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


### 1. Prepare Docker Image

All files in the current directory will be copied over to `/code` folder inside docker image.

For example, you can have the following training script saved as `train.py`:

```

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
        self.fc1 = nn.Linear(128 * 6 * 6, 120)
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

**Note**: Whenever you change the code, you have to build, tag and push the image to OCI container registry. If you change the tag, it needs to be updated inside the cluster definition yaml.

The required python dependencies are provided inside `oci_dist_training_artifacts/pytorch/v1/environment.yaml`.  If you code required additional dependencies, please add them to the `environment.yaml` file. 

**Note**: While updating `environment.yaml` do not remove the existing libraries.

Set the TAG and IMAGE_NAME as environment variables based on your needs -
```
export IMAGE_NAME=<region.ocir.io/my-tenancy/image-name>
export TAG=latest
```

Build the docker image -
```
docker build -t $IMAGE_NAME:$TAG \
    -f oci_dist_training_artifacts/pytorch/v1/Dockerfile .

```

If you are behind proxy, use this command - 

```
docker build  --build-arg no_proxy=$no_proxy \
              --build-arg http_proxy=$http_proxy \
              --build-arg https_proxy=$http_proxy \
              -t $IMAGE_NAME:$TAG \
              -f oci_dist_training_artifacts/pytorch/v1/Dockerfile .
```

Push the docker image - 
```
docker push $IMAGE_NAME:$TAG
```

### 2. Test locally with help of `docker-compose`

Create a `docker-compose.yaml` file and copy the following content.
```
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

This example `docker-compose.yaml` assumes that you have OCI API key and config stored at `~/.oci`. The default profile is used for authentication.

Set an object storage path as environment variable for `OCI__WORK_DIR` -
```
export WORK_DIR=oci://<my-bucket>@<my-tenancy>/prefix
```

Once the `docker-compose.yaml` is created, you can start the containers by running - 
```
docker compose up
```

You can learn more about docker compose [here](https://docs.docker.com/compose/)

### 3. Create yaml file to define your cluster. 

Cluster is specified using a yaml file. Below is an example to bring up 1 master node and 2 worker nodes for training. The code to run is stored in `train.py`. All code is assumed to be present inside `/code` directory within the container.

Please refer to the [documentation](http://10.209.39.50:8000/user_guide/model_training/distributed_training/dask/creating.html) for more details.

```
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
      image: <region.ocir.io/my-tenancy/image-name>
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
      entryPoint: "train.py"
      args:
        - --data-dir
        - /home/datascience/data
        - --output-dir
        - /home/datascience/outputs
        - --timeout
        - 5

```

### 4. Dry Run to validate the Yaml definition

The following command will print the Job and Job run configuration without launching the actual job.
```
ads opctl run -f train.yaml --dry-run
```

### 5. Start Distributed Job

The following command will start the training and also save the output to `info.yaml`. You could use this yaml for checking the runtime details of the cluster.

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
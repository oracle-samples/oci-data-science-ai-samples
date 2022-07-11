# Developer Guide

## Steps to run Distributed Horovod

All the docker image related artifacts are located under - `oci_dist_training_artifacts/horovod/v1/`


### 1. Prepare Docker Image
Horovod provides support for Pytorch and Tensorflow. Within these frameworks, there are two separate docker files, for cpu and gpu.
Choose the docker file and conda environment files based on whether you are going to use Pytorch or Tensorflow with either cpu or gpu.

The instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework horovod-<pytorch|tensorflow>`

All files in the current directory is copied over to `/code` folder inside docker image.

For example, you can have the following training Tensorflow script saved as `train.py`:

```
# Script adapted from https://github.com/horovod/horovod/blob/master/examples/elastic/tensorflow2/tensorflow2_keras_mnist_elastic.py

# ==============================================================================


import argparse
import tensorflow as tf
import horovod.tensorflow.keras as hvd
from distutils.version import LooseVersion

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

parser = argparse.ArgumentParser(description="Tensorflow 2.0 Keras MNIST Example")

parser.add_argument(
    "--use-mixed-precision",
    action="store_true",
    default=False,
    help="use mixed precision for training",
)

parser.add_argument(
    "--data-dir",
    help="location of the training dataset in the local filesystem (will be downloaded if needed)",
    default='/code/data/mnist.npz'
)

args = parser.parse_args()

if args.use_mixed_precision:
    print(f"using mixed precision {args.use_mixed_precision}")
    if LooseVersion(tf.__version__) >= LooseVersion("2.4.0"):
        from tensorflow.keras import mixed_precision

        mixed_precision.set_global_policy("mixed_float16")
    else:
        policy = tf.keras.mixed_precision.experimental.Policy("mixed_float16")
        tf.keras.mixed_precision.experimental.set_policy(policy)

# Horovod: initialize Horovod.
hvd.init()

# Horovod: pin GPU to be used to process local rank (one GPU per process)
gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
if gpus:
    tf.config.experimental.set_visible_devices(gpus[hvd.local_rank()], "GPU")

import numpy as np

minist_local = args.data_dir


def load_data():
    print("using pre-fetched dataset")
    with np.load(minist_local, allow_pickle=True) as f:
        x_train, y_train = f["x_train"], f["y_train"]
        x_test, y_test = f["x_test"], f["y_test"]
        return (x_train, y_train), (x_test, y_test)


(mnist_images, mnist_labels), _ = (
    load_data()
    if os.path.exists(minist_local)
    else tf.keras.datasets.mnist.load_data(path="mnist-%d.npz" % hvd.rank())
)


dataset = tf.data.Dataset.from_tensor_slices(
    (
        tf.cast(mnist_images[..., tf.newaxis] / 255.0, tf.float32),
        tf.cast(mnist_labels, tf.int64),
    )
)
dataset = dataset.repeat().shuffle(10000).batch(128)

model = tf.keras.Sequential(
    [
        tf.keras.layers.Conv2D(32, [3, 3], activation="relu"),
        tf.keras.layers.Conv2D(64, [3, 3], activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation="softmax"),
    ]
)

# Horovod: adjust learning rate based on number of GPUs.
scaled_lr = 0.001 * hvd.size()
opt = tf.optimizers.Adam(scaled_lr)

# Horovod: add Horovod DistributedOptimizer.
opt = hvd.DistributedOptimizer(
    opt, backward_passes_per_step=1, average_aggregated_gradients=True
)

# Horovod: Specify `experimental_run_tf_function=False` to ensure TensorFlow
# uses hvd.DistributedOptimizer() to compute gradients.
model.compile(
    loss=tf.losses.SparseCategoricalCrossentropy(),
    optimizer=opt,
    metrics=["accuracy"],
    experimental_run_tf_function=False,
)

# Horovod: initialize optimizer state so we can synchronize across workers
# Keras has empty optimizer variables() for TF2:
# https://sourcegraph.com/github.com/tensorflow/tensorflow@v2.4.1/-/blob/tensorflow/python/keras/optimizer_v2/optimizer_v2.py#L351:10
model.fit(dataset, steps_per_epoch=1, epochs=1, callbacks=None)

state = hvd.elastic.KerasState(model, batch=0, epoch=0)


def on_state_reset():
    tf.keras.backend.set_value(state.model.optimizer.lr, 0.001 * hvd.size())
    # Re-initialize, to join with possible new ranks
    state.model.fit(dataset, steps_per_epoch=1, epochs=1, callbacks=None)


state.register_reset_callbacks([on_state_reset])

callbacks = [
    hvd.callbacks.MetricAverageCallback(),
    hvd.elastic.UpdateEpochStateCallback(state),
    hvd.elastic.UpdateBatchStateCallback(state),
    hvd.elastic.CommitStateCallback(state),
]

# Horovod: save checkpoints only on worker 0 to prevent other workers from corrupting them.
# save the artifacts in the OCI__SYNC_DIR dir.
artifacts_dir = os.environ.get("OCI__SYNC_DIR") + "/artifacts"
tb_logs_path = os.path.join(artifacts_dir, "logs")
check_point_path = os.path.join(artifacts_dir, "ckpts", "checkpoint-{epoch}.h5")
if hvd.rank() == 0:
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(check_point_path))
    callbacks.append(tf.keras.callbacks.TensorBoard(tb_logs_path))

# Train the model.
# Horovod: adjust number of steps based on number of GPUs.
@hvd.elastic.run
def train(state):
    state.model.fit(
        dataset,
        steps_per_epoch=500 // hvd.size(),
        epochs=2 - state.epoch,
        callbacks=callbacks,
        verbose=1,
    )


train(state)
```

If you are creating a Pytorch based workload, here is an example that you can save as `train.py`.

```
# Script adapted from https://github.com/horovod/horovod/blob/master/examples/elastic/pytorch/pytorch_mnist_elastic.py

# ==============================================================================
import argparse
import os
from filelock import FileLock

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import torch.utils.data.distributed
import horovod.torch as hvd
from torch.utils.tensorboard import SummaryWriter

# Training settings
parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                    help='input batch size for training (default: 64)')
parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                    help='input batch size for testing (default: 1000)')
parser.add_argument('--epochs', type=int, default=10, metavar='N',
                    help='number of epochs to train (default: 10)')
parser.add_argument('--lr', type=float, default=0.01, metavar='LR',
                    help='learning rate (default: 0.01)')
parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                    help='SGD momentum (default: 0.5)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='disables CUDA training')
parser.add_argument('--seed', type=int, default=42, metavar='S',
                    help='random seed (default: 42)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--fp16-allreduce', action='store_true', default=False,
                    help='use fp16 compression during allreduce')
parser.add_argument('--use-adasum', action='store_true', default=False,
                    help='use adasum algorithm to do reduction')
parser.add_argument('--data-dir',
                    help='location of the training dataset in the local filesystem (will be downloaded if needed)')

args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

checkpoint_format = 'checkpoint-{epoch}.pth.tar'

# Horovod: initialize library.
hvd.init()
torch.manual_seed(args.seed)

if args.cuda:
    # Horovod: pin GPU to local rank.
    torch.cuda.set_device(hvd.local_rank())
    torch.cuda.manual_seed(args.seed)


# Horovod: limit # of CPU threads to be used per worker.
torch.set_num_threads(1)

kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
data_dir = args.data_dir or './data'
with FileLock(os.path.expanduser("~/.horovod_lock")):
    train_dataset = \
        datasets.MNIST(data_dir, train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ]))
# Horovod: use DistributedSampler to partition the training data.
train_sampler = torch.utils.data.distributed.DistributedSampler(
    train_dataset, num_replicas=hvd.size(), rank=hvd.rank())
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=args.batch_size, sampler=train_sampler, **kwargs)

test_dataset = \
    datasets.MNIST(data_dir, train=False, transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ]))
# Horovod: use DistributedSampler to partition the test data.
test_sampler = torch.utils.data.distributed.DistributedSampler(
    test_dataset, num_replicas=hvd.size(), rank=hvd.rank())
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=args.test_batch_size,
                                          sampler=test_sampler, **kwargs)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)


model = Net()

# By default, Adasum doesn't need scaling up learning rate.
lr_scaler = hvd.size() if not args.use_adasum else 1

if args.cuda:
    # Move model to GPU.
    model.cuda()
    # If using GPU Adasum allreduce, scale learning rate by local_size.
    if args.use_adasum and hvd.nccl_built():
        lr_scaler = hvd.local_size()

# Horovod: scale learning rate by lr_scaler.
optimizer = optim.SGD(model.parameters(), lr=args.lr * lr_scaler,
                      momentum=args.momentum)

# Horovod: (optional) compression algorithm.
compression = hvd.Compression.fp16 if args.fp16_allreduce else hvd.Compression.none


def metric_average(val, name):
    tensor = torch.tensor(val)
    avg_tensor = hvd.allreduce(tensor, name=name)
    return avg_tensor.item()

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
# Horovod: average metrics from distributed training.
class Metric(object):
    def __init__(self, name):
        self.name = name
        self.sum = torch.tensor(0.)
        self.n = torch.tensor(0.)

    def update(self, val):
        self.sum += hvd.allreduce(val.detach().cpu(), name=self.name)
        self.n += 1

    @property
    def avg(self):
        return self.sum / self.n

@hvd.elastic.run
def train(state):
    # post synchronization event (worker added, worker removed) init ...

    artifacts_dir = os.environ.get("OCI__SYNC_DIR") + "/artifacts"
    chkpts_dir = os.path.join(artifacts_dir,"ckpts")
    logs_dir = os.path.join(artifacts_dir,"logs")
    if hvd.rank() == 0:
        print("creating dirs for checkpoints and logs")
        create_dir(chkpts_dir)
        create_dir(logs_dir)

    writer = SummaryWriter(logs_dir) if hvd.rank() == 0 else None

    for state.epoch in range(state.epoch, args.epochs + 1):
        train_loss = Metric('train_loss')
        state.model.train()

        train_sampler.set_epoch(state.epoch)
        steps_remaining = len(train_loader) - state.batch

        for state.batch, (data, target) in enumerate(train_loader):
            if state.batch >= steps_remaining:
                break

            if args.cuda:
                data, target = data.cuda(), target.cuda()
            state.optimizer.zero_grad()
            output = state.model(data)
            loss = F.nll_loss(output, target)
            train_loss.update(loss)
            loss.backward()
            state.optimizer.step()
            if state.batch % args.log_interval == 0:
                # Horovod: use train_sampler to determine the number of examples in
                # this worker's partition.
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    state.epoch, state.batch * len(data), len(train_sampler),
                    100.0 * state.batch / len(train_loader), loss.item()))
            state.commit()
        if writer:
           writer.add_scalar("Loss", train_loss.avg, state.epoch)
        if hvd.rank() == 0:
            chkpt_path = os.path.join(chkpts_dir,checkpoint_format.format(epoch=state.epoch + 1))
            chkpt = {
                'model': state.model.state_dict(),
                'optimizer': state.optimizer.state_dict(),
            }
            torch.save(chkpt, chkpt_path)
        state.batch = 0


def test():
    model.eval()
    test_loss = 0.
    test_accuracy = 0.
    for data, target in test_loader:
        if args.cuda:
            data, target = data.cuda(), target.cuda()
        output = model(data)
        # sum up batch loss
        test_loss += F.nll_loss(output, target, size_average=False).item()
        # get the index of the max log-probability
        pred = output.data.max(1, keepdim=True)[1]
        test_accuracy += pred.eq(target.data.view_as(pred)).cpu().float().sum()

    # Horovod: use test_sampler to determine the number of examples in
    # this worker's partition.
    test_loss /= len(test_sampler)
    test_accuracy /= len(test_sampler)

    # Horovod: average metric values across workers.
    test_loss = metric_average(test_loss, 'avg_loss')
    test_accuracy = metric_average(test_accuracy, 'avg_accuracy')

    # Horovod: print output only on first rank.
    if hvd.rank() == 0:
        print('\nTest set: Average loss: {:.4f}, Accuracy: {:.2f}%\n'.format(
            test_loss, 100. * test_accuracy))


# Horovod: wrap optimizer with DistributedOptimizer.
optimizer = hvd.DistributedOptimizer(optimizer,
                                     named_parameters=model.named_parameters(),
                                     compression=compression,
                                     op=hvd.Adasum if args.use_adasum else hvd.Average)


# adjust learning rate on reset
def on_state_reset():
    for param_group in optimizer.param_groups:
        param_group['lr'] = args.lr * hvd.size()


state = hvd.elastic.TorchState(model, optimizer, epoch=1, batch=0)
state.register_reset_callbacks([on_state_reset])
train(state)
test()
```


**Note**: Whenever you change the code, you have to build, tag and push the image to repo. If you change the tag, it needs to be updated inside the cluster definition yaml.

The required python dependencies are provided inside the conda environment file `oci_dist_training_artifacts/horovod/v1/conda-<pytorch|tensorflow>-<cpu|gpu>.yaml`.  If your code requires additional dependency, update this file. 

**Note**: While updating `conda-<pytorch|tensorflow>-<cpu|gpu>.yaml` do not remove the existing libraries. You can append to the list.

Building docker image - 

Update the TAG and the IMAGE_NAME as per your needs - 

```
export IMAGE_NAME=<region.ocir.io/my-tenancy/image-name>
export TAG=latest
```

```
docker build -t $IMAGE_NAME:$TAG \
    -f oci_dist_training_artifacts/horovod/v1/<pytorch|tensorflow>.<cpu|gpu>.Dockerfile .

```

If you are behind proxy, use this command - 

```
docker build  --build-arg no_proxy=$no_proxy \
              --build-arg http_proxy=$http_proxy \
              --build-arg https_proxy=$http_proxy \
              -t $IMAGE_NAME:$TAG \
              -f oci_dist_training_artifacts/horovod/v1/<pytorch|tensorflow>.<cpu|gpu>.Dockerfile .
```

Push the docker image - 

```
docker push $IMAGE_NAME:$TAG
```

#### 2a. Test locally with stand-alone docker run.

Before triggering the job run, you can test the docker image and verify the training code,
 dependencies etc. You can do this using a local stand-alone docker run or via a docker-compose setup(section 2b)

For a stand-alone docker run, start a docker container with ```bash``` entrypoint.

```
docker run --rm -it --entrypoint bash $IMAGE_NAME:$TAG
```
Optionally, you can choose to mount oci keys and code directory to the docker container.  

```
docker run --rm -it -v $HOME/.oci:/root/.oci -v $PWD:/code --entrypoint bash $IMAGE_NAME:$TAG
```

You have now a docker container and you are logged into it. Now test your training script with the following command.

```
horovodrun -np 2 -H localhost:2 python /code/train.py
```
**Note** Pass on any args that your training script requires using the ```--``` flag. For example:

```
horovodrun -np 2 -H localhost:2 python /code/train.py --data-dir /code/data/mnist.npz
```

Once done, exit the container with the exit command.

```
exit
```

You can also test in a clustered manner using docker-compose. Next section.

#### 2b. Test locally with help of `docker-compose`

Create `docker-compose.yaml` file and copy the following content.

Once the docker-compose.yaml is created, you can start the containers by running - 

```
docker compose up
```
You can learn more about docker compose [here](https://docs.docker.com/compose/)

```
#docker-compose.yaml for distributed horovod testing

services:
  worker-main:
    ports:
      - "12344:12345"
    environment:
      ENABLE_TIMELINE: '0'
      HOROVOD_ARGS: --verbose
      MAX_NP: '2'
      MIN_NP: '2'
      OCI_IAM_TYPE: api_key
      OCI_CONFIG_PROFILE: DEFAULT
      OCI__CLUSTER_TYPE: HOROVOD
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /code/data #any arguments that the training script requires.
      OCI__EPHEMERAL: None
      OCI__MODE: MAIN
      OCI__WORKER_COUNT: '1'
      OCI__WORK_DIR: /work_dir
      SLOTS: '1'
      START_TIMEOUT: '700'
      SYNC_ARTIFACTS: '0'
      WORKER_PORT: '12345'
      WORKSPACE: <bucket_name>
      WORKSPACE_PREFIX: <workspace_name>
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/root/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
      - ./:/code
  worker-0:
    ports:
      - "12345:12345"
    environment:
      ENABLE_TIMELINE: '0'
      HOROVOD_ARGS: --verbose
      MAX_NP: '2'
      MIN_NP: '2'
      OCI_IAM_TYPE: api_key
      OCI_CONFIG_PROFILE: DEFAULT
      OCI__CLUSTER_TYPE: HOROVOD
      OCI__ENTRY_SCRIPT: /code/train.py
      OCI__ENTRY_SCRIPT_ARGS: --data-dir /code/data #any arguments that the training script requires.
      OCI__EPHEMERAL: None
      OCI__MODE: WORKER
      OCI__WORKER_COUNT: '1'
      OCI__WORK_DIR: /work_dir
      SLOTS: '1'
      START_TIMEOUT: '700'
      SYNC_ARTIFACTS: '0'
      WORKER_PORT: '12345'
      WORKSPACE: <bucket_name>
      WORKSPACE_PREFIX: <workspace_name>
    image: <region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>
    volumes:
      - ~/.oci:/root/.oci
      - ./work_dir:/work_dir
      - ./artifacts:/opt/ml
      - ./:/code
  
```

Things to keep in mind:
1. Port mapping needs to be added as each container needs a different ssh port to be able to run on the same machine. Ensure that `network_mode: host` is not present when port mapping is added.
2. You can mount your training script directory to /code like the above docker-compose (`../examples:/code`). This way there's no need to build docker image every time you change training script during local development
3. Pass in any parameters that your training script requires in 'OCI__ENTRY_SCRIPT_ARGS'.
4. During multiple runs, delete your all mounted folders as appropriate; especially `OCI__WORK_DIR`
5. `OCI__WORK_DIR` can be a location in object storage or a local folder like `OCI__WORK_DIR: /work_dir`.
6. In case you want to use a config_profile other than DEFAULT, please change it in `OCI_CONFIG_PROFILE` env variable.

### 3. Create yaml file to define your cluster. Here is an example. 
### Please refer to the [documentation](http://10.209.39.50:8000/user_guide/model_training/distributed_training/horovod/creating.html) for more details.


In this example, we bring up 2 worker nodes and 1 scheduler node. The training code to run is `train.py`. All code is assumed to be present inside `/code` directory within the container. Additionaly 
you can also put any data files inside the same directory (and pass on the location ex '/code/data/**' as an argument to your training script).

```
kind: distributed
apiVersion: v1.0
spec:
  infrastructure: # This section maps to Job definition. Does not include environment variables
    kind: infrastructure
    type: dataScienceJob
    apiVersion: v1.0
    spec:
      projectId: oci.xxxx.<project_ocid>
      compartmentId: oci.xxxx.<compartment_ocid>
      displayName: HVD-Distributed-TF
      logGroupId: oci.xxxx.<log_group_ocid>
      subnetId: oci.xxxx.<subnet-ocid>
      shapeName: VM.Standard2.4 #use a gpu shape such as VM.GPU2.1 incase you have built a gpu based docker image.
      blockStorageSize: 50
  cluster:
    kind: HOROVOD
    apiVersion: v1.0
    spec:
      image: "<region>.ocir.io/<tenancy_id>/<repo_name>/<image_name>:<image_tag>"
      workDir:  "oci://<bucket_name>@<bucket_namespace>/<bucket_prefix>"
      name: "horovod_tf"
      config:
        env:
          # MIN_NP, MAX_NP and SLOTS are inferred from the shape. Modify only when needed.
          # - name: MIN_NP
          #   value: 2
          # - name: MAX_NP
          #   value: 4
          # - name: SLOTS
          #   value: 2
          - name: WORKER_PORT
            value: 12345
          - name: START_TIMEOUT #Optional: Defaults to 600.
            value: 600
          - name: ENABLE_TIMELINE # Optional: Disabled by Default.Significantly increases training duration if switched on (1).
            value: 0
          - name: SYNC_ARTIFACTS #Mandatory: Switched on by Default.
            value: 1
          - name: WORKSPACE #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket to sync generated artifacts to.
            value: "<bucket_name>"
          - name: WORKSPACE_PREFIX #Mandatory if SYNC_ARTIFACTS==1: Destination object bucket folder to sync generated artifacts to.
            value: "<bucket_prefix>"
          - name: HOROVOD_ARGS # Parameters for cluster tuning.
            value: "--verbose"
      main:
        name: "worker-main"
        replicas: 1 #this will be always 1. Handles scheduler's responsibilities too.
      worker:
        name: "worker-0"
        replicas: 1 #number of workers. This is in addition to the 'worker-main' worker. Could be more than 1
  runtime:
    kind: python
    apiVersion: v1.0
    spec:
      entryPoint: "/code/train.py" #location of user's training script in docker image.
      args:  #any arguments that the training script requires.
          - --data-dir    # assuming data folder has been bundled in the docker image.
          - /code/data/mnist.npz
      env:
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
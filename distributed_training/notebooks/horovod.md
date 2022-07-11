# Developer Guide

## Steps to run Distributed Horovod

All the docker image related artifacts are located under - `oci_dist_training_artifacts/horovod/v1/`


### 1. Prepare Docker Image
Horovod provides support for Pytorch and Tensorflow. Within these frameworks, there are two separate docker files, for cpu and gpu.
Choose the docker file and conda environment files based on whether you are going to use Pytorch or Tensorflow with either cpu or gpu.

The instruction assumes that you are running this within the folder where you ran `ads opctl distributed-training init --framework horovod-<pytorch|tensorflow>`

All files in the current directory is copied over to `/code` folder inside docker image. 

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
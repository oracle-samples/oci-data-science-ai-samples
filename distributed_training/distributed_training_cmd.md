# Developer Guide

## ADS CLI commands for distributed training

ADS Opctl CLI provides a set of commands for seamless local setup and testing of code for distributed training.

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

### Build Container Image Only Using ADS CLI

#### Args

- `-t`: tag of the container image
- `-reg`: OCIR Container Registry
- `-df`: the location of Dockerfile used to build the container image
- `-push`: to push the image to OCI Registry
- `-s`: your project source code directory

#### Command

```bash
ads opctl distributed-training build-image
   -t $TAG
   -reg $NAME_OF_REGISTRY
   -df $PATH_TO_DOCKERFILE
   -s $MOUNT_FOLDER_PATH
```

**Note** these commands can be used to build a container image from ADS CLI. It writes a `config.ini` file into your project which can be used further referred by other CLI commands.

When the `-push` flag is used in the command then container image is pushed to the specified OCIR repository und successsful build.

Sample **config.ini** file

```ini
[main]
tag = $TAG
registry = $NAME_OF_REGISTRY
dockerfile = $PATH_TO_DOCKERFILE
source_folder = $MOUNT_FOLDER_PATH
; mount oci keys for local testing 
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

**Note** the `~/.oci` is the default location for the Oracle SDK API Keys. Change this only if you store your keys in a different location.

### Publish Container Image to OCI Registry

#### Args

`-image`: Name of the container image (default value is picked from config.ini file)

#### Command

```bash
ads opctl distributed-training publish-image
```

**Note** this command can be used to push images to the OCI repository. In case the name of the image is not mentioned it refers to the image name from the `config.ini` file.

### Run the Container Image on the OCI Data Science Service Jobs platform or local

#### Args

- `-f`: path to `train.yaml` file (required argument)
- `-b`:
  - `local` → run DT workflow on the local environment
  - `job` → run DT workflow on the OCI Data Science Jobs
  **Note** : default value is set to `job`
- `-i`: auto increments the tag of the image
- `-nopush`: do not push the latest image to OCIR
- `-nobuild`: do not build the image
- `-t`: sets the tag of the container image
- `-reg`: Oracle Cloud Infrastructure Registry location to push the build container images
- `-df`: Dockerfile location used to build the container image
- `-s`: your project source code directory

**Note**: In case `train.yaml` has `"@image"` specified for `image` property, the image name will be replaced at runtime using combination of  `-t` and `-r` params.

#### Command

_Run locally_

```bash
ads opctl run
        -f train.yaml
        -b local
        -i
```

_Run as a Job on OCI_

```bash
ads opctl run
        -f train.yaml
```

**Note** the command `ads opctl run -f train.yaml` is used to run the DT jobs on the Oracle Cloud Infrastructure Data Science Jobs platform. By default, it builds the new image and pushes it to the OCIR and executes the distributed training job.

If required OCI API keys can be mounted by specifying the location in the `config.ini` file

## User Flow For Seamless Development Experience

**Init Your Project**:

Setup your project on your local machine with all the required project files to run distributed training.

```bash
ads opctl distributed-training init --framework <framework>
```

`<framework>` - could be `horovod-tensorflow|horovod-pytorch|pytorch|tensorflow|dask`

**Step1**:

Build the container image and run it locally.

If you run the CLI outside of the init setup folder, mount your project code folder using the ```-s``` tag.

```bash
ads opctl run \
        -f train.yaml \
        -b local \
        -t $TAG \
        -reg $NAME_OF_REGISTRY \
        -df $PATH_TO_DOCKERFILE \
        -s $MOUNT_FOLDER_PATH
```

**Example**:

```bash
ads opctl run \
        -f train.yaml \
        -b local \
        -t 1.0 \
        -reg iad.ocir.io/bigdatadatasciencelarge/dtv15 \
        -df oci_dist_training_artifacts/horovod/v1/docker/pytorch.cpu.Dockerfile \
        -s .
```

**Note** that the above `run` will also setup your `config.ini` file and you no longer need to use all of the flags next time.

**Step2**:

After the initial run, if you do changes to your project like Dockefile or environment.yaml files, just re-run with:

```bash
ads opctl run \
        -f train.yaml \
        -b local \
```

If you change files only in you mounted code folder and never change Dockerfile or related environment.yaml files you can run locally with the `-nobuild` flat, which means the container image will not be rebuild:

```bash
ads opctl run \
        -f train.yaml \
        -b local \
        -nobuild \
```

`-i` tag is required only if the you want to auto-increment the tag version of the container image:

```bash
ads opctl run \
        -f train.yaml \
        -b local \
        -i
```

**Step3**:

Finally, to run on a jobs platform

```bash
ads opctl run \
        -f train.yaml
```

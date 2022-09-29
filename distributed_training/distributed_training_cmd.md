# Developer Guide

## Ads CLI commands to run Ml distributed frameworks

### 1. Build Image using ads CLI


**Args**

1. -t: Tag of the docker image
2. -reg: Docker Repository 
3. -df: Dockerfile using which docker will be build 
4. -push: push the image to oci registry
5. -s: source code dir

**Command**

```
ads opctl distributed-training build-image
   -t $TAG
   -reg $NAME_OF_REGISTRY
   -df $PATH_TO_DOCKERFILE
   -s $MOUNT_FOLDER_PATH
```

**Note** : 

This command can be used to build a docker image from ads CLI. It writes the config.ini file in the user's runtime environment which can be used further referred by other CLI commands.

If ```-push``` tag is used in command then docker image is pushed to mentioned repository

*Sample config.ini file*

```
[main]
tag = $TAG
registry = $NAME_OF_REGISTRY
dockerfile = $PATH_TO_DOCKERFILE
source_folder = $MOUNT_FOLDER_PATH
; mount oci keys for local testing 
oci_key_mnt = ~/.oci:/home/oci_dist_training/.oci
```

### 2. Publish Docker Image to the repository using Ads CLI

**Args**

1. -image: Name of the Docker image (default value is picked from config.ini file)

**Command**

```
ads opctl distributed-training publish-image
```

**Note**

This command can be used to push images to the OCI repository. In case the name of the image is not mentioned it refers to the image name from the config.ini file.

### 3. Run the Docker Image on the OCI Jobs platform or local using Ads CLI

**Args**

1. -f: Path to train.YAML file (required argument)
2. -b : 
   1. ```local``` → Run DT workflow on the local environment
   2. ```jobs``` → Run DT workflow on the OCI ML Jobs 
   3. **Note** : default value is set to jobs
3. -i: Auto increments the tag of the image 
4. -nopush: Doesn't Push the latest image to OCIR
5. -nobuild: Doesn't build the image
6. -t: Tag of the docker image
7. -reg: Docker Repository 
8. -df: Dockerfile using which docker will be build
9. -s: source code dir

**Note** : ``` -t ``` and ``` -reg ``` args are not required if image name is mentioned in train.yaml 
file. If the image name in train.yaml file starts with ```@``` then image name is updated using ``` -t ```
and ``` -reg ``` args.

**Command**

*Local Command*

```
ads opctl run
        -f train.yaml
        -b local
        -i
```

*Jobs Command*

```
ads opctl run
        -f train.yaml
```

**Note**

The command ``` ads opctl run -f train.yaml ``` is used to run the DT jobs on the Jobs platform. By default, it builds the new image and pushes it to the OCIR. 

If required OCI API keys can be mounted by specifying the location in the config.ini file



## User Flow For Seamless Development Experience

**Step1**: 

Build the Docker and run it locally.

If required mount the code folder using the ```-s``` tag 
``` 
ads opctl run
        -f train.yaml 
        -b local
        -t $TAG
        -reg $NAME_OF_REGISTRY 
        -df $PATH_TO_DOCKERFILE
        -s $MOUNT_FOLDER_PATH
```

**Step2**: 

If the user has changed files only in the mounted folder and needs to run it locally. *{Build is not required}*

```
ads opctl run
        -f train.yaml
        -b local
        -nobuild
```

In case there are some changes apart from the mounted folder and needs to run it locally. *{Build is required}*

```-i``` tag is required only if the user needs to increment the tag of the image 

```
ads opctl run
        -f train.yaml
        -b local
        -i
```

**Step3**: 

Finally, to run on a jobs platform

```
ads opctl run
        -f train.yaml
```
<!-- ### Process to pull NIM image from Nvidia and push in to OCIR -->

## Part 1: Pull NIM image from Nvidia to your local machine

### Step 1: Get access to NIM image login to docker:

Register to developer account at https://build.nvidia.com/explore/discover. After logging in you can get the ngc token by going in the model page and clicking generate token button.

In place of password place your newly generated NGC token.

```
$ docker login nvcr.io  
Username: $oauthtoken  
Password: nvapi-6mj......
```

### Step 2: Pull image to your local machine:  
```
Choose a container name for bookkeeping  
$ export CONTAINER_NAME=llama3-8b-instruct
 
Define the vendor name for the LLM  
$ export VENDOR_NAME=meta  

$ export IMG_NAME="nvcr.io/nim/${VENDOR_NAME}/${CONTAINER_NAME}:latest"  

$ docker pull $IMG_NAME
```

## Part 2: Push this image to ocir:

### Step 1: Login to ocir docker:

To get your registry domain check: https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryprerequisites.htm#regional-availability  
If you dont have login details please check: https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm#:~:text=If%20you%20already%20have%20an%20auth%20token%2C%20go%20to%20the%20next%20step.%20Otherwise%3A

```
$ docker login <registry-domain>
```
When prompted for a username, enter your username in the format ```<tenancy-namespace>```/```<username>```, where ```<tenancy-namespace>``` is the auto-generated Object Storage namespace string of your tenancy (as shown on the Tenancy Information page).  
For example, ansh81vru1zp/jdoe@acme.com.  
When prompted for a password, enter your auth token.



### Step 2: Locate the image on the client machine that you want to push:
```
$ docker images
```
```
Ex output for our image:  

REPOSITORY                            TAG      IMAGE ID    
nvcr.io/nim/meta/llama3-8b-instruct   latest   106df041c287
```

### Step 3: Tag the docker image
```
$ docker tag <image-identifier> <target-tag>
```

```<target-tag>``` is the fully qualified path to the target location in Container Registry where you want to push the image, in the format ```<registry-domain>/<tenancy-namespace>/<repo-name>:<version>```

```
Ex command:

$ docker tag 106df041c287 ocir.us-ashburn-1.oci.oraclecloud.com/ansh81vru1zp/project01/acme-web-app:v2.0.test
```

### Setp 4: push to ocir
```
$ docker push <target-tag>
```

Note: For more information on pushing image to OCIR refer: https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm
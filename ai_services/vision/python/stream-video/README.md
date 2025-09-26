vision-service python sample for streaming service (detecting object) video using sync API and final output is saved in json file. 

# MAC OS:

## 0. Setup 
```
Follow the links below to generate a config file and a key pair in your ~/.oci directory
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm
https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm#configfile

After completion, you should have following 2 things in your ~/.oci directory 

a. A config file(where key file point to private key:key_file=~/.oci/oci_api_key.pem)
b. A key pair named oci_api_key.pem and oci_api_key_public.pem

Now make sure you change the reference of key file in config file (where key file point to private key:key_file=/YOUR_DIR_TO_KEY_FILE/oci_api_key.pem)
```

## 1. Make sure you are in the root directory of this project:
```
cd ~/stream-video
```

## 2. Upload Public Key
```
Upload your oci_api_key_public.pem to the console:
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#three

If you do not have your own config and oci_api_key.pem ready to use, we have
a pair of keys and a config file in the /sample_secrets folder. You can use those to run the demo code for testing purposes.
```

## 3. Make sure you have python installed on your machine
```
python --version
```
And I see following:
'''
Python 3.9.6
'''
 
## 4. Install all dependencies (including our beta version SDK):
```
Make sure you are on either Oracle Corp VPN or OCNA, and have enabled the proxy
export http_proxy=http://www-proxy-adcq7.us.oracle.com:80;
export https_proxy=http://www-proxy-adcq7.us.oracle.com:80;
export no_proxy=localhost,127.0.0.1,.us.oracle.com,oraclecorp.com;
pip install -r requirements.txt

```
 
## 5. Private Connectivity via Static IP and Port Forwarding
```
Follow these steps to configure secure private connectivity in Oracle Cloud Infrastructure:

A. Create a Virtual Cloud Network (VCN):
Set up a new VCN with your chosen CIDR block in the appropriate compartment.

B. Create a Private Subnet:
Add a private subnet within your VCN to isolate internal resources.

C. Create a NAT Gateway:
Provision a NAT Gateway in the VCN so that private resources can access the internet for updates and patches, while remaining inaccessible from the public internet.

D. Configure Route Table:
Add a route table entry to direct all outbound internet traffic from the private subnet through the NAT Gateway.

```


## 5. Stream video python sample scripts usage

```
usage: stream_video_demo.py [-h] --compartment-id [COMPARTMENT_ID] --subnet-id [SUBNET_ID] --camera-url [CAMERA_URL] --namespace [NAMESPACE] --bucket [BUCKET] [--prefix PREFIX] [-v]

arguments:
-h, --help Show this help message and exit
-v, --verbose Print logs
--compartment-id COMPARTMENT_OCID Compartment OCID for the resources
--subnet-id SUBNET_ID Subnet for the private endpoint
--camera-url CAMERA_URL Camera URL for the stream
--namespace NAMESPACE Namespace of the bucket
--bucket BUCKET_NAME Bucket name
optional arguments:
--prefix PREFIX Prefix
```

## 6. Some examples commands:
```
python3 stream_video_demo.py --compartment-id "ocid1.compartment.oc1.." --subnet-id "ocid1.subnet.oc1.iad." --camera-url ""rtsp://64.181.159.98:443/weapon" --namespace "namespace"  --bucket "bucket" --prefix "testing"

The above command will create a stream source, stream job, and stream group, then start and stop the stream job, and finally delete everything.

```
 

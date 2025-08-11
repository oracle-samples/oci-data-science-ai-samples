vision-service python sample for streaming service (detecting object) video using sync API and final output is saved in json file. 

# MAC OS:

## 0. Set up 
```
Follow links below to generate a config file and a key pair in your ~/.oci directory 
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
# Upload your oci_api_key_public.pem to console:
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#three

Just in case you do not have your own config and oci_api_key.pem ready to use, we have
a pair of keys and a config file in /sample_secrets folder, you can use those to run demo code for testing purposes.
```

## 3. Make sure you have python installed on your machine
```
python --version
```
And I see following:
'''
Python 3.9.6
'''
 
## 4. Install all dependencies(include our beta version SDK):
```
# Make sure you are on either Oracle Corp VPN or OCNA, and have enabled proxy
export http_proxy=http://www-proxy-adcq7.us.oracle.com:80;
export https_proxy=http://www-proxy-adcq7.us.oracle.com:80;
export no_proxy=localhost,127.0.0.1,.us.oracle.com,oraclecorp.com;
pip install -r requirements.txt

```
 
## 5. Stream video python sample scripts usage

```
usage: stream_video_demo.py [-h] --compartment-id [COMPARTMENT_ID] --camera-url [CAMERA_URL] --namespace [NAMESPACE] 
    --bucket [BUCKET] --prefix [PREFIX] --feature [FEATURE] [-v]

optional arguments:
  -h, --help  show this help message and exit
  -v, --verbose Print logs
  --compartment-id COMPARTMENT_OCID compartment for the resources
  --camera-url CAMERA_URL camera url for the stream
  --namespace NAMESPACE namespace of the Bucket
  --bucket BUCKET_NAME bucket name
  --prefix PREFIX prefix
  --feature FEATURE feature
```

## 6. Some examples commands:
```
python3.9 stream_video_demo.py --compartment-id  --camera-url "rtsp://64.181.159.98:443/stream" --namespace "idvbwij6bjry"  --bucket  "stream-test" --prefix "testing" --feature FEATURES "[
    {
        "featureType": "OBJECT_TRACKING",

        "trackingTypes":[
            {
                "objects": ["face"],
                "maxResults": 5,
                "shouldReturnLandmarks": True,
                "biometricStoreId": "ocid1.aibiometricstore.oc1.phx.amaaaaaat4fqliqahiowefua5gnv4vclqzejnjbt6udryjuqrmsqvppkp74a",
                "biometricStoreCompartmentId": "ocid1.tenancy.oc1..aaaaaaaanvgztn3ytxqdpryxvcv6xfx4xaggt7n243kjzim36xstqbymdgkq"
            }
        ]
    }
]"

Above command will create stream source, stream job and stream group, then start and stop stream job and finally delete everything


```
 
## 7. After running above script, You should see output in json, format is video-file_fps_output-frame-rate_responses.json.

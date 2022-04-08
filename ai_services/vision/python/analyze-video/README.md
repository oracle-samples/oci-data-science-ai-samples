vision-service python sample for analysing (detecting object) video using sync API and final output is saved in json file. 

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
cd ~/analyze-video
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
 
## 5. Analyse video python sample scripts usage

```
usage: analyze_video_demo.py [-h] --video-file VIDEO_FILE [--model-id MODEL_ID] 
    [--output-frame-rate OUTPUT_FRAME_RATE] [--confidence-threshold CONFIDENCE_THRESHOLD] [-v]

optional arguments:
  -h, --help            show this help message and exit
  --video-file VIDEO_FILE
                        video input file path
  --model-id MODEL_ID   custom trained model id for inference
  --output-frame-rate OUTPUT_FRAME_RATE
                        output frames per second
  --confidence-threshold CONFIDENCE_THRESHOLD
                        confidence threshold values are added
  -v, --verbose         Print logs

```

## 6. Some examples commands:
```
python3.9 analyze_video_demo.py --video-file input-video-file.mp4 --output-frame-rate 5

Above command will process the input file input-video-file.mp4 and process 5 frames per second.

python3.9 analyze_video_demo.py --video-file input-video-file.mp4 --output-frame-rate 5 --confidence-threshold 0.9

Above command will process the input file input-video-file.mp4 and process 5 frames per second and remove object 
which has lower confidence than 0.9

```
 
## 7. After running above script, You should see output in json, format is video-file_fps_output-frame-rate_responses.json.

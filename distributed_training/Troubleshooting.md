# TroubleShooting

| Problem        | Possible Cause           | Solution  |
| ------------- |-------------| -----|
| Horovod Job runs fails with the following message: </br> </br> ```/miniconda/envs/env/lib/python3.8/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 15 leaked semaphore objects to clean up at shutdown 2022-07-05 10:50:18 - Exiting with exit code: 1```  </br>  | This generally indicates an issue with the network communication. | Please ensure that for Horovod, allow all traffic within the subnet. |
| Tensorboard shows empty logs. | While fetching logs from object bucket, Tensorboard takes a little bit of time for bootstrapping. |    1. Please wait for some time. </br> 2. Check the object storage. |
| Docker image publish to ocir fails during ```ads opctl run -f train.yaml -b job```. | This could be because of a wrong image name or incorrect policies for the container registry. |    1. Please ensure the name represents the container registry. </br> 2. Check the container registry related policies. |

# FAQS

| Framework        | Question           | Answer  |
| ------------- |:-------------:| -----:|
| Tensorflow   | Do I need to take care of ```TF_CONFIG``` in my code ? | No. The framework takes care of injecting the ```TF_CONFIG``` representing the cluster and ```task_type```, ```task_id```.|





# TroubleShooting

| | Problem        | Possible Cause           | Solution  |
|-------------| ------------- |-------------| -----|
|1.| Horovod Job runs fails with the following message: </br> </br> ```/miniconda/envs/env/lib/python3.8/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 15 leaked semaphore objects to clean up at shutdown 2022-07-05 10:50:18 - Exiting with exit code: 1```  </br>  | This generally indicates an issue with the network communication. | Please ensure that for Horovod, allow all traffic within the subnet. |
|2.| Tensorboard shows empty logs. | While fetching logs from object bucket, Tensorboard takes a little bit of time for bootstrapping. |    1. Please wait for some time. </br> 2. Check the object storage. |
|3.| Docker image publish to ocir fails during ```ads opctl run -f train.yaml -b job```. | This could be because of a wrong image name or incorrect policies for the container registry. |    1. Please ensure the name represents the container registry. </br> 2. Check the container registry related policies. |

# FAQS

| | Framework        | Question           | Answer  |
| -------------| ------------- |:-------------:| -----:|
|1. | Tensorflow   | Do I need to take care of ```TF_CONFIG``` in my code ? | No. The framework takes care of injecting the ```TF_CONFIG``` representing the cluster and ```task_type```, ```task_id```.|


# Known Issues

| | Issue        | Description           |   
|-------------| ------------- |:-------------:|
|1.| Horovod Scale Down not working. | Horovod scale down Elasticity doesn't seem to work with ads opctl. When of the jobs runs is cancelled, the expected behavior is that the horovod training will continue as long as ```min_np``` is satisfied. However, the training stops.|
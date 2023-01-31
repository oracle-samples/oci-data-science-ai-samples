# Troubleshootings

## Guide

***:scream: Problem***
Horovod Job runs fails with the following message:

```/miniconda/envs/env/lib/python3.8/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 15 leaked semaphore objects to clean up at shutdown 2022-07-05 10:50:18 - Exiting with exit code: 1```

***:sparkles: Solution***
This generally indicates an issue with the network communication. Please ensure that for Horovod, all traffic within the subnet is enabled.

---

***:scream: Problem***
Tensorboard shows empty logs, while fetching logs from object bucket. Tensorboard takes a little bit of time for bootstrapping.

***:sparkles: Solution***

- Please wait for some time.
- Check the object storage.

---

***:scream: Problem***
Docker image publish to ocir **fails** during **`ads opctl run -f train.yaml -b job`**

***:sparkles: Solution***
This could be because of a wrong image name or incorrect policies for the container registry.

- Please ensure the name represents the container registry.
- Check the container registry related policies.

---

***:scream: Problem***
`ads opctl run` fails with the error:

```bash
ApplyLayer exit status 1 stdout:  stderr: write /miniconda/pkgs/perl-5.32.1-0_h7f98852_perl5/lib/perl5/5.32/core_perl/auto/Encode/JP/JP.so: no space left on device
Traceback (most recent call last):
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/ads/cli.py", line 35, in <module>
    cli()
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 829, in __call__
    return self.main(*args, **kwargs)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/ads/opctl/distributed/cli.py", line 178, in build_image
    docker_build_cmd(ini)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/ads/opctl/distributed/cmds.py", line 355, in docker_build_cmd
    return run_cmd(cmd)
  File "/home/opc/miniconda3/envs/dtv15-1/lib/python3.8/site-packages/ads/opctl/distributed/cmds.py", line 406, in run_cmd
    raise RuntimeError(f"Docker build failed.")
RuntimeError: Docker build failed.
```

***:sparkles: Solution***
This is due to no disk space left on your instance or local machine. Increase the disk space or clean unused docker images and try again.

---

***:scream: Problem***
`ads opctl run` fails with the error:

```bash
PermissionError: [Errno 13] Permission denied: '/home/oci/.oci/oracleidentitycloudservice_oci.cardoso-12-15-16-14.pem'
```

***:sparkles: Solution***
This suggest that the private key stored on your local machine to be used by the OCI SDK and configured in your `.oci/config` file does not have the right permissions to be read by the account that runs the `ads opctl` commands in the terminal. To change the permissions use:

```bash
sudo chown <user>:<group> <private-key-name>.pem
```

---

***:scream: Problem***
`ads opctl distributed-training build-image -t $TAG -reg $IMAGE_NAME -df oci_dist_training_artifacts/tensorflow/v1/Dockerfile -s $MOUNT_FOLDER_PATH` fails with the error:

```bash

invalid argument "iad.ocir.io/namespace/dt:1.0:latest" for "-t, --tag" flag: invalid reference format
See 'docker build --help'.
Traceback (most recent call last):
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/ads/cli.py", line 35, in <module>
    cli()
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 829, in __call__
    return self.main(*args, **kwargs)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/ads/opctl/distributed/cli.py", line 178, in build_image
    docker_build_cmd(ini)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/ads/opctl/distributed/cmds.py", line 354, in docker_build_cmd
    return run_cmd(cmd)
  File "/home/oci/miniconda3/envs/distributed-training/lib/python3.8/site-packages/ads/opctl/distributed/cmds.py", line 405, in run_cmd
    raise RuntimeError(f"Docker build failed.")
RuntimeError: Docker build failed.
```

***:sparkles: Solution***
This error is due to wrongly set `$IMAGE_NAME`. The name is used also for the taggint that is needed to push to your OCIR. This name has to be in the correct form:

`iad.ocir.io/your-namespace/repo-name:latest`

---

***:scream: Problem***
`ads opctl run -f train.yaml | tee info.yaml` fails with error:

```bash
RuntimeError: Docker build failed.
......................... Initializing the process ...................................
#1 [internal] load build definition from Dockerfile
#1 sha256:25e29a908925d292aac8ad96ada80a9a01ee1536a35aa446cff5acc1fe377103
#1 transferring dockerfile: 38B done
#1 DONE 0.0s

#2 [internal] load .dockerignore
#2 sha256:815a9413864a4766f601ab62c6b14daaeed475ed80204f9a40c81c9b48231e71
#2 transferring context: 2B done
#2 DONE 0.0s

#3 [internal] load metadata for nvcr.io/nvidia/tensorflow:22.07-tf2-py3
#3 sha256:89beb62ed35a3e33301260a014f455765ed0d058224fc12da1930295e7d214c6
#3 ERROR: failed to authorize: rpc error: code = Unknown desc = failed to fetch anonymous token: unexpected status: 401 Unauthorized
------
 > [internal] load metadata for nvcr.io/nvidia/tensorflow:22.07-tf2-py3:
------
failed to solve with frontend dockerfile.v0: failed to create LLB definition: failed to authorize: rpc error: code = Unknown desc = failed to fetch anonymous token: unexpected status: 401 Unauthorized
```

***:sparkles: Solution***
This is very likely due to not been authenticated to the OCIR. Run `docker login` as shown in the [Getting Started Guide](README.md) to Login into your OCIR (Oracle Cloud Container Registry)

---

## FAQS

| | Framework        | Question           | Answer  |
| -------------| ------------- |:-------------:| -----:|
|1. | Tensorflow   | Do I need to take care of ```TF_CONFIG``` in my code ? | No. The framework takes care of injecting the ```TF_CONFIG``` representing the cluster and ```task_type```, ```task_id```.|

## Known Issues

| | Issue        | Description           |
|-------------| ------------- |:-------------:|
|1.| Horovod Scale Down not working. | Horovod scale down Elasticity doesn't seem to work with ads opctl. When of the jobs runs is cancelled, the expected behavior is that the horovod training will continue as long as ```min_np``` is satisfied. However, the training stops.|

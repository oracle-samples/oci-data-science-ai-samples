# ZIP/TAR Jobs

This folder contain samples that demonstrate how to run entire project structure as ZIP or TAR compressed Job artifact.

There aren't special requirements about how to write your Python code or shell script to run it as a job. You can point to your main file using the `JOB_RUN_ENTRYPOINT` parameter after you zipped and tar compressed your file and upload it as job artifact.

They are two ways of how you can zip your project structure which will change the way you specify the `JOB_RUN_ENTRYPOINT` on Job and/or JobRun

__Variant 1__
In that you enter the folder that contains your project and you zip the content of the project, for example:

```bash
cd zipped_python_job
zip -r zipped_python_job.zip *.* -x ".*" -x "__MACOSX"
```

In that case the `JOB_RUN_ENTRYPOINT` should be set to: `entry.py`

__Variant 2__
... or zip the folder from outside:

```bash
zip -r zipped_python_job.zip zipped_python_job/ -x ".*" -x "__MACOSX" 
```

In that case the `JOB_RUN_ENTRYPOINT` should be set to: `zipped_python_job/entry.py`

Notice that the main file can be called anything, it doesn't have to be name `entry.py` but you should keep in mind that the name of the file `should NOT` have the same name as of the folder that contains the project or any other subfolder.

Additionally notice the `-x "__MACOSX"` prevents the hidden folder to be part of the package and it is important when you zip the code on MacOS machines, as it could cause an issue with the Job artifact execution.

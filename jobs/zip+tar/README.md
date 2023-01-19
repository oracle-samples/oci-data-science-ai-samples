# ZIP/TAR Jobs

This folder contain samples that demontstrate how to run entire project structure as ZIP or TAR compressed Job artifact.

There aren't special requirements about how to write your Python code or shell script to run it as a job. You can point to your main file using the `JOB_RUN_ENTRYPOINT` parameter after you upload the ZIP or compressed tar artifact.

Example of how to package and zip the code from within the folder:

```bash
cd zip-runtime-yaml-artifact
zip -r zip-runtime-yaml-artifact.zip *.* -x ".*" -x "__MACOSX"
```

... or zip the folder from outside:

```bash
zip -r zip-runtime-yaml-artifact.zip zip-runtime-yaml-artifact/ -x ".*" -x "__MACOSX" 
```

Notice the `-x "__MACOSX"` prevents the hidden folder to be part of the package and it is important when you zip the code on MacOS machines, as it could cause an issue with the Job artifact execution.

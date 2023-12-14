# Debugging

You could debug the code in the container utilizing the [Visual Studio Code Remote - Tunnels](https://code.visualstudio.com/docs/remote/tunnels) extension, which lets you connect to a remote machine, like a desktop PC or virtual machine (VM), via a secure tunnel. You can connect to that machine from a VS Code client anywhere, without the requirement of setting up your own SSH, including also using the Oracle Cloud Infrastructure Data Science Jobs.

The tunneling securely transmits data from one network to another. This can eliminate the need for the source code to be on your VS Code client machine since the extension runs commands and other extensions directly on the OCI Data Science Job remote machine.

## Requirements

To use the debugging you have to finalize the steps of building and pushing the container of your choice to the Oracle Cloud Container Registry.

# Run for Debugging

For debugging purposes we will utilize the OCI Data Science Jobs service. Once the TGI or the vLLM container was build and published to the OCIR, we can run it as a Job, which would enable us take advance of the VSCode Remote Tunneling. To do so follow the steps:

* In your [OCI Data Science](https://cloud.oracle.com/data-science/projects) section, select the project you've created for deployment
* Under the `Resources` section select `Jobs`
* Click on `Create job` button
* Under the `Default Configuration` select the checkbox for `Bring your own container`
  * Set following environment variables:
  * `CONTAINER_CUSTOM_IMAGE` with the value to the OCI Container Registry Repository location where you pushed your container, for example: `<your-region>.ocir.io/<your-tenancy-name>/vllm-odsc:0.1.3`
  * `CONTAINER_ENTRYPOINT` with the value `"/bin/bash", "--login",  "-c"`
  * `CONTAINER_CMD` with the value `/aiapps/runner.sh`
  * The above values will override the default values set in the `Dockerfile` and would enable to launch the tunneling
* Under `Compute shape` select `Custom configuration` and then `Specialty and previous generation` and select the `VM.GPU.A10.2` shape
* Under `Logging` select the log group you've created for the model deployment and keep the option `Enable automatic log creation`
* Under `Storage` set 500GB+ of storage
* Under `Networking` keep the `Default networking` configuration

With this we are now ready to start the job

* Select the newly created job, if you have not done so
* Click on the `Start a job run` 
* Keep all settings by default and click on `Start` button at the bottom left

Once the job is up and running, you will notice in the logs, the authentication code appears, you can copied and use it to authorize the tunnel, few seconds later the link for the tunnel would appear.

![vscode tunnel in the oci job](../../../jobs/tutorials/assets/images/vscde-server-tunnel-job.png)

Copy the link and open it in a browser, which should load the VSCode Editor and reveals the code inside the job, enabling direct debugging and coding.

`Notice` that you can also use your local VSCode IDE for the same purpose via the [Visual Studio Code Remote - Tunnels](https://code.visualstudio.com/docs/remote/tunnels) extension

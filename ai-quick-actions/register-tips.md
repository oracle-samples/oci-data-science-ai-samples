# Register a model

Table of Contents:

- [Home](README.md)
- [CLI](cli-tips.md)
- [Policies](policies/README.md)
- [Model Deployment](model-deployment-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)

The AI Quick Action model explorer allows you to register a model from Hugging Face or Object Storage with a few clicks.

![Register new model](web_assets/register-button.png)

## Register Model from Hugging Face

To register a model from Hugging Face, select "Download from Hugging Face" in the dropdown under model artifact. Then you may select a verified model from the "Select Model" dropdown, or you may "register any model" by entering the model name.

Note that for gated models, please authenticate to Hugging Face by running `huggingface-cli login` command in terminal. See details in [Hugging Face CLI documentation](https://huggingface.co/docs/huggingface_hub/en/guides/cli).

![Register model from Hugging Face](web_assets/register-model.png)

## Upload Model Artifact to Object Storage Manually

AI Quick Actions also supports user-provided models that can be deployed, fined-tuned and evaluated.

While registering the model in AI Quick Actions, you need to specify the Object Storage location where the model artifact is stored.
You may first prepare your model files locally and then upload it to object storage.
For example, you can download the model from the Hugging Face Hub using the download instructions [here](https://huggingface.co/docs/huggingface_hub/main/en/guides/download).

Once downloaded, use [oci-cli](https://github.com/oracle/oci-cli) to upload these artifacts to the correct object storage location. 
The object storage bucket needs to be versioned, run the following command to check whether versioning is set up. If the output of the below command is "Disabled", then you need
to turn on object storage versioning for this bucket. More details on how to do this is available [here](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingversioning.htm).

```bash
oci os bucket get -bn <bucket-name> -ns <namespace> --auth <auth_tpye> | jq ".data.versioning"
```

If the output of the above command is "Enabled", proceed to uploading the model artifacts to the object storage location using the following CLI command:
```bash
oci os object bulk-upload -bn <bucket-name> -ns <namespace> --auth <auth_tpye> --prefix <file prefix> --src-dir <local-dir-location> --no-overwrite
```

Once the upload is complete, provide the object storage location in the Register form in AI Quick Actions.

![Register and Upload.png](web_assets/register-upload.png)

After registration, this model will be available in the "My Models" tab in the Model Explorer for further use.


Table of Contents:

- [Home](README.md)
- [Policies](policies/README.md)
- [CLI](cli-tips.md)
- [Model Deployment](model-deployment-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)


This module handles opinionated Feature Store AuthN/AuthZ configuration using API Gateway on Oracle Cloud Infrastructure ([OCI][oci]). This stack is designed to be used with the [OCI Resource Manager][oci_rm] to enhance Feature store experience with AuthN/AuthZ in a single step. The stack can also be used with the [OCI Terraform Provider][oci_tf_provider] to deploy using local or CloudShell Terraform cli.

## Deploy Using Oracle Resource Manager

> ___NOTE:___ If you aren't already signed in, when prompted, enter the tenancy and user credentials. Review and accept the terms and conditions.

1. Click to deploy the stack

   [![Deploy to Oracle Cloud][magic_button]][magic_oke_stack]

1. Select the region and compartment where you want to deploy the stack.

1. Follow the on-screen prompts and instructions to create the stack.

1. After creating the stack, click Terraform Actions, and select Plan.

1. Wait for the job to be completed, and review the plan.

1. To make any changes, return to the Stack Details page, click Edit Stack, and make the required changes. Then, run the Plan action again.

1. If no further changes are necessary, return to the Stack Details page, click Terraform Actions, and select Apply.

1. After the stack application is complete attach the auto-provisioned security rules to the respective service and node subnets of the OKE cluster. 

### Prerequisites

Create a terraform.tfvars file and populate with the required variables or override existing variables.

Note: An example [tfvars file](examples/terraform.tfvars.example) is included for reference. Using this file is the
preferred way to run the stack from the CLI, because of the large number of variables to manage.

To use this file just copy the example [tfvars file](examples/terraform.tfvars.example) and save it in the outermost directory.
Next, rename the file to __terraform.tfvars__. You can override the example values set in this file.


### Running Terraform

After specifying the required variables you can run the stack using the following commands:

```bash
terraform init
```

```bash
terraform plan
```

```bash
terraform apply
```

```bash
terraform destroy -refresh=false
```


## License

Copyright (c) 2021, 2024 Oracle and/or its affiliates.
Released under the Universal Permissive License (UPL), Version 1.0.
See [LICENSE](./LICENSE) for more details.

[oci]: https://cloud.oracle.com/en_US/cloud-infrastructure
[oci_rm]: https://docs.cloud.oracle.com/iaas/Content/ResourceManager/Concepts/resourcemanager.htm
[magic_button]: https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg
[magic_oke_stack]: https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://raw.githubusercontent.com/harsh97/oci-data-science-ai-samples/feature-store/feature_store/fs_apigw_terraform.zip

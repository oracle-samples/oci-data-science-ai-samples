This module handles opinionated Feature Store AuthN/AuthZ configuration using API Gateway on Oracle Cloud Infrastructure ([OCI][oci]). This stack is designed to be used with the [OCI Resource Manager][oci_rm] to enhance Feature store experience with AuthN/AuthZ in a single step. The stack can also be used with the [OCI Terraform Provider][oci_tf_provider] to deploy using local or CloudShell Terraform cli.

## Deploy Using Oracle Resource Manager

> ___NOTE:___ If you aren't already signed in, when prompted, enter the compartment <compartment_name> and user credentials. Review and accept the terms and conditions.

1. Click to download the [terraform bundle][https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://raw.githubusercontent.com/harsh97/oci-data-science-ai-samples/feature-store/feature_store/fs_apigw_terraform.zip]

2. Create a stack in OCI resource manager with the downloaded bundle

3. Follow the on-screen prompts and instructions to create the stack.

4. After creating the stack, click Terraform Actions, and select Plan.

5. Wait for the job to be completed, and review the plan.

6. To make any changes, return to the Stack Details page, click Edit Stack, and make the required changes. Then, run the Plan action again.

7. If no further changes are necessary, return to the Stack Details page, click Terraform Actions, and select Apply.

8. After the stack application is complete attach the auto-provisioned security rules to the respective service and node subnets of the OKE cluster. 

### Prerequisites
#### Required permissions:

```bash
allow group <user_group> to manage orm-stacks in compartment <compartment_name>
allow group <user_group> to manage orm-jobs in compartment <compartment_name>
allow group <user_group> to read network-load-balancers in compartment <compartment_name>
allow group <user_group> to read instances in compartment <compartment_name>
allow group <user_group> to manage groups in compartment <compartment_name>
allow group <user_group> to manage dynamic-groups in compartment <compartment_name>
allow group <user_group> to manage functions-family in compartment <compartment_name>
allow group <user_group> to manage virtual-network-family in compartment <compartment_name>
allow group <user_group> to manage policies in tenancy
```


### Running Terraform

After specifying the required variables you can run the stack using the following commands:

```bash
terraform init
```

```bash
terraform plan -var-file=<path-to-variable-file>
```

```bash
terraform apply -var-file=<path-to-variable-file>
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
[stack]: https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://raw.githubusercontent.com/harsh97/oci-data-science-ai-samples/feature-store/feature_store/fs_apigw_terraform.zip

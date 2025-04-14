ML Application Infrastructure
==============================

Create New Environment
-----------------------------------
Steps to create new environment:
1. Navigate to `<project_root>/infrastructure/environments`. Copy the existing environment directory (for example, `_dev_`) and rename the copy to the new environment name, e.g., `_qa_`, `_integration_`.  
   * For a personal development environment, we recommend copying your `_dev_` directory (already configured for your tenancy) and using the naming convention `_dev-yourname_` (e.g., `_dev-john_`). You can leave all values in `input_variables.tfvars` as they are, except for the property `environment_name`, which should be updated to the new environment name, e.g., `_dev-myname_`.
   
2. Edit the `input_variables.tfvars` file in your new environment directory. Each configuration property is explained by a comment in the file.
   * For a personal development environment, assuming that all personal development environment will be 
   located in the same compartment as `_dev_` environment, you can leave all values in 
   `input_variables.tfvars` as they were originally for `_dev_` environment, except for the property `environment_name`, which should be updated to the new environment name, e.g., `dev-yourname`.

3. Open a terminal and navigate to your environment directory:
   ```bash
   cd infrastructure/environments/<your-env-dir-path>
   ```

4. Execute the following commands to create/update instruction for the environment:
   ```bash
   # Only for the first time
   terraform init
   
   # Anytime you make a change to Terraform and want to apply it to the cloud (for both creation usage and updates)
   terraform apply -var-file=input_variables.tfvars
   ```

Creation/Update/Destroy of Infrastructure
-----------------------------------

For creation/update of ML Application infrastructure use standard Terraform commands.

| WARNING: For production usage, it is highly recommended to configure remote state files<br/>See the documentation: https://developer.hashicorp.com/terraform/language/state/remote |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


Go to environment specific directory (e.g. {project_root}/infrastructure/environments/dev) and use following commands:

To initialize terraform (just for the first time):
```bash
terraform init
```
To create/update infrastructure:
```bash
terraform apply -var-file input_variables.tfvars
```
To remove infrastructure:
```bash
terraform destroy -var-file input_variables.tfvars
```

Oracle Resource Manager
----------------------------
For applying Terraform you can also use [Oracle Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm). In such a case
remove _config_file_profile_ property from _provider.tf_ file. Package the infra folder, create ORM stack and upload the package. Important is to set working directory to 
environment folder you want to use.

Multi-region Environment
-------------------------
In case of multi-region environment e.g. production with application deployment in more than one region, 
_region_ parameter should not be defined in _input_variables.tfvars_. It should be provided as parameter of terraform apply command instead.

Multi-realm Environment
------------------------
Each realm should have its own directory (including _input_variables.tfvar_) in directory _{project_root}/environments/_.

Example of directory _environments_:
- dev
- int
- preprod
- prod-oc1
- prod-oc2





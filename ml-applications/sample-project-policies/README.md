Environments Creation
======================

For creation/update of ML Application environment use standard Terraform commands.

| WARNING: For production usage, it is highly recommended to configure remote state files                                                                       |
|:--------------------------------------------------------------------------------|


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

FAQ
__________________________
- **Can policies for ML Applications be created in non-root compartment?**
  - No, they cannot because policies contain some statements which must be in root compartment ("Endorse" statements and statements with "in tenancy" scope). 
  - Note: These statements could be separated into another policy which would be in root and rest of the policies could be created in non-root compartment.
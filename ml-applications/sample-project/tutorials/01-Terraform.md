Terraform
============

## 1. Terraform Fundamentals

### Key Concepts
- **Infrastructure as Code (IaC)**: Manage cloud resources via text-based configuration files.
- **Declarative Approach**: Define the desired end state; Terraform calculates the necessary changes.
- **Providers, Resources, Data Sources**: Terraform uses providers (like OCI) to manage resources. Data sources fetch existing info.
- **State File**: Tracks metadata of managed resources (IDs, properties, relationships).

### Typical Terraform Workflow
1. **Initialize** (`terraform init`):
   - Downloads and configures providers.
   - Prepares working directory.
   - Also fetches and configures modules if your configuration references them.
2. **Plan** (`terraform plan`):
   - Compares desired state in `.tf` files with current state.
   - Shows what changes will be made (create, update, destroy).
3. **Apply** (`terraform apply`):
   - Executes the changes from the plan.
   - Deploys or updates resources in OCI.
   - Can also destroy resources if the plan requires it.
4. **Destroy** (`terraform destroy`):
   - Removes all resources in your Terraform configuration.
   - Use carefully, especially with production or stateful resources.

---

## 2. Providers, Resources, Data Sources & Resource Pitfalls

### Providers & Resources
- **Provider**: Plugin instructing Terraform how to interact with a platform (e.g., OCI).
- **Resource**: Declarative block describing an infrastructure component to create/manage.

```hcl
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

resource "oci_identity_compartment" "example_compartment" {
  name        = "example_tf_compartment"
  description = "Compartment created via Terraform"
}
```

- **Pitfall**: Certain immutable resource fields cause a destroy and recreate if changed.
  - Always check `terraform plan` before applying.

### Data Sources
- **Purpose**: Fetch information about existing resources or configurations.
- **Usage**: Ideal for referencing compartments, existing networks, etc.
- **Example**: Get a compartment by ID:

```hcl
data "oci_identity_compartment" "by_id" {
  compartment_id = var.existing_compartment_id
}

output "existing_compartment_name" {
  value = data.oci_identity_compartment.by_id.name
}
```

### Resource Pitfalls & Warnings
- **Renaming Resources**: Changing the resource block name or certain fields often leads to recreate.
- **Immutable Fields**: Changing a field that can’t be updated in place forces a replacement.
- **Dependent Resources**: If a parent resource is destroyed/recreated, child resources might also be impacted.

---

## 3. State Management

- **Purpose**: Maintains a record of existing resources (IDs, relationships, metadata) in `.tfstate`.
- **How It Works**:
  - Terraform compares your desired state (in `.tf` files) to the recorded state, then to real infrastructure.
  - Minimizes the need to query every resource on every plan.
- **Storage**:
  - Local: `terraform.tfstate` in current directory.
  - Remote: E.g., OCI Object Storage, Terraform Cloud.
- **Pitfall**: Manually modifying the state file can cause drift or corruption.

---

## 4. Variables, Locals, Functions & Output Blocks

### Variables
- **Types**:
  1. **string**
  2. **number**
  3. **bool**
  4. **list(...)**
  5. **map(...)**
  6. **object(...)**
  7. **tuple(...)**
- **Definition**:
```hcl
variable "compartment_name" {
  type    = string
  default = "example_compartment"
}

variable "tags" {
  type = map(string)
}

variable "allowed_ports" {
  type = list(number)
}

variable "instance_config" {
  type = object({
    shape = string
    count = number
  })
}

variable "misc_values" {
  type = tuple([string, bool, number])
}
```

### Example: `input_variables.tfvars`
```hcl
compartment_name = "my_prod_compartment"
tags = {
  env   = "production"
  owner = "team-sre"
}
allowed_ports = [22, 80, 443]
instance_config = {
  shape = "VM.Standard.E2.1.Micro"
  count = 2
}
misc_values = ["hello", true, 42]
```

### Referencing Variables
- **Inline**:
```hcl
resource "oci_identity_compartment" "example" {
  name = "my-project-${var.compartment_name}"
}
```
- **Standalone**:
```hcl
region = var.region
```

### Locals
- **Purpose**: Store reusable expressions/values within a config.
```hcl
locals {
  env         = "dev"
  prefix      = "myapp"
  full_prefix = "${local.prefix}-${local.env}"
}
```
- **Usage**:
```hcl
resource "oci_identity_compartment" "local_example" {
  name = "test-${local.full_prefix}"
}
```

### Functions
- **Common Built-in**: `upper()`, `lower()`, `concat()`, `length()`, `replace()`, etc.
```hcl
variable "environment" {
  type = string
}

locals {
  env_upper = upper(var.environment)
}

output "upper_env" {
  value = local.env_upper
}
```
- **Best Practices**:
  - Use descriptive names for variables and locals.
  - Parameterize environment-specific values in `.tfvars`.
  - Keep local usage clear; overuse can obscure code.

### Output Blocks
- **Purpose**: Let you expose certain values from your configuration after `terraform apply`. Useful for referencing in other contexts or simply for clarity.
- **Syntax**:
```hcl
output "resource_id" {
  description = "An ID for the created resource"
  value       = oci_identity_compartment.example_compartment.id
}
```
- **Where**: Typically declared in `.tf` files at the root level or within modules’ `outputs.tf`.
- **Tip**: Provide a `description` for clarity, especially in module outputs.

---

## 5. Modules

- **Purpose**: Package Terraform code for reusability and organization.
- **Structure**: `main.tf`, `variables.tf`, `outputs.tf` in a subfolder, e.g. `modules/compartment`.
- **Usage**:
```hcl
module "example_compartment" {
  source      = "./modules/compartment"
  name        = var.compartment_name
  description = "Module-based compartment"
}
```
- **Tip**: Keep modules small and cohesive.

### Example: Module with Output Usage

**modules/compartment/main.tf**
```hcl
resource "oci_identity_compartment" "this" {
  name        = var.name
  description = var.description
}
```

**modules/compartment/outputs.tf**
```hcl
output "compartment_id" {
  description = "ID of the created compartment"
  value       = oci_identity_compartment.this.id
}
```

**In your root configuration**:
```hcl
module "example_compartment" {
  source      = "./modules/compartment"
  name        = var.compartment_name
  description = "Module-based compartment"
}

# Example usage of module output
output "created_compartment_id" {
  description = "Display the newly created compartment OCID"
  value       = module.example_compartment.compartment_id
}
```


---

## 6. Project Organization

- **Typical Layout**:
  - `main.tf` for core resources or module calls.
  - `provider.tf` for provider configuration.
  - `variables.tf`, `outputs.tf` for definitions and references.
  - `modules/` subdirectory for custom modules.
  - `terraform.tfvars` for environment-specific overrides.
- **Multiple Environments**:
  - Separate directories or `.tfvars` files (e.g. `dev.tfvars`, `prod.tfvars`).

---

## 7. Advanced Features

- **for_each / count**:
  - Dynamically create multiple resources from a list or map.
  - Watch for changed keys or removed items, which can trigger destruction of resources.
- **Template Rendering**: `templatefile()` for dynamic configurations.
- **CI/CD Integration**: Automate `terraform plan`/`apply` with GitHub Actions, Jenkins, etc.
- **Custom Providers**: Extend Terraform with your own logic in Go.

---

## 8. Tips, Tricks, & Common Pitfalls

- **Sensitive Data**:
  - Use a vault (like HashiCorp Vault) for secrets.
  - Don’t commit credentials or private keys to version control.
- **Resource Replacement**:
  - **Immutable Fields**: Changing them triggers destroy/create (e.g., certain DB or bucket attributes).
  - **Rename**: Changing the `name` block or resource block name can cause recreation.
  - **Moving to New Compartment** or Region: Often forces re-creation.
  - **Dependencies**: Replacing a parent resource might cascade to child resources.
- **Always Check `terraform plan`** before applying in production.
- **Version Control**: Store `.tf` files in Git; ignore `.terraform/` and `*.tfstate*`.

---

## 9. Live demo / hands on part
You can begin this demo/hands-on exercise in the `sandbox/01-Terraform/` directory, where pre-configured Terraform code 
and necessary files for creating a dummy OCI Data Science model are provided.

### 9.1 Prerequisites
1. Terraform CLI installed.
1. An OCI provider block configured (with tenancy, user credentials, region, etc.).
1. A compartment OCID already known, stored `input_variables.tfvars`, variable `compartment_id`.

Example `provider.tf`:
```hcl
provider "oci" {
  region = var.region
  config_file_profile = var.oci_config_profile
}
```
Example `variables.tf`:
```hcl
variable "compartment_id" {
  description = "Sandbox compartment ID"
  type     = string
  nullable = false
}
variable "oci_config_profile" {
  description = "Profile from OCI configuration file"
  type     = string
  nullable = false
}
variable "region" {
  description = "OCI region e.g. us-ashburn-1"
  type     = string
  nullable = false
}
```
Example `input_variables.tfvar`:
```hcl
compartment_id = "ocid1.compartment.oc1..aaaaaaaafrobyownitwra7gqjv3hjsnsjraexuv42eujql2fax4hkg3ge7ta"
oci_config_profile = "DEFAULT"
region = "us-phoenix-1"
```

### 9.2 Create One Resource (OCI Data Science Project)
`main.tf`:
```hcl
resource "oci_datascience_project" "demo" {
  compartment_id = var.compartment_id
  display_name   = "MyFirstDataScienceProject"
}
```
When you run 
```commandline
terraform init
```
and
```commandline
terraform apply -var-file input_variables.tfvars
```
this will create a single Data Science Project in your compartment.

### 9.3 Modify Resource Block Name → Demonstrates Recreation

If we rename the resource block from `demo` to `demo_modified`, Terraform sees it as a new resource:

```hcl
resource "oci_datascience_project" "demo_modified" {
  compartment_id = var.compartment_id
  display_name   = "MyFirstDataScienceProject"
}
```

Try to change display name to see what happen. It causes in place update. No recreation needed as display name is updatable field.

### 9.4 Create Second Resource (OCI Data Science Model)
Next, introduce another resource for the Data Science Model, using the existing project ID.

Note: this code expects that you have `model` folder with your score.py and runtime.yaml
`main.tf`:
```hcl
resource "oci_datascience_project" "demo_modified" {
  compartment_id = var.compartment_id
  display_name   = "MyFirstDataScienceProject"
}

data "archive_file" "model" {
  type        = "zip"
  output_path = "model.zip"
  source_dir  = "model/"
}

resource "oci_datascience_model" "demo" {
  #Required
  artifact_content_length      = data.archive_file.model.output_size
  model_artifact = data.archive_file.model.output_path
  artifact_content_disposition = "attachment; filename=${data.archive_file.model.output_path}"
  compartment_id               = var.compartment_id
  project_id                   = oci_datascience_project.demo_modified.id
  display_name                 = "MyFirstDataScienceModel"
}
```
Now you have two resources: a Project and a Model.

### 9.5 Modification of an Immutable Field in the Model → Demonstrates Recreation
Some fields in the Data Science Model are immutable. Changing them forces the resource to be destroyed and re-created. For example, changing the project_id.
Let's demonstrate this change using change of project resource block name from `demo_modified` back to `demo`. This 
recreates project and therefore change project ID for model.

```hcl
resource "oci_datascience_project" "demo" {
  compartment_id = var.compartment_id
  display_name   = "MyFirstDataScienceProject"
}

data "archive_file" "model" {
  type        = "zip"
  output_path = "model.zip"
  source_dir  = "model/"
}

resource "oci_datascience_model" "demo" {
  #Required
  artifact_content_length      = data.archive_file.model.output_size
  model_artifact = data.archive_file.model.output_path
  artifact_content_disposition = "attachment; filename=${data.archive_file.model.output_path}"
  compartment_id               = var.compartment_id
  project_id                   = oci_datascience_project.demo.id
  display_name                 = "MyFirstDataScienceModel"
}
```
Terraform will destroy demo_model (the old one) and create a new demo_model with the updated project_id.

### 9.6 Create a Variable and Use It in a Resource
Let’s introduce a variable for the model’s display name. Add to variables.tf:

add this to `variables.tf`
```hcl
variable "model_version" {
  type    = string
  default = "v1"
}
```
Use it in `main.tf`:
```hcl
resource "oci_datascience_model" "demo" {
  #Required
  artifact_content_length      = data.archive_file.model.output_size
  model_artifact = data.archive_file.model.output_path
  artifact_content_disposition = "attachment; filename=${data.archive_file.model.output_path}"
  compartment_id               = var.compartment_id
  project_id                   = oci_datascience_project.demo.id
  display_name                 = "MyFirstDataScienceModel-${var.model_version}"
}
```
This shows how we can parameterize resources using a variable.

### 9.7 Create a Local That Calculates Something From the Variable and Use It
Define a local value that calculates a display name. For example:

```hcl
locals {
  model_name = "MyModel-${var.model_version}"
}

resource "oci_datascience_model" "demo" {
  #Required
  artifact_content_length      = data.archive_file.model.output_size
  model_artifact = data.archive_file.model.output_path
  artifact_content_disposition = "attachment; filename=${data.archive_file.model.output_path}"
  compartment_id               = var.compartment_id
  project_id                   = oci_datascience_project.demo.id
  display_name                 = local.model_name
}
```
Now we construct the display name from a local that references the model_version variable.

### 9.8 Create a Module With at Least One Input Variable and One Output
Before you start with creating module, let's clean up everything in cloud:
```commandline
terraform destroy -var-file input_variables.tfvars
```
Now, let’s encapsulate the Data Science resources in a module: 
1. Create a directory `modules/datascience`
1. Create file `modules/datascience/variables.tf` 
    ```hcl
    variable "compartment_id" {
      type = string
    }
    variable "model_version" {
      type    = string
    }
    ```
1. Create file `modules/datascience/main.tf` and move the content of old `main.tf` to it. 
2. Move directory `model` with its content to `modules/datascience/`  
3. Fix the path referencing moved directory in `archive_data` data source, field `source_dir`.
To reference root of the module, you can use `{path.module}`.
Result should look as below code:
    ```hcl
    resource "oci_datascience_project" "demo" {
      compartment_id = var.compartment_id
      display_name   = "MyFirstDataScienceProject"
    }
    
    data "archive_file" "model" {
      type        = "zip"
      output_path = "model.zip"
      source_dir  = "${path.module}/model/"
    }
    
    locals {
      model_name = "MyModel-${var.model_version}"
    }
    
    resource "oci_datascience_model" "demo" {
      #Required
      artifact_content_length      = data.archive_file.model.output_size
      model_artifact = data.archive_file.model.output_path
      artifact_content_disposition = "attachment; filename=${data.archive_file.model.output_path}"
      compartment_id               = var.compartment_id
      project_id                   = oci_datascience_project.demo.id
      display_name                 = local.model_name
    }
    ```
1. Create file `modules/datascience/outputs.tf`
```hcl
output "model_id" {
  value = oci_datascience_model.demo.id
}
```
### 9.9 Use the Module in Main + Output the Output of the Model
Finally, reference the module in your root `main.tf`, and output its result:
```hcl
module "datascience" {
  source = "./modules/datascience"
  compartment_id = var.compartment_id
  model_version = var.model_version
}

output "model_id" {
  value = module.datascience.model_id
}
```
When you run terraform apply, Terraform will:

Create or update the Data Science Project.
Create the Data Science Model using the module.
Output the model ID in the console.

## 10. Q&A and Next Steps

- Clarify any doubts about data sources, resources, or variable usage.
- Try building a multi-environment pipeline with modules.
- Explore more OCI services (VCN, LB, DB, etc.) and advanced Terraform constructs.

---

## Appendix: Useful Links

- **Terraform Installation**:
  - [Terraform Downloads](https://developer.hashicorp.com/terraform/downloads)
  - [Terraform Docs](https://developer.hashicorp.com/terraform)
- **OCI Provider Docs**: <https://registry.terraform.io/providers/oracle/oci/latest/docs>
- **OCI Configuration**:
  - [OCI Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- **Terraform Tutorials**:
  - <https://developer.hashicorp.com/terraform/tutorials>

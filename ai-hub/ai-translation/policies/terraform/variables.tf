variable "tenancy_ocid" {}
variable "compartment_ocid" {}
variable "region" {}

variable "availability_domain" {
  description = "Availabiliy domain"
  type        = string
}
# Network configuration CIDR

variable "create_new_vcn" {
  type    = bool
  default = true
}
variable "vcn_compartment_id" {
  description = "Compartment in which VCN, Subnets needs to be created or present"
  type        = string
}
variable "existing_vcn_id" {
  type    = string
  default = ""
}
variable "vcn_display_name" {
  default = "ai-solutions-vcn"
}
variable "vcn_cidr" {
  type    = string
  default = "10.1.0.0/16"
}
variable "existing_app_subnet_id" {
  type    = string
  default = ""
}
variable "app_subnet_cidr" {
  type    = string
  default = "10.1.2.0/24"
}
variable "existing_api_gw_subnet_id" {
  type    = string
  default = ""
}
variable "api_gw_subnet_cidr" {
  type    = string
  default = "10.1.1.0/24"
}

#IDCS Configuration
variable "identity_domain_id" {
  type    = string
  default = ""
}

#Vault Configuration to Store Identity App Client Secret
variable "vault_compartment_id" {
  description = "Compartment in which Vault is present"
  type        = string
}
variable "use_existing_vault" {
  type        = bool
  description = "Use existing vault"
  default     = true
}
variable "new_vault_display_name" {
  type        = string
  description = "Display name of the key vault"
  default     = ""
}
variable "vault_id" {
  description = "The vault where the database ADMIN password will be stored"
  type        = string
  default     = "none"
}
# Encryption key to be used when storing the ADMIN password
variable "key_id" {
  description = "Encryption key used for storing the password"
  type        = string
  default     = "none"
}

variable "project_ocid" {
  type = string
  description = "Data Science project in which resources needs to be created"
}

variable "log_group_ocid" {
  default = "ocid1.loggroup.oc1.iad.amaaaaaav66vvniaidjweu7sgg5qgx7yzri5yb4xw3qnqsg6szl2xdh7scka"
}
variable "log_ocid" {
  default = "ocid1.log.oc1.iad.amaaaaaav66vvnia3h4o6otedz4lz23zex6z2pei6yjqszb7zdfswaa5srca"
}

variable "shape" {
  default = "VM.Standard.E5.Flex"
}

variable "container_shape" {
  default = "CI.Standard.E4.Flex"
}
variable "memory_in_gbs" {
  default = 16
}
variable "ocpus" {
  default = 1
}

# The following variables are for job
variable "model_display_name" {
  default = "AI Hub Empty Model"
}

variable "job_display_name" {
  default = "AI Translation Job"
}

variable "container_display_name" {
  default = "AI Translation Container"
}

# The following variables are for deployment
variable "deployment_display_name" {
  default = "AI Translation Deployment"
}
variable "deployment_type" {
  default = "SINGLE_MODEL"
}
variable "deployment_bandwidth_mbps" {
  default = 10
}
variable "deployment_instance_count" {
  default = 1
}

# The following variables are for container instance

variable "model_backend" {
  default = "GenAI"
}

variable "model_name" {
  default = "meta.llama-3.3-70b-instruct"
}

variable "model_url" {
  default = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
}

variable "oci_cache_endpoint" {
  default = ""
}

variable "openai_api_key" {
  default = "API_KEY"
}

variable "translation_log_dir" {
  default = ""
}

variable "num_workers" {
  default = "1"
}


# locals variables
locals {
  vcn_id           = (var.create_new_vcn ? oci_core_vcn.aih_vcn[0].id : var.existing_vcn_id)
  app_subnet_id    = (var.create_new_vcn ? oci_core_subnet.app_oci_core_subnet[0].id : var.existing_app_subnet_id)
  api_gw_subnet_id = (var.create_new_vcn ? oci_core_subnet.api_gw_oci_core_subnet[0].id : var.existing_api_gw_subnet_id)

  image          = "dsmc://ai-translation:0.1.0-dev.16"
  digest         = "sha256:124f2834142305c3f53f63d0c3f8aa071b9180d50f1c8c17fbf66937f183804c"
  job_desc       = "Job for batch translation"
  job_entrypoint = ["python"]
  job_cmd        = ["/opt/app/batch.py"]
  md_desc        = "Deployment for AI translation Application"
  model_desc = "Data Science Model for AI Translation Deployment"
}



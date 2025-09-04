variable "tenancy_ocid" {}
variable "compartment_ocid" {}
variable "region" {}

variable "compartment_id" {
  description = "The selected compartment, by default the compartment in which stack is created"
  type        = string
}

variable "availability_domain" {
  description = "Availabiliy domain"
  type        = string
}
# Network configuration CIDR

variable "create_new_vcn" {
  type    = bool
  default = true
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

# ------------------------- Environment variables required for Document Extraction Application ----------------------------- #

# The following variables will be used by deployment.
variable "project_ocid" {
  default = "ocid1.datascienceproject.oc1.iad.amaaaaaav66vvniaklsknycfb6fso64knuk36egpsg3j5vasn3sveiuvdmna"
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
  # default = ""
  default = "aaav66vvniax2viamc6jbwfeujiowpxnuu7kioiyfyqwgdptkwthq2q-p.redis.us-ashburn-1.oci.oraclecloud.com"
}

variable "openai_api_key" {
  default = "sk-123456789"
}

variable "translation_log_dir" {
  default = "oci://a_bucket_for_qq@ociodscdev/data/translation/logs"
}

variable "num_workers" {
  default = "1"
}


# locals variables
locals {
  vcn_id           = (var.create_new_vcn ? oci_core_vcn.aih_vcn[0].id : var.existing_vcn_id)
  app_subnet_id    = (var.create_new_vcn ? oci_core_subnet.app_oci_core_subnet[0].id : var.existing_app_subnet_id)
  api_gw_subnet_id = (var.create_new_vcn ? oci_core_subnet.api_gw_oci_core_subnet[0].id : var.existing_api_gw_subnet_id)

  image          = "iad.ocir.io/ociodscdev/ai_translation:1.35"
  digest         = "sha256:9de28d33b7419b7f9ff42a6c2ad6792e904c3c815949f090e35e688cb23553fc"
  job_desc       = "Job for batch translation"
  job_entrypoint = ["python"]
  job_cmd        = ["/opt/app/batch.py"]
  model_id       = "ocid1.datasciencemodel.oc1.iad.amaaaaaav66vvniazwx42xndxz3kfemfpwht3unc3ib33tscln462gmuwiyq"
  md_desc        = "Deployment for AI translation Application"
}



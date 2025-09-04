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
variable "identity_domain_compartment_id" {
  description = "Compartment in which identity domain is present"
  type        = string
}
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

# ------------------------- Environment variables required for Document Extraction Application ----------------------------- #

# The following variables will be used by deployment.
variable "data_science_project_compartment_id" {
  description = "Compartment in which Data Science Project is present"
  type        = string
}
variable "project_ocid" {
  default = "ocid1.datascienceproject.oc1.iad.amaaaaaav66vvniadk4ecmjg7lhz65s54ulqdi4bcbk3u6e26bsjg4mekyjq"
}

variable "log_group_ocid" {
  default = "ocid1.loggroup.oc1.iad.amaaaaaav66vvnia76nyddgo3e6jfchcn6jhi7zvn7do3tlxh6ug4ye2hhgq"
}
variable "log_ocid" {
  default = "ocid1.log.oc1.iad.amaaaaaav66vvnias7eplqdggtirvefa7nc3vhg2gjlekblrwmylo35hpvta"
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

variable "container_display_name" {
  default = "AI Document Converter Instance"
}

# The following variables are for deployment
variable "deployment_display_name" {
  default = "AI Document Converter Deployment"
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

variable "multimodal_llm_provider" {
  default = "genai"
}
variable "genai_compartment_ocid" {
  default = "ocid1.tenancy.oc1..aaaaaaaahzy3x4boh7ipxyft2rowu2xeglvanlfewudbnueugsieyuojkldq"
}
variable "multimodal_model_name" {
  default = "openai.gpt-4.1-mini"
}
variable "multimodal_model_endpoint" {
  default = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
}
variable "multimodal_max_output_token" {
  default = 8192
}
variable "prompt_version" {
  default = 3
}


# locals variables
locals {
  vcn_id           = (var.create_new_vcn ? oci_core_vcn.aih_vcn[0].id : var.existing_vcn_id)
  app_subnet_id    = (var.create_new_vcn ? oci_core_subnet.app_oci_core_subnet[0].id : var.existing_app_subnet_id)
  api_gw_subnet_id = (var.create_new_vcn ? oci_core_subnet.api_gw_oci_core_subnet[0].id : var.existing_api_gw_subnet_id)

  image    = "iad.ocir.io/ociodscdev/document-converter:1.0.1"
  digest   = "sha256:2b07ac9bb1aeea99828a6ca8e1615edf083ff931f67e74295e51bb571bb49124"
  model_id = "ocid1.datasciencemodel.oc1.iad.amaaaaaav66vvnia44764hnygt3td7wme7ly3jrjupaal42m4uqcfebnkg2q"
  md_desc  = "Deployment for PDF to Markdown Converter"
}



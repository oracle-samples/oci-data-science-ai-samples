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

variable "use_existing_dynamic_group_and_policies" {
  type        = bool
  description = "Use existing Dynamic Group and Policies"
  default     = true
}

# ------------------------- Environment variables required for Document Extraction Application ----------------------------- #

# The following variables will be used by deployment.
variable "data_science_project_compartment_id" {
  description = "Compartment in which Data Science Project is present"
  type        = string
}
variable "project_ocid" {
  type        = string
  description = "Data Science project in which resources needs to be created"
}

variable "log_compartment_id" {
  description = "Compartment in which Logs are present"
  type        = string
}
variable "log_group_ocid" {
  type        = string
  description = "Log Group Ocid where logs will be stored"
  default = ""
}
variable "log_ocid" {
  type        = string
  description = "Log ocid where where logs needs to be stored"
  default = ""
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

variable "model_display_name" {
  default = "AI Document Converter Model"
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
  type        = string
  description = "Gen AI Compartment OCID"
}
variable "multimodal_model_name" {
  default = "openai.gpt-4.1-mini"
}
variable "multimodal_model_endpoint" {
  default = "https://inference.generativeai.us-ashburn-1.oci.oraclecloud.com"
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

  container_image = "iad.ocir.io/id1ytzpctjnn/dsmc/aisolution/ai_document_converter:0.1.0"
  image      = "dsmc://ai_document_converter:0.1.0"
  digest     = "sha256:73555609549a33bd5e06a1bc7b17c596067e72f0fb17babe054cf11152dbc060"
  model_desc = "Data Science Model for PDF to Markdown Converter Deployment"
  md_desc    = "Deployment for PDF to Markdown Converter"
}

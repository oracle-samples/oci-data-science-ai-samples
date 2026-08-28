variable "compartment_id" {
  description = "Compartment OCID used for both Compute Capacity Reservations and visible Data Science resources."
  type        = string
  nullable    = false
}

variable "profile" {
  description = "OCI profile for api_key or security_token SDK authentication. Ignored for instance_principal and resource_principal."
  type        = string
  default     = "DEFAULT"
}

variable "config_file" {
  description = "Optional OCI config file path. Leave empty to use the SDK default."
  type        = string
  default     = ""
}

variable "region" {
  description = "Optional OCI region override. Leave empty to use the configured region."
  type        = string
  default     = ""
}

variable "auth" {
  description = "OCI SDK authentication mode."
  type        = string
  default     = "api_key"

  validation {
    condition     = contains(["api_key", "security_token", "instance_principal", "resource_principal"], var.auth)
    error_message = "auth must be api_key, security_token, instance_principal, or resource_principal."
  }
}

variable "python_executable" {
  description = "Python executable that has a supported public OCI SDK installed."
  type        = string
  default     = "python3"
}

variable "discovery_script_path" {
  description = "Optional absolute path to discover_ds_capacity_reservations.py. Leave empty when this Terraform module remains beside the discovery script."
  type        = string
  default     = ""
}

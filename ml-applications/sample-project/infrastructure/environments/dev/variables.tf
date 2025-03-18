variable "environment_compartment_id" {
  description = "Application-Environment specific compartment ID"
  type     = string
  nullable = false
}
variable "environment_name" {
  description = "Name of environment e.g. dev, preprod"
  type = string
  nullable = false
}
variable "application_name" {
  description = "Name of ML Application"
  type     = string
  nullable = false
}
variable "custom_subnet_id" {
  description = "ID of an existing subnet which should be used by all the Pipeline Jobs. If not specified, VCN and Subnet are created."
  type = string
  default = ""
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
variable "mlapp_environment_compartment_id" {
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
  type     = string
  nullable = false
}

variable "custom_subnet_id" {
  description = "ID of an existing subnet which should be used by all the Pipeline Jobs. If not specified, VCN and Subnet are created."
  type = string
  default = ""
}
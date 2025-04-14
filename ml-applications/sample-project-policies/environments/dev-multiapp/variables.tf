variable "tenancy_id" {
  type     = string
  nullable = false
}
variable "external_subnet_compartment_id" {
  description = "If an existing subnet should be reused for ML App, provide compartment where the subnet is located. If not provided, there is expectation that subnet for ML App will be created in compartment where ML App is located."
  type        = string
  default     = ""
  nullable    = false
}
variable "environment_name" {
  type     = string
  nullable = false
}
variable "region" {
  type     = string
  nullable = false
}
variable "oci_config_profile" {
  type     = string
  default  = "DEFAULT"
  nullable = false
}
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
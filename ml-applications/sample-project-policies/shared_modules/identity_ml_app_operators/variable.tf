variable "tenancy_id" {
  type     = string
#   nullable = false
}

variable "app_compartment_id" {
  type = string
#   nullable = false
}

variable "application_name" {
  type = string
#   nullable = false
}

variable "environment_naming_suffix" {
  type    = string
#   nullable = false
}

variable "mlapps_tag_namespace" {
  type = string
  default = "MLApplications"
#   nullable = false
}

variable "app_team_group_id" {
  description = "ID of ML Application team identity group (or dynamic group - useful for build RP). If Boat group (Internal Oracle tenancy) is used, fill also 'boat_tenancy_id'"
  type = string
#   nullable = false
  default = ""
}

# do not use this variable directly in module Terraform code, use local.networking_compartment_id instead
variable "networking_compartment_id" {
  type = string
#   nullable = false
  default = ""
}

########################################################################################################################
# Only for remote group
########################################################################################################################
variable "app_team_group_tenancy_id" {
  type = string
  description = "Tenancy OCID where group is defined. This should be used only if the operator policies should be given to group from different tenancy. It cannot be used in combination with dynamic group."
  default = null
}
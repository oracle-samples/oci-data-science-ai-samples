variable "application_name" {
  type = string
#   nullable = false
}

variable "environment_name" {
  type = string
#   nullable = false
}

variable "tenancy_id" {
  type = string
#   nullable = false
}

variable "parent_compartment_id" {
  type = string
  default = ""
#   nullable = false
}

variable "external_subnet_compartment_id" {
  description = "If an existing subnet should be reused for ML App, provide compartment where the subnet is located. If not provided, there is expectation that subnet for ML App will be created in compartment where ML App is located."
  type     = string
#   nullable = false
  default = ""
}

variable "app_team_group_id" {
  description = "ID of ML Application team identity group. If Boat group (Internal Oracle tenancy) is used, fill also 'boat_tenancy_id'"
  type = string
#   nullable = false
  default = ""
}

variable "app_team_group_tenancy_id" {
  description = "Tenancy OCID where group is defined. This should be used only if the operator policies should be given to group from different tenancy."
  default = ""
#   nullable = false
}




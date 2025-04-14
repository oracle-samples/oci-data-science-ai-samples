variable "applications" {
  description = "List of applications with their attributes: name (name of application), operator_group_id (ID of operator group, must be defined but can be empty if operator policies are not needed), group_tenancy_id (ID of tenancy where operator group is defined, must be defined but can be empty if operator policies are not needed or group is in same tenancy as ML App)."
  type = list(object({
    name              = string
    operator_group_id = string
    group_tenancy_id  = string
  }))
  # nullable = false
}

variable "parent_compartment_id" {
  type = string
  description = "Compartment where the environment root compartment should be located. If not provided the tenancy_id is used."
}

variable "tenancy_id" {
  type = string
  description = "ID of OCI tenancy where ML Application environment should be created"
}

variable "environment_name" {
  type = string
  description = "Name of ML Application environment (e.g. dev, qa, preprod, production)"
#   nullable = false
}

variable "environment_root_compartment_name_prefix" {
  type = string
  description = "Name prefix of root environment compartment. The name of root environment is composed <environment_root_compartment_name_prefix>-<environment_name> or just <environment_name> if name prefix is not provided."
  default = ""
}
variable "external_subnet_compartment_id" {
  type = string
  default = ""
}
variable "network_in_shared_resources" {
  type = bool
  default = true
}


variable "tenancy_id" {
  type     = string
  # nullable = false
}

variable "app_compartment_id" {
  description = "Specifies root of compartment tree where ML Applications should be located. It can be directly application compartment or any parent of application compartment."
  type     = string
  # nullable = false
}

variable "external_subnet_compartment_id" {
  description = "If an existing subnet should be reused for ML App (which is out of application compartment), provide Id of compartment where the subnet is located. If not provided, subnet is expected to be in 'shared' compartment (for multiapp environment) or in application compartment."
  type     = string
  # nullable = false
  default = ""
}

variable "shared_resources_compartment_id" {
  description = "This is for multiapp environment where each environment has compartment for resources which are shared across all applications."
  type = string
  # nullable = false
  default = ""
}

variable "policy_name_suffix" {
  description = "Resource name suffix (like policy name suffix). Environment name is appended to result name suffix: <name_base>_<name_sufix>_<environment_name>"
  default = ""
  type     = string
  # nullable = false
}

variable "environment_name" {
  type     = string
  # nullable = false
}

variable "mlapps_tag_namespace" {
  type = string
  default = "MLApplications"
#   nullable = false
}

variable "mlapp_instance_id_tag" {
  description = "Defined tag name used for tenant isolation (resources belonging to certain ML App Instance should be tagged this tag)."
  type = string
  default = "MLApplicationInstanceId"
#   nullable = false
}

variable "mlapp_env_tag_namespace" {
  type = string
  default = "MLApplicationEnvironment"
#   nullable = false
}

variable "compartment_type_tag" {
  type = string
  default = "app"
}


variable "data_science_service_environment" {
  description = "Use only if non-production Data Science Service environment should be used (default is production). Allowed values: int, preprod, production"
  type    = string
  # nullable = false
  default = "production"
  validation {
    error_message = "Value can be one of: int, preprod, production."
    condition = can(regex("^(int|preprod|production)$", var.data_science_service_environment))
  }
}
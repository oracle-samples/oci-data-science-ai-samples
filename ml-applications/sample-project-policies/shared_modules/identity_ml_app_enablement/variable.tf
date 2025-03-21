# ML Application Provider tenancy ID (tenancy where ML Application will be created)
variable "tenancy_id" {
  type = string
#   nullable = false
}

variable "policy_name_suffix" {
  description = "Resource name suffix (like policy name suffix). Environment name is appended to result name suffix: <name_base>_<name_sufix>_<environment_name>"
  default = ""
  type     = string
#   nullable = false
}

variable "environment_name" {
  type     = string
  default = ""
#   nullable = false
}

variable "mlapp_env_tag_namespace" {
  type = string
  default = "MLApplications"
#   nullable = false
}

variable "compartment_type_tag" {
  description = "Defined tag name used for tenant isolation (resources belonging to certain ML App Instance should be tagged this tag)."
  type = string
  default = "CompartmentType"
#   nullable = false
}

variable "data_science_service_environment" {
  description = "Use only if non-production Data Science Service environment should be used (default is production). Allowed values: int, preprod, production"
  type    = string
#   nullable = false
  default = "production"
  validation {
    error_message = "Value can be one of: int, preprod, production."
    condition = can(regex("^(int|preprod|production)$", var.data_science_service_environment))
  }
}
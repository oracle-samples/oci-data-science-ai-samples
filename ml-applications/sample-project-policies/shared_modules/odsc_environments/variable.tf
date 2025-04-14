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
variable "environment_name" {
  description = "Name of ML Application environment (e.g. dev, int, preprod, prod)"
  type     = string
  default  = ""
#   nullable = false
}

variable "namespace_suffix" {
  type = string
  default = ""
#   nullable = false
}

variable "compartment_id" {
  type     = string
#   nullable = false
}
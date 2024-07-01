variable "kubernetes_nlb_id" {
  type = string
}
variable "subnet_name" {
  type = string
}
variable "compartment_id" {
  type = string
}

variable "existing_subnet_id" {
  type = string
}

variable "use_existing_subnet" {
  type = bool
}

variable "create_security_rules" {
  type = bool
}

variable "compartment_id" {
  type = string
}
variable "defined_tags" {
  type = map(string)
  default = {}
}
variable "subnet_id" {
  type = string
}
variable "ocir_path" {
  type = string
}
variable "authorized_groups" {
  type = list(string)
}
variable "name_suffix" {
  type = string
}

variable "tenancy_id" {
  type = string
}

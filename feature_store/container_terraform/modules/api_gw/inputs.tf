variable "compartment_id" {}
variable "ip" {}
variable "defined_tags" {
  type = map(string)
  default = {}
}
variable "subnet_id" {}
variable "function_id" {}

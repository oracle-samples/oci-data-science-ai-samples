variable "compartment_id" {}
variable "nlb_id" {}
variable "defined_tags" {
  type = map(string)
  default = {}
}
variable "subnet_id" {}
variable "function_id" {}

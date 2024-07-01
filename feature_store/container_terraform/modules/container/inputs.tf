
variable "compartment_ocid" {
  type = string
}

variable "subnet_ocid" {
  type = string
}

variable "mysql_ip" {
  type = string
}
variable "mysql_password" {
  type = string
}
variable "name_suffix" {
  type =  string
}
variable "tenancy_ocid" {
  type = string
}
variable "img_uri" {
  type = string
}
variable "container_shape" {
  type = string
}
variable "container_shape_flex_details" {
  type = map(string)
}

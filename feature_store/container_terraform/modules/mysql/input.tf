
variable "compartment_ocid" {}

variable "mysql_db_size" {
  default = 50
}

variable "subnet_id" {
}


variable "mysql_db_name" {
  default = "FeatureStoreMySqlDB"
}

variable "mysql_shape" {
  default = ""
}



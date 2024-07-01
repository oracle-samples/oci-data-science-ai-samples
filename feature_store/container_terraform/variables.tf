variable authorized_user_groups {
  description = "User group OCIDs authorized to access feature store environment"
  type = list(string)
}
#
variable function_img_ocir_url {
  description = "OCIR URL of the authorizer image exported from feature store marketplace listing"
  type = string
}

variable api_img_ocir_url {
  description = "OCIR URL of the api image exported from feature store marketplace listing"
  type = string
}

variable "tenancy_ocid" {
  type = string
  description = "OCID of the tenancy where the stack needs to be deployed"
}

variable "compartment_ocid" {
  type = string
  description = "OCID of the compartment where the stack needs to be deployed. If not provided, the stack will be deployed in the root compartment"
  default = ""
}

variable "region" {
  description = "Region in which the resources are to be provisioned"
  type = string
}

variable "mysql_shape" {
  description = "Shape of the MySQL instance"
  type = string
  default = "MySQL.VM.Standard.E3.1.8GB"
}

variable "container_shape" {
  description = "Shape of the feature store container instance"
  type = string
  default = "CI.Standard.E4.Flex"
}

variable "container_shape_flex_details" {
  description = "Flex shape details of the container instance"
  type = map(string)
  default = {
    "memory_in_gbs" = "16"
    "ocpus" = "1"
  }
}

variable "home_region" {
  default = ""
  description = "Home region of the tenancy. If not provided, the home region will be automatically populated using metadata from tenancyid"
  type = string
}

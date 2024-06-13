
terraform {
  required_version = ">= 1.0"
}

provider "oci" {
  region       = var.region
  tenancy_ocid = var.tenancy_ocid
#  auth = "SecurityToken"
#  config_file_profile = "DEFAULT"
}


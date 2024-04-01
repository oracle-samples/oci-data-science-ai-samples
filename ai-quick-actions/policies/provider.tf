
terraform {
  required_version = ">= 1.0"
}

provider "oci" {
  region       = var.region
  tenancy_ocid = var.tenancy_ocid
  ###### Uncomment the below if running locally using terraform and not as OCI Resource Manager stack #####
#  user_ocid = var.user_ocid
#  fingerprint = var.fingerprint
#  private_key_path = var.private_key_path
}

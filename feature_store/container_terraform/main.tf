resource "random_string" "suffix" {
  length = 4
  special = false
}

locals {
  compartment_id = var.compartment_ocid!=""?var.compartment_ocid:var.tenancy_ocid
}

module "networking" {
  source = "./modules/networking"
  compartment_ocid = "${local.compartment_id}"
}

module "mysql" {
  source = "./modules/mysql"
  compartment_ocid = "${local.compartment_id}"
  subnet_id = module.networking.private_subnet
  mysql_shape = var.mysql_shape
}

module "function" {
  source = "./modules/function"
  tenancy_id = var.tenancy_ocid
  authorized_groups = var.authorized_user_groups
  compartment_id = local.compartment_id
  ocir_path = var.function_img_ocir_url
  subnet_id = module.networking.private_subnet
  name_suffix = random_string.suffix.id
  providers = {
    oci.home_region=oci.home_region
  }
}

module "container" {
  source = "./modules/container"
  compartment_ocid = local.compartment_id
  subnet_ocid = module.networking.private_subnet
  name_suffix = random_string.suffix.id
  tenancy_ocid = var.tenancy_ocid
  mysql_password = module.mysql.password
  mysql_ip = module.mysql.ip
  img_uri = var.api_img_ocir_url
  container_shape = var.container_shape
  container_shape_flex_details = var.container_shape_flex_details
  providers = {
    oci.home_region = oci.home_region
  }
}

module "api_gw" {
  source = "./modules/api_gw"
  compartment_id = local.compartment_id
  subnet_id = module.networking.public_subnet
  function_id = module.function.fn_id
  ip=module.container.ip
}

resource oci_identity_policy feature_store_policies {
  description = "FEATURE STORE: Policy allowing feature store to authenticate and authorize"
  name        = "feature_store_gw_${random_string.suffix.id}"
  compartment_id = var.tenancy_ocid
  statements = concat(module.api_gw.policies, module.function.policies, module.container.policies)
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
  provider = oci.home_region
}




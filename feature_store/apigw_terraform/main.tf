resource "random_string" "suffix" {
  length = 4
  special = false
}


locals {
  compartment_id = var.use_nlb_compartment?data.oci_network_load_balancer_network_load_balancer.nlb.compartment_id:var.compartment_id
}

data oci_network_load_balancer_network_load_balancer nlb {
  network_load_balancer_id = var.nlb_id
}

module "feature_store_networking" {
  source = "./modules/feature_store_networking"
  kubernetes_nlb_id = var.nlb_id
  compartment_id = local.compartment_id
  subnet_name = "fs-gw-subnet"
  existing_subnet_id = var.api_gw_subnet_id
  use_existing_subnet = !var.automatically_provision_apigw_subnet
  create_security_rules = var.create_security_rules
}

module "function" {
  source = "./modules/function"
  tenancy_id = var.tenancy_ocid
  authorized_groups = var.authorized_user_groups
  compartment_id = local.compartment_id
  ocir_path = var.function_img_ocir_url
  subnet_id = module.feature_store_networking.subnet_id
  name_suffix = random_string.suffix.id
  providers = {
    oci.home_region = oci.home_region
  }
}

module "api_gw" {
  source = "./modules/api_gw"
  compartment_id = local.compartment_id
  function_id = module.function.fn_id
  nlb_id = var.nlb_id
  subnet_id = module.feature_store_networking.subnet_id
}

resource oci_identity_policy feature_store_policies {
  description = "FEATURE STORE: Policy allowing feature store to authenticate and authorize"
  name        = "feature_store_gw_${random_string.suffix.id}"
  compartment_id = var.tenancy_ocid
  statements = concat(module.api_gw.policies, module.function.policies)
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
  provider = oci.home_region
}




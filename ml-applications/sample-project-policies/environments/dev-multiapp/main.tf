module "app_list" {
  source = "../../shared_modules/application_list"
}

module "multiapp-environment" {
  source = "../../shared_modules/multip_app_environment"
  environment_name = var.environment_name
  environment_root_compartment_name_prefix = "ml-apps"
  parent_compartment_id = var.tenancy_id
  tenancy_id = var.tenancy_id
  external_subnet_compartment_id = var.external_subnet_compartment_id
  network_in_shared_resources = false
  applications = module.app_list.applications
}

output "application_compartment_ids" {
  value = module.multiapp-environment.application_compartment_ids
}

output "environment_compartment_id" {
  value = module.multiapp-environment.environment_compartment_id
}

output "shared_compartment_id" {
  value = module.multiapp-environment.shared_compartment_id
}
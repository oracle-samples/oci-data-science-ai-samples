module "odsc_environments" {
    source = "../odsc_environments"
    data_science_service_environment = var.data_science_service_environment
}

locals {
    odsc_service_tenancy_id = module.odsc_environments.odsc_service_tenancy_id
    mlapp_type_suffix = module.odsc_environments.mlapp_type_suffix
}
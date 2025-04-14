module "infra-module" {
  source = "../../infra-module"

  mlapp_environment_compartment_id = var.environment_compartment_id
  environment_name                 = var.environment_name
  application_name                 = var.application_name

  custom_subnet_id = var.custom_subnet_id
}

module "test-data-module" {
  source           = "../../fetalrisk-testdata-module"

  compartment_id   = var.environment_compartment_id
  test_bucket_name = "test_data_${var.application_name}_${var.environment_name}"
}

output "subnet_id" {
  value = module.infra-module.subnet_id
}
output "data_science_project_id" {
  value = module.infra-module.data_science_project_id
}
output "data_science_log_group_id" {
  value = module.infra-module.data_science_log_group_id
}
output "data_science_pipeline_log_id" {
  value = module.infra-module.data_science_pipeline_log_id
}
output "model_deployment_access_log_id" {
  value = module.infra-module.model_deployment_access_log_id
}
output "model_deployment_predict_log_id" {
  value = module.infra-module.model_deployment_predict_log_id
}
output "schedule_log_id" {
  value = module.infra-module.schedule_log_id
}
data "oci_identity_compartment" "app" {
    id = var.environment_compartment_id
}
output "mlapps_tag_namespace" {
  value = data.oci_identity_compartment.app.freeform_tags["MlApplicationTagNamespaceName"]
}

# Test data
output "x_test_data" {
  value = "oci://${module.test-data-module.external_data_source_bucket_name}@${module.test-data-module.external_data_source_bucket_namespace}/${module.test-data-module.external_data_source_bucket_file_name}"
}
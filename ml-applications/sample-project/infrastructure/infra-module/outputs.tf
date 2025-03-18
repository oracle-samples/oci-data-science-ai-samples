output "subnet_id" {
  value = var.custom_subnet_id == "" ? oci_core_subnet.mlapp_env[0].id : var.custom_subnet_id
}
output "data_science_project_id" {
  value = oci_datascience_project.app_env.id
}
output "data_science_log_group_id" {
  value = oci_logging_log_group.mlapp_env.id
}
output "data_science_pipeline_log_id" {
  value = oci_logging_log.data_science_pipeline.id
}
output "model_deployment_access_log_id" {
  value = oci_logging_log.model_deployment_access.id
}
output "model_deployment_predict_log_id" {
  value = oci_logging_log.model_deployment_log.id
}
output "schedule_log_id" {
  value = oci_logging_log.schedule_log.id
}
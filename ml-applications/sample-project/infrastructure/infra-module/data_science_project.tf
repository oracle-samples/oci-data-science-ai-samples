resource "oci_datascience_project" "app_env" {
  description = "Data Science Project for application '${var.application_name}' in environment '${var.environment_name}'"
  compartment_id = var.mlapp_environment_compartment_id
  display_name = local.resource_basename
}

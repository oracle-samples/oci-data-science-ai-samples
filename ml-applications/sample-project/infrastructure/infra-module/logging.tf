# Log group and log resources

resource "oci_logging_log_group" "mlapp_env" {
  compartment_id = var.mlapp_environment_compartment_id
  display_name   = "${local.resource_basename}_log_group"
}

resource "oci_logging_log" "data_science_pipeline" {
  display_name = "${local.resource_basename}_pipeline_log"
  log_group_id = oci_logging_log_group.mlapp_env.id
  log_type     = "CUSTOM"
  is_enabled   = true
}

resource "oci_logging_log" "model_deployment_access" {
  display_name = "${local.resource_basename}_model_deployment_access_log"
  log_group_id = oci_logging_log_group.mlapp_env.id
  log_type     = "CUSTOM"
  is_enabled   = true
}

resource "oci_logging_log" "model_deployment_log" {
  display_name = "${local.resource_basename}_model_deployment_prediction_log"
  log_group_id = oci_logging_log_group.mlapp_env.id
  log_type     = "CUSTOM"
  is_enabled   = true
}


resource "oci_logging_log" "schedule_log" {
  display_name = "${local.resource_basename}_schedule_log"
  log_group_id = oci_logging_log_group.mlapp_env.id
  log_type     = "CUSTOM"
  is_enabled   = true
}
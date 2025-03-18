resource "oci_datascience_schedule" "test_schedule" {
  action {
    action_details {
      http_action_type = "INVOKE_ML_APPLICATION_PROVIDER_TRIGGER"
      ml_application_instance_view_id = var.app_instance.view_id
      trigger_ml_application_instance_view_flow_details {
        trigger_name = "TrainingTrigger"
      }
    }
    action_type = "HTTP"
  }
  compartment_id = var.app_impl.compartment_id
  display_name   = "ml-app-fetal-risk-schedule-${var.app_instance.id}"
  project_id     = var.app_impl.package_arguments.data_science_project_id
  trigger {
    #Required
    trigger_type = "INTERVAL"

    #Optional
    frequency = "DAILY"
    interval  = 1
    # this is only for testing purpose not to let scheduler tick for forever
    # time_end = timeadd(timestamp(), "24h")
    # this should be uncommented for production ready systems
    # is_random_start_time = true
  }

  #Optional
  defined_tags = {
    "${var.app_impl.package_arguments.mlapps_tag_namespace}.MlApplicationInstanceId" = var.app_instance.id
  }
  description = "Schedule for FetalRisk ML Application Instance ${var.app_instance.id}"
  log_details {
    #Required
    log_group_id = var.app_impl.package_arguments.data_science_log_group_id
    log_id       = var.app_impl.package_arguments.schedule_log_id
  }
}
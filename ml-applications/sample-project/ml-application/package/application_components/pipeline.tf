locals {
  ml_pipeline_name = "Training_ML_Pipeline"
  ingestion_step_name = "Ingestion"
  transformation_step_name = "Transformation"
  training_step_name = "Training"

  steps = {
    "step1" = {
      step_name = local.ingestion_step_name
      step_type = "ML_JOB"

      #Optional
      depends_on = []
      job_id = oci_datascience_job.ingestion_job.id
      step_configuration_maximum_runtime_in_minutes = 30
      environment_variables = {
      }
    }
    "step2" = {
      step_name = local.transformation_step_name
      step_type = "ML_JOB"

      #Optional
      depends_on = [local.ingestion_step_name]
      job_id =  oci_datascience_job.transformation_job.id
      step_configuration_maximum_runtime_in_minutes = 30
      environment_variables = {
      }
    }
    "step3" = {
      step_name = local.training_step_name
      step_type = "ML_JOB"

      #Optional
      depends_on = [local.transformation_step_name]
      job_id =  oci_datascience_job.training_job.id
      step_configuration_maximum_runtime_in_minutes = 30
      environment_variables = {
      }
    }
  }
}

resource "oci_datascience_pipeline" "test_pipeline" {
  #Required
  compartment_id = var.app_impl.compartment_id
  project_id = var.app_impl.package_arguments.data_science_project_id
  delete_related_pipeline_runs = true

  dynamic "step_details" {
    for_each = [for s in local.steps: {
      step_name = s.step_name
      step_type = s.step_type
      step_configuration_maximum_runtime_in_minutes = s.step_configuration_maximum_runtime_in_minutes
      depends_on = s.depends_on
      job_id = s.job_id
    }]
    content {
      #Required
      step_name = step_details.value["step_name"]
      step_type = step_details.value["step_type"]

      #Optional
      depends_on = step_details.value["depends_on"] == [] ? null : step_details.value["depends_on"]
      job_id = step_details.value["job_id"]
      step_configuration_details {
        maximum_runtime_in_minutes = step_details.value["step_configuration_maximum_runtime_in_minutes"]
      }
    }
  }
  #Optional
  configuration_details {
    #Required
    type = "DEFAULT"
    maximum_runtime_in_minutes = 90
  }

  display_name = local.ml_pipeline_name
  description = local.ml_pipeline_name

  log_configuration_details {
    enable_auto_log_creation = "false"
    enable_logging           = "true"
    log_group_id = var.app_impl.package_arguments.data_science_log_group_id
    log_id = var.app_impl.package_arguments.data_science_pipeline_log_id
  }
}

output "pipeline_id" {
  value = oci_datascience_pipeline.test_pipeline.id
}

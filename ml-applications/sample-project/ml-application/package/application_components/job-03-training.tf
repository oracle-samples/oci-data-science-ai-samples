resource oci_datascience_job training_job {
  compartment_id          = var.app_impl.compartment_id
  display_name            = "Training_ML_Job"
  delete_related_job_runs = true
  job_configuration_details {
    command_line_arguments     = "defaultParam"
    job_type                   = "DEFAULT"
    maximum_runtime_in_minutes = 30
    environment_variables = {
      "CONDA_ENV_TYPE" = "service"
      "CONDA_ENV_SLUG" = "automlx242_p38_cpu_x86_64_v1"

      "MODEL_COMPARTMENT_ID"  = var.app_impl.compartment_id
      "PROJECT_ID"            = var.app_impl.package_arguments.data_science_project_id

      "INPUT_FILE"   = "training/data.csv"
      "OS_NAMESPACE" = data.oci_objectstorage_namespace.this.namespace
      "MLAPPS_TAG_NAMESPACE" = var.app_impl.package_arguments.mlapps_tag_namespace
      "JOB_RUN_ENTRYPOINT": "training.sh"

      # Provided by trigger:
      # "INSTANCE_BUCKET_NAME"
      # "MODEL_DEPLOYMENT_ID"
    }
  }
  job_infrastructure_configuration_details {
    block_storage_size_in_gbs = local.training_job_block_storage_size
    job_infrastructure_type   = "STANDALONE"
    shape_name                = local.training_job_shape_name
    job_shape_config_details {
      memory_in_gbs = 16
      ocpus         = 4
    }
    subnet_id                 = var.app_impl.package_arguments.subnet_id
  }
  project_id = var.app_impl.package_arguments.data_science_project_id
  #If we wanted to create ML job with python script, please uncomment below code
  job_artifact                 = "./src/03-training_job.py"
  artifact_content_disposition = "attachment; filename=03-training_job.py"
}

output "training_job_id" {
  value = oci_datascience_job.training_job.id
}

resource oci_datascience_job transformation_job {
  compartment_id          = var.app_impl.compartment_id
  display_name            = "Transformation_ML_Job"
  delete_related_job_runs = true
  job_configuration_details {
    command_line_arguments     = "defaultParam"
    job_type                   = "DEFAULT"
    maximum_runtime_in_minutes = 30
    environment_variables = {
      "CONDA_ENV_TYPE" = "service"
      "CONDA_ENV_SLUG" = "automlx242_p38_cpu_x86_64_v1"

      "INPUT_FILE"   = "raw/data.csv"
      "OUTPUT_FILE"  = "training/data.csv"
      "OS_NAMESPACE" = data.oci_objectstorage_namespace.this.namespace

      # Provided by trigger:
      #  "INSTANCE_BUCKET_NAME"
    }
  }
  job_infrastructure_configuration_details {
    block_storage_size_in_gbs = local.transformation_job_block_storage_size
    job_infrastructure_type   = "STANDALONE"
    shape_name = local.transformation_job_shape_name
    job_shape_config_details {
      memory_in_gbs = 16
      ocpus         = 4
    }
    subnet_id                 = var.app_impl.package_arguments.subnet_id
  }
  project_id = var.app_impl.package_arguments.data_science_project_id
  #If we wanted to create ML job with python script, please uncomment below code
  job_artifact                 = "./src/02-transformation_job.py"
  artifact_content_disposition = "attachment; filename=02-transformation_job.py"
}

output "transformation_job_id" {
  value = oci_datascience_job.transformation_job.id
}

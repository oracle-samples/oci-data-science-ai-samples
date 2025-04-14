resource oci_datascience_job ingestion_job {
  compartment_id = var.app_impl.compartment_id
  display_name = "Ingestion_ML_Job"
  delete_related_job_runs = true
  job_configuration_details {
    command_line_arguments = "defaultParam"
    job_type = "DEFAULT"
    maximum_runtime_in_minutes = 30
    environment_variables = {
      "CONDA_ENV_TYPE" = "service"
      "CONDA_ENV_SLUG" = "automlx242_p38_cpu_x86_64_v1"

      "OS_NAMESPACE" = data.oci_objectstorage_namespace.this.namespace
      "OUTPUT_FILE" = "raw/data.csv"

      # Provided by trigger:
      #   EXTERNAL_DATA_SOURCE
      #   INSTANCE_BUCKET_NAME
    }
  }
  job_infrastructure_configuration_details {
    block_storage_size_in_gbs = local.ingestion_job_block_storage_size
    job_infrastructure_type   = "STANDALONE"
    shape_name                = local.ingestion_job_shape_name
    job_shape_config_details {
      memory_in_gbs = 16
      ocpus         = 4
    }
    subnet_id                 = var.app_impl.package_arguments.subnet_id
  }
  project_id = var.app_impl.package_arguments.data_science_project_id
  #If we wanted to create ML job with python script, please uncomment below code
  job_artifact = "./src/01-ingestion_job.py"
  artifact_content_disposition = "attachment; filename=01-ingestion_job.py"
}

output "ingestion_job_id" {
  value = oci_datascience_job.ingestion_job.id
}

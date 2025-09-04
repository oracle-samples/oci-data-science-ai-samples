# Job
resource "oci_datascience_job" "ai_job" {
  # Required
  display_name   = var.job_display_name
  description    = local.job_desc
  compartment_id = var.compartment_id
  project_id     = var.project_ocid

  job_configuration_details {
    job_type = "DEFAULT"
    environment_variables = {
      MODEL_BACKEND  = var.model_backend,
      MODEL_NAME     = var.model_name,
      MODEL_URL      = var.model_url
      OPENAI_API_KEY = var.openai_api_key,
    }
  }
  job_infrastructure_configuration_details {
    job_infrastructure_type = "STANDALONE"
    shape_name              = var.shape
    job_shape_config_details {
      memory_in_gbs = var.memory_in_gbs
      ocpus         = var.ocpus
    }
    block_storage_size_in_gbs = 50
    # subnet_id = var.subnet_app
    subnet_id = local.app_subnet_id
  }

  job_environment_configuration_details {
    job_environment_type = "OCIR_CONTAINER"
    image                = local.image
    image_digest         = local.digest
    entrypoint           = local.job_entrypoint
    cmd                  = local.job_cmd
  }

  # Logging
  job_log_configuration_details {
    enable_logging = true
    log_group_id   = var.log_group_ocid
    log_id         = var.log_ocid
  }

  timeouts {
    delete = "2m"
  }

}
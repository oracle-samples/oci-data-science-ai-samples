resource "oci_container_instances_container_instance" "ai_container_instance" {
  #Required
  availability_domain = var.availability_domain
  compartment_id      = var.vcn_compartment_id
  containers {
    #Required
    image_url = local.image

    #Optional
    environment_variables = {
      # OCI GenAI Service
      MODEL_BACKEND            = var.model_backend
      MODEL_NAME               = var.model_name
      MODEL_URL                = var.model_url
      OPENAI_API_KEY           = var.openai_api_key
      NUM_WORKERS              = var.num_workers
      TASK_STORE               = "TMPDIR"
      LOG_DIR                  = var.translation_log_dir
      PROJECT_COMPARTMENT_OCID = var.data_science_project_compartment_id
      PROCESSING_JOB_OCID      = oci_datascience_job.ai_job.id
      OCI_CACHE_ENDPOINT       = var.oci_cache_endpoint
      BACKEND_MD_URL           = oci_datascience_model_deployment.ai_deployment.model_deployment_url
    }
  }
  shape = var.container_shape
  shape_config {
    #Required
    ocpus = var.ocpus

    #Optional
    memory_in_gbs = var.memory_in_gbs
  }
  vnics {
    #Required
    subnet_id = local.app_subnet_id
    # private_ip = var.container_instance_private_ip
  }

  #Optional
  display_name = var.container_display_name
}

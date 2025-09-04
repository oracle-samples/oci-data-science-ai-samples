resource "oci_container_instances_container_instance" "ai_container_instance" {
  #Required
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  containers {
    #Required
    image_url = local.image

    #Optional
    environment_variables = {
      # OCI GenAI Service
      MODEL_BACKEND            = var.model_backend,
      MODEL_NAME               = var.model_name,
      MODEL_URL                = var.model_url
      OPENAI_API_KEY           = var.openai_api_key,
      NUM_WORKERS              = var.num_workers,
      TASK_STORE               = "TMPDIR",
      LOG_DIR                  = var.translation_log_dir,
      PROJECT_COMPARTMENT_OCID = var.compartment_ocid,
      PROCESSING_JOB_OCID      = oci_datascience_job.ai_job.id,
      OCI_CACHE_ENDPOINT       = var.oci_cache_endpoint,
      BACKEND_MD_URL           = oci_datascience_model_deployment.ai_deployment.model_deployment_url,
      http_proxy               = "http://10.68.69.53:80",
      https_proxy              = "http://10.68.69.53:80",
      no_proxy                 = "oraclecloud.com,artifactory.oci.oraclecorp.com,artifacthub-tip.oraclecorp.com,oraclecorp.com,oc-test.com,127.0.0.1,localhost,100.100.84.201,100.126.5.5,10.89.228.16,10.242.12.81,10.89.228.14,169.254.169.254"
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

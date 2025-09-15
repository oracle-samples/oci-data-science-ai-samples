resource "oci_container_instances_container_instance" "ai_container_instance" {
  #Required
  availability_domain = var.availability_domain
  compartment_id      = var.vcn_compartment_id
  containers {
    #Required
    image_url = local.image

    #Optional
    environment_variables = {
      MULTIMODAL_LLM_PROVIDER   = var.multimodal_llm_provider
      MULTIMODAL_MODEL_NAME     = var.multimodal_model_name
      MULTIMODAL_MODEL_ENDPOINT = var.multimodal_model_endpoint
      MAX_OUTPUT_TOKEN          = var.multimodal_max_output_token
      GENAI_COMPARTMENT_OCID    = var.genai_compartment_ocid
      PROMPT_VERSION            = var.prompt_version
      BACKEND_MD_URL            = oci_datascience_model_deployment.ai_deployment.model_deployment_url
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

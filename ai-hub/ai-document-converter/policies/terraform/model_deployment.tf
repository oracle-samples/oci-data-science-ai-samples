# Model deployment with custom network and scaling policy type = FIXED SIZE
resource "oci_datascience_model_deployment" "ai_deployment" {
  # Required
  display_name   = var.deployment_display_name
  description    = local.md_desc
  compartment_id = var.data_science_project_compartment_id
  project_id     = var.project_ocid

  model_deployment_configuration_details {
    deployment_type = var.deployment_type
    model_configuration_details {
      # Required
      instance_configuration {
        instance_shape_name = var.shape
        model_deployment_instance_shape_config_details {
          memory_in_gbs = var.memory_in_gbs
          ocpus         = var.ocpus
        }
        # Required for custom networking
        # subnet_id = var.subnet_ocid
        subnet_id = local.app_subnet_id
      }
      model_id       = oci_datascience_model.ai_model.id
      bandwidth_mbps = var.deployment_bandwidth_mbps
      scaling_policy {
        instance_count = var.deployment_instance_count
        policy_type    = "FIXED_SIZE"
      }
    }

    environment_configuration_details {
      image                          = local.image
      image_digest                   = local.digest
      environment_configuration_type = "OCIR_CONTAINER"
      # Environment variables are customized based on the AI app.
      environment_variables = {
        # OCI GenAI Service
        MULTIMODAL_LLM_PROVIDER       = var.multimodal_llm_provider
        MULTIMODAL_MODEL_NAME         = var.multimodal_model_name
        MULTIMODAL_MODEL_ENDPOINT     = var.multimodal_model_endpoint
        MAX_OUTPUT_TOKEN              = var.multimodal_max_output_token
        GENAI_COMPARTMENT_OCID        = var.genai_compartment_ocid
        PROMPT_VERSION                = var.prompt_version,
        MODEL_DEPLOY_CUSTOM_ENDPOINTS = "[{\"endpointURI\": \"/api/list\", \"httpMethods\": [\"GET\"]}, {\"endpointURI\": \"/api/convert\", \"httpMethods\": [\"POST\"]}, {\"endpointURI\": \"/api/convert/file\", \"httpMethods\": [\"POST\"]}, {\"endpointURI\": \"/mcp/\", \"httpMethods\": [\"POST\"], \"streaming\": true}]"
      }
    }
  }

  # Logging, use the same log group and log ocid to reduce the variables.
  dynamic "category_log_details" {
    for_each = (
      var.log_group_ocid != null && var.log_ocid != "" &&
      var.log_group_ocid != null && var.log_ocid != ""
    ) ? [1] : []

    content {
      access {
        log_group_id = var.log_group_ocid
        log_id       = var.log_ocid
      }
      predict {
        log_group_id = var.log_group_ocid
        log_id       = var.log_ocid
      }
    }
  }

  freeform_tags = {
    "ai-hub-solution-name"       = "PDF to markdown conversion"
    "ai_solution_playground_url" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/"
    "ai_solution_mcp_endpoint" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/mcp"
    "ai_solution_api_endpoint_list_apis" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/api/convert"
  }

  depends_on = [oci_identity_policy.ai_solution_policies]

}
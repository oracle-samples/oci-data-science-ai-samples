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
      image = local.image
      # image_digest                   = local.digest
      environment_configuration_type = "OCIR_CONTAINER"
      # Environment variables are customized based on the AI app.
      environment_variables = {
        # OCI GenAI Service
        MODEL_BACKEND                 = var.model_backend
        MODEL_NAME                    = var.model_name
        MODEL_URL                     = var.model_url
        OPENAI_API_KEY                = var.openai_api_key
        NUM_WORKERS                   = var.num_workers
        TASK_STORE                    = "TMPDIR",
        LOG_DIR                       = var.translation_log_dir
        PROJECT_COMPARTMENT_OCID      = var.data_science_project_compartment_id
        PROCESSING_JOB_OCID           = oci_datascience_job.ai_job.id
        OCI_CACHE_ENDPOINT            = var.oci_cache_endpoint
        MODEL_DEPLOY_CUSTOM_ENDPOINTS = "[{\"endpointURI\": \"/api/languages\", \"httpMethods\": [\"GET\"]}, {\"endpointURI\": \"/api/batch\", \"httpMethods\": [\"POST\"]}, {\"endpointURI\": \"/api/task\", \"httpMethods\": [\"GET\"]}, {\"endpointURI\": \"/api/translate\", \"httpMethods\": [\"GET\", \"POST\"]}, {\"endpointURI\": \"/api/translate\", \"httpMethods\": [\"POST\"], \"streaming\": true}, {\"endpointURI\": \"/mcp/\", \"httpMethods\": [\"POST\"], \"streaming\": true}]"
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
    "ai-hub-solution-name" = "LLM based translation"
    "ai_solution_playground_url" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/"
    "ai_solution_mcp_endpoint" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/mcp"
    "ai_solution_api_endpoint_list_apis" = "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/api/translate"
  }

}
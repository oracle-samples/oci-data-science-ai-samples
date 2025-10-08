output "base_url" {
  description = "Application Base URL"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}"
}

output "mcp_endpoint" {
  description = "MCP Endpoint"
  value       = "${oci_datascience_model_deployment.ai_deployment.model_deployment_url}/predictWithResponseStream/mcp/"
}

output "playground_ui" {
  description = "Playground UI"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}ui/playground"
}

output "api_reference" {
  description = "API Reference"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}ui/docs"
}

output "api_schema" {
  description = "API Schema"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}api/schema"
}

output "api_endpoint_default" {
  description = "API Endpoint - Translate"
  value       = "${oci_datascience_model_deployment.ai_deployment.model_deployment_url}/predictWithResponseStream/api/translate"
}

output "api_endpoint_batch" {
  description = "API Endpoint - Batch Translation Job"
  value       = "${oci_datascience_model_deployment.ai_deployment.model_deployment_url}/predict/api/batch"
}

output "api_endpoint_list_languages" {
  description = "API Endpoint - Supported Languages"
  value       = "${oci_datascience_model_deployment.ai_deployment.model_deployment_url}/predict/api/languages"
}

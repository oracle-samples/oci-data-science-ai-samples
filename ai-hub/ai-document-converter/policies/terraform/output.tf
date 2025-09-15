output "base_url" {
  description = "Application Base URL"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}"
}

output "mcp_endpoint" {
  description = "MCP Endpoint"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}mcp"
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
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}api/openapi.json"
}

output "api_endpoint_convert" {
  description = "API Endpoint - Convert PDF from Object Storage to Markdown"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}api/convert"
}

output "api_endpoint_convert_file" {
  description = "API Endpoint - Convert PDF uploaded as file to Markdown"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}api/convert/file"
}

output "api_endpoint_list_apis" {
  description = "API Endpoint - Supported APIs for Document Conversion"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}api/list"
}

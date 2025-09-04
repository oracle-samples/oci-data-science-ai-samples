output "app_url" {
  description = "Application URL"
  value       = "${oci_apigateway_deployment.ai_application_apigateway_deployment.endpoint}"
}
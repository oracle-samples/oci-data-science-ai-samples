resource "oci_identity_domains_app" "ai_application_confidential_app" {
  based_on_template {
    value         = "CustomWebAppTemplateId"
    well_known_id = "CustomWebAppTemplateId"
  }
  client_type               = "confidential"
  description               = "Confidential Application for AI Document Converter Application"
  display_name              = "ai__doc_converter_application_confidential_app_${random_string.randomstring.result}"
  schemas                   = ["urn:ietf:params:scim:schemas:oracle:idcs:App"]
  allowed_operations        = ["introspect"]
  idcs_endpoint             = data.oci_identity_domain.application_identity_domain.url
  active                    = true
  is_oauth_client           = true
  bypass_consent            = true
  allowed_grants            = ["authorization_code", "client_credentials", "urn:ietf:params:oauth:grant-type:jwt-bearer", "implicit"]
  all_url_schemes_allowed   = true
  redirect_uris             = ["https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/ui", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/ui/", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/ui/gradio", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/ui/playground", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/ui/docs", "https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/callback"]
  post_logout_redirect_uris = ["https://${oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname}/"]
  audience                  = oci_apigateway_gateway.ai_application_oci_apigateway_gateway.hostname
}

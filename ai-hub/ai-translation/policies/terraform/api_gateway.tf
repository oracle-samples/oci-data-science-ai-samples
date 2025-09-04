# API Gateway
resource "oci_apigateway_gateway" "ai_application_oci_apigateway_gateway" {
  compartment_id = var.compartment_id
  display_name   = "ai_application_api_gw_${random_string.randomstring.result}"
  endpoint_type  = "PUBLIC"
  response_cache_details {
    type = "NONE"
  }
  subnet_id = local.api_gw_subnet_id
}

# API Gateway Deployments
resource "oci_apigateway_deployment" "ai_application_apigateway_deployment" {
  compartment_id = var.compartment_id
  display_name   = "api-deployment${random_string.randomstring.result}"
  gateway_id     = oci_apigateway_gateway.ai_application_oci_apigateway_gateway.id
  path_prefix    = "/"
  specification {
    logging_policies {
      execution_log {
        log_level = "INFO"
      }
    }
    request_policies {
      authentication {
        is_anonymous_access_allowed = "true"
        token_auth_scheme           = "Bearer"
        token_header                = "token"
        type                        = "TOKEN_AUTHENTICATION"
        validation_failure_policy {
          client_details {
            type = "VALIDATION_BLOCK"
          }
          response_type = "CODE"
          scopes        = ["openid"]
          source_uri_details {
            type = "VALIDATION_BLOCK"
          }
          type                               = "OAUTH2"
          use_cookies_for_intermediate_steps = "true"
          use_cookies_for_session            = "true"
        }
        validation_policy {
          additional_validation_policy {
            issuers = ["https://identity.oraclecloud.com/"]
          }
          client_details {
            client_id                    = oci_identity_domains_app.ai_application_confidential_app.name
            client_secret_id             = oci_vault_secret.idcs_app_client_secret.id
            client_secret_version_number = "1"
            type                         = "CUSTOM"
          }
          max_cache_duration_in_hours = "1"
          source_uri_details {
            type = "DISCOVERY_URI"
            uri  = "${data.oci_identity_domain.application_identity_domain.url}/.well-known/openid-configuration"
          }
          type = "REMOTE_DISCOVERY"
        }
      }
      mutual_tls {
        is_verified_certificate_required = "false"
      }
    }
    routes {
      backend {
        type = "OAUTH2_LOGOUT_BACKEND"
      }
      logging_policies {
      }
      methods = ["GET"]
      path    = "/logout"
    }
    routes {
      backend {
        status = "200"
        type   = "STOCK_RESPONSE_BACKEND"
      }
      logging_policies {
      }
      methods = ["ANY"]
      path    = "/token"
      response_policies {
        header_transformations {
          set_headers {
            items {
              if_exists = "OVERWRITE"
              name      = "token"
              values    = ["$${request.auth[id_token]}"]
            }
            items {
              if_exists = "OVERWRITE"
              name      = "x-csrf-token"
              values    = ["$${request.auth[apigw_csrf_token]}"]
            }
          }
        }
      }
    }
    routes {
      backend {
        connect_timeout_in_seconds = "60"
        is_ssl_verify_disabled     = "false"
        read_timeout_in_seconds    = "10"
        send_timeout_in_seconds    = "10"
        type                       = "HTTP_BACKEND"
        url                        = "http://${data.oci_core_vnic.ai_application_container_instance_vnic.private_ip_address}:8080/$${request.path[req]}"
      }
      logging_policies {
      }
      methods = ["ANY"]
      path    = "/{req*}"
      response_policies {
        header_transformations {
          set_headers {
            items {
              name      = "X-CSRF-TOKEN"
              values    = ["$${request.auth[apigw_csrf_token]}"]
              if_exists = "OVERWRITE"
            }
          }
        }
      }
    }
  }
}


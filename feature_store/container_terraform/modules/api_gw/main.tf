locals {
  routes = data.oci_apigateway_api_deployment_specification.specs.routes
  ip = format("%s%s:21000%s","http://", var.ip, "/20230101")
  unique_paths = {for route in local.routes : route.path=> route.methods...}
  unique_paths_flattened = {for path, methods in local.unique_paths: path=>flatten(methods) }
  # we are doing it like this because of issues in escaping ${ character
  path_str = format("%s%s","$","{request.path[")
  path_map = {for path,methods in local.unique_paths: path=>replace(replace(tostring(path), "{", local.path_str),"}", "]}")}
  policies = length(regexall(".*tenancy.*", var.compartment_id)) > 0? ["allow any-user to use functions-family in tenancy where ALL {request.principal.type='ApiGateway'}"]:["allow any-user to use functions-family in compartment ${data.oci_identity_compartment.compartment.name} where ALL {request.principal.type='ApiGateway'}"]
}

data "oci_identity_compartment" "compartment" {
  id = var.compartment_id
}

resource oci_apigateway_api specs {
  display_name = "Feature Store API spec"
  compartment_id = var.compartment_id
  content = file("${path.module}/api.yaml")
  # data resource is not provisioned properly without this
  provisioner "local-exec" {
    command = "sleep 20"
  }
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}

data oci_apigateway_api_deployment_specification specs {
  api_id = oci_apigateway_api.specs.id
}
resource oci_apigateway_gateway fs_gateway {
  compartment_id = var.compartment_id
  display_name   = "FeatureStoreGateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = var.subnet_id
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}

resource oci_apigateway_deployment fs_deployment {
  display_name="Feature store api deployment"
  compartment_id = var.compartment_id

  gateway_id     = oci_apigateway_gateway.fs_gateway.id
  path_prefix    = "/20230101"
  specification {
    request_policies {
      cors {
        allowed_origins = ["*"]
        allowed_methods = ["*"]
        allowed_headers = ["*"]
        exposed_headers = ["*"]
        is_allow_credentials_enabled = false
        max_age_in_seconds = 0
      }
      authentication {
        is_anonymous_access_allowed = true
        type = "CUSTOM_AUTHENTICATION"
        function_id = var.function_id
        parameters = {
          "(request-target)" = "request.headers[path]"
          accept-language = "request.headers[accept-language]"
          authorization = "request.headers[authorization]"
          path = "request.headers[path]"
          host = "request.headers[host]"
          opc-request-id = "request.headers[opc-request-id]"
          x-date = "request.headers[x-date]"
          x-content-sha256 = "request.headers[x-content-sha256]"
          content-length = "request.headers[content-length]"
          content-type = "request.headers[content-type]"
        }
        validation_failure_policy {
          type = "MODIFY_RESPONSE"
          response_code = 401
          response_message = "Your request couldn't be authenticated"
        }
        cache_key = ["authorization"]
      }

      mutual_tls {
        is_verified_certificate_required = false
        allowed_sans = []
      }
    }
    logging_policies {
      execution_log {
        log_level = "INFO"
        is_enabled = true
      }
    }

    dynamic "routes" {
      for_each = local.unique_paths_flattened

      content {
        methods = routes.value
        path = routes.key
        backend {
          connect_timeout_in_seconds = 60
          read_timeout_in_seconds = 300
          send_timeout_in_seconds = 300
          type = "HTTP_BACKEND"
          url = format("%s%s", local.ip, local.path_map[routes.key])
          is_ssl_verify_disabled = true

        }
        request_policies {
          authorization{
            type = "AUTHENTICATION_ONLY"
          }
          header_transformations {
            set_headers {
              items {
                name = "subjectId"
                values = ["$${request.auth[subjectId]}"]
              }
            }
          }
        }
      }
    }
    dynamic "routes" {
      for_each = local.unique_paths_flattened

      content {
        methods = ["OPTIONS"]
        path = routes.key
        backend {
          type = "STOCK_RESPONSE_BACKEND"
          status = 200
          body = ""
        }
        request_policies {
          authorization {
            type = "ANONYMOUS"
          }
        }
      }
    }
  }
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}

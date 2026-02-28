# Create API Gateway for Secure Access
resource "oci_apigateway_gateway" "dco_audit_gateway" {
  compartment_id = var.compartment_ocid
  display_name   = "dco-access-audit-gateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = oci_core_subnet.dco_audit_subnet.id
}

# Define Deployment for API Gateway
resource "oci_apigateway_deployment" "dco_audit_deployment" {
  compartment_id = var.compartment_ocid
  gateway_id     = oci_apigateway_gateway.dco_audit_gateway.id
  display_name   = "dco-access-audit-deployment"
  path_prefix    = "/audit"

  specification {
    routes {
      path    = "/app/{path*}"
      methods = ["ANY"]
      backend {
        type = "HTTP_BACKEND"
        url  = "http://${oci_container_instances_container_instance.dco_audit_instance.vnics[0].private_ip_address}:8501/{path}"
      }
    }
  }
}
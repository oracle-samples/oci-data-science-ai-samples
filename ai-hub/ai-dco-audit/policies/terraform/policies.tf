# Create IAM Policy for Container Instance and API Gateway Access
resource "oci_identity_policy" "dco_audit_policy" {
  compartment_id = var.compartment_ocid
  name           = "dco-access-audit-policy"
  description    = "Policy for DCO Access Audit app resources"
  statements     = [
    "Allow service containerinstance to manage container-instances in compartment id ${var.compartment_ocid}",
    "Allow service apigateway to manage api-gateway in compartment id ${var.compartment_ocid}",
    "Allow group <your-group-name> to manage container-instances in compartment id ${var.compartment_ocid}",  # Replace with your IAM group
    "Allow group <your-group-name> to manage api-gateway in compartment id ${var.compartment_ocid}",  # Replace with your IAM group
    "Allow group <your-group-name> to use virtual-network-family in compartment id ${var.compartment_ocid}"  # Replace with your IAM group
  ]
}
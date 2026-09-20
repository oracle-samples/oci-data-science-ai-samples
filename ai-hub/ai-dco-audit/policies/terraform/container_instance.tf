# Create Container Instance for DCO Access Audit App
resource "oci_container_instances_container_instance" "dco_audit_instance" {
  compartment_id      = var.compartment_ocid
  availability_domain = "AD-1"  # Replace with your AD if different
  display_name        = "dco-access-audit-instance"
  shape               = "CI.STANDARD.E4.FLEX"  # Adjust based on needs
  shape_config {
    ocpus         = 2
    memory_in_gbs = 4
  }

  vnics {
    subnet_id        = oci_core_subnet.dco_audit_subnet.id
    display_name     = "dco-audit-vnic"
    is_public_ip_assigned = true  # Needed for initial access, later routed via API Gateway
  }

  containers {
    display_name = "dco-access-audit-container"
    image_url    = var.image_ocid  # Format: <region>.ocir.io/<tenancy>/<repo>/dco-access-audit:latest
    resource_config {
      memory_limit_in_gbs = 4
      vcpus_limit         = 2
    }
    ports {
      port     = 8501
      protocol = "TCP"
      is_host  = true
    }
  }

  state = "ACTIVE"
}
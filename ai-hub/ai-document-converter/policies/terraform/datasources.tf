data "oci_core_services" "all_oci_services" {
  filter {
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }
}

data "oci_identity_availability_domains" "get_availability_domains" {
  compartment_id = var.compartment_ocid
}

data "oci_identity_domain" "application_identity_domain" {
  domain_id = trimspace(var.identity_domain_id)
  lifecycle {
    precondition {
      condition     = var.identity_domain_id != null
      error_message = "Existing domain id must be provided when using an existing domain."
    }
  }
}

data "oci_core_vnic" "ai_application_container_instance_vnic" {
  vnic_id = oci_container_instances_container_instance.ai_container_instance.vnics[0].vnic_id
}
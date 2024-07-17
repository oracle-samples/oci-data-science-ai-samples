
locals {
  policies = ["allow dynamic-group ${oci_identity_dynamic_group.functions_dg.name} to {AUTHENTICATION_INSPECT,GROUP_MEMBERSHIP_INSPECT} in tenancy"]
}

resource "oci_identity_dynamic_group" "functions_dg" {
  compartment_id = var.tenancy_id
  description    = "FEATURESTORE: Allow Oci functions to inspect identity"
  matching_rule  = "All {resource.type = 'fnfunc', resource.id = '${oci_functions_function.test_function.id}'}"
  name           = "Feature_Store_Authorizer_${var.name_suffix}"
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
  provider = oci.home_region
}

resource oci_functions_application test_application {
  compartment_id = var.compartment_id
  subnet_ids = [var.subnet_id]
  display_name = "Feature_Store_Authorizer_${var.name_suffix}"
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}

resource oci_functions_function test_function {
  application_id = oci_functions_application.test_application.id
  display_name = "authorizer"
  image = var.ocir_path
  memory_in_mbs = "256"
  config = {
    "GROUP_IDS" : "${join("," ,var.authorized_groups)}"
  }
  provisioned_concurrency_config {
    strategy = "CONSTANT"
    count = 20
  }
  defined_tags = var.defined_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}


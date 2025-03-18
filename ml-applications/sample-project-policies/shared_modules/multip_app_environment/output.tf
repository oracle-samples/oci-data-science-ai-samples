output "tenancy_id" {
  value = var.tenancy_id
}

output "parent_compartment_id" {
  value = local.parent_compartment_id_resolved
}

output "environment_compartment_id" {
  value = oci_identity_compartment.environment_root.id
}

output "shared_compartment_id" {
  value = oci_identity_compartment.shared.id
}

output "application_compartment_ids" {
  value = {
    for app_name, compartment in oci_identity_compartment.apps :
    app_name => compartment.id
  }
}
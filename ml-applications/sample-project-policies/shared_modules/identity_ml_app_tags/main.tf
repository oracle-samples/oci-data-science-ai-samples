locals {
  environment_name_resolved = var.environment_name != null && var.environment_name != "" ? join("", [upper(substr(var.environment_name, 0, 1)), lower(substr(var.environment_name, 1, length(var.environment_name) - 1))] ) : ""
  namespace_suffix_resolved = var.namespace_suffix != null && var.namespace_suffix != "" ? join("", [upper(substr(var.namespace_suffix, 0, 1)), lower(substr(var.namespace_suffix, 1, length(var.namespace_suffix) - 1))] ) : ""
  suffix = "${local.namespace_suffix_resolved}${local.environment_name_resolved}"
  description_suffix = var.environment_name != "" ? "for environment ${var.environment_name}" : ""
  compartment_type_app = "app"
  compartment_type_shared = "shared"
}


resource "oci_identity_tag_namespace" "ml_applications" {
  #Required
  compartment_id = var.compartment_id
  description    = "ML Applications related tag namespace ${local.description_suffix}"
  name = "MlApplications${local.suffix}"

  #Optional
  is_retired = false
}

resource "oci_identity_tag" "ml_application_instance" {
  #Required
  description = "ID of ML Application Instance which tagged resource belongs to. Tag serves for tenant isolation - tag-based policies."
  name        = "MlApplicationInstanceId"
  tag_namespace_id = oci_identity_tag_namespace.ml_applications.id

  #Optional
  is_cost_tracking = false
  is_retired       = false
}

resource "oci_identity_tag_namespace" "ml_application_environment" {
  #Required
  compartment_id = var.compartment_id
  description    = "ML Application environment related tag namespace ${local.description_suffix}"
  name = "MlApplicationEnvironment${local.suffix}"

  #Optional
  is_retired = false
}


resource "oci_identity_tag" "compartment_type" {
  #Required
  description      = "Tag distinguishing the purpose of the compartment (e.g., for an application or shared resources)"
  name             = "CompartmentType"
  tag_namespace_id = oci_identity_tag_namespace.ml_application_environment.id

  # Define validator for enumerated values
  validator {
    validator_type = "ENUM"
    values = [
      local.compartment_type_app,
      local.compartment_type_shared
    ]
  }

  #Optional
  is_cost_tracking = false
  is_retired       = false
}

output "mlapps_namespace" {
  value = oci_identity_tag_namespace.ml_applications.name
}

output "mlapp_instance_tag" {
  value = oci_identity_tag.ml_application_instance.name
}

output "mlapp_env_namespace" {
  value = oci_identity_tag_namespace.ml_application_environment.name
}

output "compartment_type_tag" {
  value = oci_identity_tag.compartment_type.name
}

output "compartment_type_app" {
  value = local.compartment_type_app
}

output "compartment_type_shared" {
  value = local.compartment_type_shared
}
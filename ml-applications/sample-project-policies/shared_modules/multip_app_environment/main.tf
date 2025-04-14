locals {
  environment_root_name = coalesce(var.environment_root_compartment_name_prefix, "") != "" ? "${var.environment_root_compartment_name_prefix}-${var.environment_name}" : var.environment_name
  parent_compartment_id_resolved = coalesce(var.parent_compartment_id, var.tenancy_id)
}

resource "oci_identity_compartment" "environment_root" {
  name        = local.environment_root_name
  description = "Base compartment for multi-MLApplication environment '${var.environment_name}'"
  compartment_id = local.parent_compartment_id_resolved
}

module "identity_ml_app_tags" {
  source = "../../shared_modules/identity_ml_app_tags"
  environment_name = var.environment_name
  compartment_id = oci_identity_compartment.environment_root.id
}

resource "oci_identity_compartment" "apps" {
  depends_on = [oci_identity_compartment.environment_root, module.identity_ml_app_tags]
  for_each = { for comp in var.applications : comp.name => comp }

  name        = each.key
  description = "Compartment for ML Application '${each.key}' in environment '${var.environment_name}'"
  compartment_id   = oci_identity_compartment.environment_root.id

  defined_tags = {"${module.identity_ml_app_tags.mlapp_env_namespace}.${module.identity_ml_app_tags.compartment_type_tag}"= "${module.identity_ml_app_tags.compartment_type_app}"}
  freeform_tags = {
    # For app deployments to be able to get environment specific tag namespace
    "MlApplicationTagNamespaceName" = "${module.identity_ml_app_tags.mlapps_namespace}"
  }
}


resource "oci_identity_compartment" "shared" {
  depends_on = [oci_identity_compartment.environment_root, module.identity_ml_app_tags]

  name        = "shared"
  description = "Compartment for OCI resources which should be shared by all ML Applications in environment '${var.environment_name}'"
  compartment_id   = oci_identity_compartment.environment_root.id

  defined_tags = {"${module.identity_ml_app_tags.mlapp_env_namespace}.${module.identity_ml_app_tags.compartment_type_tag}"= "${module.identity_ml_app_tags.compartment_type_shared}"}
}



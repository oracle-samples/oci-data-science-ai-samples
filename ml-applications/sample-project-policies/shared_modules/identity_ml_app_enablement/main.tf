locals {
  environment_name_resolved = var.environment_name != null && var.environment_name != "" ? var.environment_name : ""
  description_suffix = local.environment_name_resolved != "" ? "for environment '${local.environment_name_resolved}'" : "in tenancy"
  policy_name_suffix = var.policy_name_suffix != null && var.policy_name_suffix != "" ? "${var.policy_name_suffix}_${local.environment_name_resolved}" : local.environment_name_resolved
}

resource "oci_identity_policy" "ml-application-enablement" {
  compartment_id = var.tenancy_id
  description    = "Endorse policies ensuring ML Application enablement '${local.description_suffix}'"
  name           = "ml_applications_enablement_${local.policy_name_suffix}"
  statements     = [
    "Define tenancy DataScienceTenancy as ${local.odsc_service_tenancy_id}",
    "Endorse any-user to manage orm-stacks in tenancy DataScienceTenancy where all { request.principal.type='datasciencemlapp${local.mlapp_type_suffix}', request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app' }",
    "Endorse any-user to manage orm-jobs in tenancy DataScienceTenancy where all { request.principal.type='datasciencemlappimpl${local.mlapp_type_suffix}', request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app' }",
    "Endorse any-user to use orm-stacks in tenancy DataScienceTenancy where all { request.principal.type='datasciencemlappimpl${local.mlapp_type_suffix}', request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app' }",
  ]
}


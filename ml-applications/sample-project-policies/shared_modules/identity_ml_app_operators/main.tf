locals {
  remote_tenancy = coalesce(var.app_team_group_tenancy_id, "NO_TENANCY")
  dynamic_prefix = strcontains(var.app_team_group_id, "dynamicgroup") ? "dynamic-" : ""

  statements = [
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage data-science-family in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to use tag-namespaces in tenancy where target.tag-namespace.name='${var.mlapps_tag_namespace}'",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage secrets in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to use virtual-network-family in compartment id ${local.networking_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage object-family in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage logging-family in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to inspect tenancies in tenancy",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to inspect compartments in tenancy",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage metrics in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage alarms in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage ons-family in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage functions-family in compartment id ${var.app_compartment_id}",
    "Allow ${local.dynamic_prefix}group id ${var.app_team_group_id} to manage cloudevents-rules in compartment id ${var.app_compartment_id}",
  ]
  x_tenancy_statements = [
    "Define tenancy remote_tenancy as ${local.remote_tenancy})",
    "Define group remote_app_team_group as ${var.app_team_group_id}",

    "Admit group remote_app_team_group of tenancy remote_tenancy to manage data-science-family in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to use tag-namespaces in tenancy where target.tag-namespace.name='${var.mlapps_tag_namespace}'",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage secrets in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to use virtual-network-family in compartment id ${local.networking_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage object-family in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage logging-family in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to inspect tenancies in tenancy",
    "Admit group remote_app_team_group of tenancy remote_tenancy to inspect compartments in tenancy",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage metrics in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage alarms in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage ons-family in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage functions-family in compartment id ${var.app_compartment_id}",
    "Admit group remote_app_team_group of tenancy remote_tenancy to manage cloudevents-rules in compartment id ${var.app_compartment_id}",
  ]
}

resource "oci_identity_policy" "ml_apps_operators" {
  compartment_id = var.tenancy_id # must be tenancy ID because some statements have "in tenancy" scope
  description    = "Policies for ML Application operators"
  name           = "ml_app_operators_${local.name_suffix}"
  statements     = var.app_team_group_tenancy_id == null ? local.statements : local.x_tenancy_statements
}
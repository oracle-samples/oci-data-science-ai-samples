module "identity_ml_app_runtime_policies" {
  source = "../../shared_modules/identity_ml_app_runtime"
  depends_on = [oci_identity_compartment.environment_root, module.identity_ml_app_tags]
  environment_name = var.environment_name
  tenancy_id = var.tenancy_id
  app_compartment_id = oci_identity_compartment.environment_root.id
  mlapps_tag_namespace = module.identity_ml_app_tags.mlapps_namespace
  mlapp_instance_id_tag = module.identity_ml_app_tags.mlapp_instance_tag
  mlapp_env_tag_namespace = module.identity_ml_app_tags.mlapp_env_namespace
  compartment_type_tag = module.identity_ml_app_tags.compartment_type_tag
  # if subnet is in 'shared' compartment, we should provided ID of shared compartment
  shared_resources_compartment_id = var.network_in_shared_resources ? oci_identity_compartment.shared.compartment_id : ""
  external_subnet_compartment_id = var.external_subnet_compartment_id
}

module "identity_ml_app_enablement_policies" {
  source = "../../shared_modules/identity_ml_app_enablement"
  environment_name = var.environment_name
  tenancy_id = var.tenancy_id
  mlapp_env_tag_namespace = module.identity_ml_app_tags.mlapp_env_namespace
  compartment_type_tag = module.identity_ml_app_tags.compartment_type_tag
}

module "identity_ml_app_operator_policies" {
  depends_on = [oci_identity_compartment.environment_root, module.identity_ml_app_tags]
  for_each = {
    for app in var.applications :
    app.name => app
    if app.operator_group_id != null && app.operator_group_id != ""
  }
  source = "../../shared_modules/identity_ml_app_operators"
  tenancy_id = var.tenancy_id
  environment_naming_suffix = var.environment_name
  app_compartment_id = oci_identity_compartment.environment_root.id
  app_team_group_id = each.value.operator_group_id
  app_team_group_tenancy_id = each.value.group_tenancy_id
  mlapps_tag_namespace = module.identity_ml_app_tags.mlapps_namespace
  application_name = each.value.name
}
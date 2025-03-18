module "identity_ml_app_tags" {
  source = "../../shared_modules/identity_ml_app_tags"
  namespace_suffix = var.application_name
  environment_name = var.environment_name
  compartment_id = var.tenancy_id
}

resource "oci_identity_compartment" "app" {
  depends_on = [module.identity_ml_app_tags]

  name           = "ml-app-${var.application_name}-${var.environment_name}"
  description    = "Compartment for ML Application '${var.application_name}'"
  compartment_id = var.tenancy_id

  defined_tags = {"${module.identity_ml_app_tags.mlapp_env_namespace}.${module.identity_ml_app_tags.compartment_type_tag}" = "${module.identity_ml_app_tags.compartment_type_app}"}
  freeform_tags = {
    # For app deployments to be able to get environment specific tag namespace
    "MlApplicationTagNamespaceName" = "${module.identity_ml_app_tags.mlapps_namespace}"
  }
}

module "identity_ml_app_runtime_policies" {
  source = "../../shared_modules/identity_ml_app_runtime"
  depends_on = [oci_identity_compartment.app]

  tenancy_id = var.tenancy_id
  app_compartment_id = oci_identity_compartment.app.id
  policy_name_suffix = var.application_name
  environment_name = var.environment_name
  external_subnet_compartment_id = var.subnet_compartment_id

  mlapps_tag_namespace = module.identity_ml_app_tags.mlapps_namespace
  mlapp_env_tag_namespace = module.identity_ml_app_tags.mlapp_env_namespace
  mlapp_instance_id_tag = module.identity_ml_app_tags.mlapp_instance_tag
  compartment_type_tag = module.identity_ml_app_tags.compartment_type_tag
}

module "identity_ml_app_enablement" {
  source = "../../shared_modules/identity_ml_app_enablement"
  depends_on = [oci_identity_compartment.app]

  policy_name_suffix = var.application_name
  environment_name = var.environment_name
  tenancy_id = var.tenancy_id
  mlapp_env_tag_namespace = module.identity_ml_app_tags.mlapp_env_namespace
  compartment_type_tag = module.identity_ml_app_tags.compartment_type_tag
}

module "identity_ml_app_operators" {
  count = var.app_team_group_id != "" ? 1 : 0 # This will be created only if dev team group ID is provided
  source = "../../shared_modules/identity_ml_app_operators"
  depends_on = [oci_identity_compartment.app]

  tenancy_id = var.tenancy_id
  app_compartment_id = oci_identity_compartment.app.id
  app_team_group_id = var.app_team_group_id
  application_name = var.application_name
  environment_naming_suffix = var.environment_name
  app_team_group_tenancy_id = var.app_team_group_tenancy_id
}

output "tenancy_id" {
  value = var.tenancy_id
}

output "environment_compartment_id" {
  value = oci_identity_compartment.app.id
}

output "mlapps_tag_namespace" {
  value = module.identity_ml_app_tags.mlapps_namespace
}



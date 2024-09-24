resource "oci_identity_dynamic_group" "aqua-dynamic-group" {
  count = local.is_admin_policies_only ? 0 : 1
  compartment_id = var.tenancy_ocid
  description    = "Data Science Aqua Dynamic Group"
  name           = var.aqua_dg_name
  matching_rule =  local.is_resource_policy_required? local.aqua_dg_match: local.aqua_admin_only_dg_match
}

resource "oci_identity_dynamic_group" "distributed_training_job_runs" {
  count          = local.is_resource_policy_required ? 1 : 0
  compartment_id = var.tenancy_ocid
  description    = "Data Science Distributed Training Job Runs Group"
  name           = var.distributed_training_dg_name
  matching_rule = "any {all {resource.type='datasciencejobrun',resource.compartment.id='${var.compartment_ocid}'}}"
}


locals {
  is_admin_policies_only = var.deployment_type == "Only admin policies"
  is_resource_policy_only = var.deployment_type == "Only resource policies"
  is_all_policies = var.deployment_type == "All policies"
  is_resource_policy_required = var.deployment_type != "Only admin policies"
  // Aqua dg matching rules
  aqua_admin_only_dg_match = "all {resource.type='datasciencenotebooksession'}"
  aqua_dg_match = "any {all {resource.type='datasciencenotebooksession',resource.compartment.id='${var.compartment_ocid}'}, all {resource.type='datasciencemodeldeployment',resource.compartment.id='${var.compartment_ocid}'}, all {resource.type='datasciencejobrun',resource.compartment.id='${var.compartment_ocid}'}}"
  is_compartment_tenancy = length(regexall(".*tenancy.*", var.compartment_ocid)) > 0
  compartment_policy_string = local.is_compartment_tenancy ? "tenancy" :  "compartment id ${var.compartment_ocid}"
  policy_tenancy = local.is_resource_policy_only? var.compartment_ocid : var.tenancy_ocid

  tenancy_map = ({
    oc1: "ocid1.tenancy.oc1..aaaaaaaax5hdic7ya6r5rxsgpifff4l6xdxzltnrncdzp3m75ubbvzqqzn3q"
    oc8: "ocid1.tenancy.oc8..aaaaaaaa2nxkxxix6ngdcifswvrezlmuylejvse4x6oa2ub4wfaduyz547wa"
  })
  user_realm = element(split(".", var.tenancy_ocid), 2)
  service_tenancy_ocid = lookup(local.tenancy_map, local.user_realm, "UNKNOWN")

  // These are encompassing policies that will be created in the tenancy. When the user selects "All policies" these policies will be created.
  aqua_all_policies = local.is_all_policies? [
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-model-deployments in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-models in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to use logging-family in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-jobs in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-job-runs in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to use virtual-network-family in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read resource-availability in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-projects in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-notebook-sessions in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-modelversionsets in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read buckets in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read objectstorage-namespaces in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to inspect compartments in tenancy"
    ]:[]

  // Aqua resource only policies. These policies will be created in a specific compartment. When the user selects "Only resource policies" these policies will be created.
  aqua_resource_only_policies = local.is_resource_policy_only? [
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-model-deployments in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-models in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to use logging-family in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-jobs in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-job-runs in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to use virtual-network-family in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read resource-availability in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-projects in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-notebook-sessions in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage data-science-modelversionsets in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read buckets in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to read objectstorage-namespaces in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to inspect compartments in ${local.compartment_policy_string}"
  ]:[]

  policies_to_use = local.is_admin_policies_only ? [] : local.is_resource_policy_only ? local.aqua_resource_only_policies : local.aqua_all_policies

  all_buckets = concat(var.user_model_buckets, var.user_data_buckets)
  bucket_names = join(", ", formatlist("target.bucket.name='%s'", local.all_buckets))
  bucket_names_oss = join(", ", formatlist("all{target.bucket.name='%s', any {request.permission='OBJECT_CREATE', request.permission='OBJECT_INSPECT'}}", local.all_buckets))
  dt_jr_policies = local.is_resource_policy_required?[
    "Allow dynamic-group id ${oci_identity_dynamic_group.distributed_training_job_runs[0].id} to use logging-family in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.distributed_training_job_runs[0].id} to manage data-science-models in ${local.compartment_policy_string}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.distributed_training_job_runs[0].id} to read data-science-jobs in ${local.compartment_policy_string}"
  ]: []
  dt_jr_policies_target_buckets = local.is_resource_policy_required? [
    "Allow dynamic-group id ${oci_identity_dynamic_group.distributed_training_job_runs[0].id} to manage objects in ${local.compartment_policy_string} where any {${local.bucket_names}}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.distributed_training_job_runs[0].id} to read buckets in ${local.compartment_policy_string} where any {${local.bucket_names}}"
  ]: []
  aqua_policies_target_buckets = local.is_resource_policy_required?[
    "Allow dynamic-group id ${oci_identity_dynamic_group.aqua-dynamic-group[0].id} to manage object-family in ${local.compartment_policy_string} where any {${local.bucket_names_oss}}"
  ]:[]

}

resource "oci_identity_policy" "aqua-policy" {
  compartment_id = local.policy_tenancy
  description    = "Data Science Aqua Policies"
  name           = var.aqua_policy_name
  statements     = length(local.bucket_names) > 0 ? concat(local.policies_to_use, local.aqua_policies_target_buckets): local.policies_to_use
}

resource "oci_identity_policy" "distributed_training_job_runs_policy" {
  count          = local.is_resource_policy_required ? 1 : 0
  compartment_id = local.policy_tenancy
  description    = "Distributed Training Job Runs Policies"
  name           = var.distributed_training_policy_name
  statements     = length(local.bucket_names) > 0 ? concat(local.dt_jr_policies, local.dt_jr_policies_target_buckets) : local.dt_jr_policies
}



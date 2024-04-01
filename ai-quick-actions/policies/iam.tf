resource "oci_identity_dynamic_group" "aqua-dynamic-group" {
  compartment_id = var.tenancy_ocid
  description    = "Data Science Aqua Dynamic Group"
  name           = var.aqua_dg_name
  matching_rule = "any {all {resource.type='datasciencenotebooksession',resource.compartment.id='${var.compartment_ocid}'}, all {resource.type='datasciencemodeldeployment',resource.compartment.id='${var.compartment_ocid}'}, all {resource.type='datasciencejobrun',resource.compartment.id='${var.compartment_ocid}'}}"
}

resource "oci_identity_dynamic_group" "distributed_training_job_runs" {
  compartment_id = var.tenancy_ocid
  description    = "Data Science Distributed Training Job Runs Group"
  name           = var.distributed_training_dg_name
  matching_rule = "any {all {resource.type='datasciencejobrun',resource.compartment.id='${var.compartment_ocid}'}}"
}

locals {
  aqua_policies = [
    "Define tenancy datascience as ocid1.tenancy.oc1..aaaaaaaax5hdic7ya6r5rxsgpifff4l6xdxzltnrncdzp3m75ubbvzqqzn3q",
    "Endorse any-user to read data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}",
    "Endorse any-user to inspect data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}",
    "Endorse any-user to read object in tenancy datascience where ALL {target.compartment.name='service-managed-models', target.bucket.name='service-managed-models'}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-model-deployments in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-models in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to use logging-family in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-jobs in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-job-runs in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to use virtual-network-family in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read resource-availability in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-projects in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-notebook-sessions in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-modelversionsets in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read buckets in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read objectstorage-namespaces in compartment ${data.oci_identity_compartment.current_compartment.name}"
    ]
  aqua_root_policies = [
    "Define tenancy datascience as ocid1.tenancy.oc1..aaaaaaaax5hdic7ya6r5rxsgpifff4l6xdxzltnrncdzp3m75ubbvzqqzn3q",
    "Endorse any-user to read data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}",
    "Endorse any-user to inspect data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}",
    "Endorse any-user to read object in tenancy datascience where ALL {target.compartment.name='service-managed-models', target.bucket.name='service-managed-models'}",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-model-deployments in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-models in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to use logging-family in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-jobs in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-job-runs in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to use virtual-network-family in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read resource-availability in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-projects in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-notebook-sessions in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to manage data-science-modelversionsets in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read buckets in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.aqua-dynamic-group.name} to read objectstorage-namespaces in tenancy"
  ]
  use_aqua_root_policies = length(regexall(".*tenancy.*", var.compartment_ocid)) > 0
  all_buckets = concat(var.user_model_buckets, var.user_data_buckets)
  bucket_names = join(", ", formatlist("target.bucket.name='%s'", local.all_buckets))
  dt_jr_policies = [
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to use logging-family in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to manage data-science-models in compartment ${data.oci_identity_compartment.current_compartment.name}",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to read data-science-jobs in compartment ${data.oci_identity_compartment.current_compartment.name}"
  ]
  dt_jr_policies_target_buckets = [
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to manage objects in compartment ${data.oci_identity_compartment.current_compartment.name} where any {${local.bucket_names}}",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to read buckets in compartment ${data.oci_identity_compartment.current_compartment.name} where any {${local.bucket_names}}"
  ]
  dt_jr_root_policies = [
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to use logging-family in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to manage data-science-models in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to read data-science-jobs in tenancy"
  ]
  dt_jr_root_policies_target_buckets = [
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to manage objects in tenancy where any {${local.bucket_names}}",
    "Allow dynamic-group ${oci_identity_dynamic_group.distributed_training_job_runs.name} to read buckets in tenancy where any {${local.bucket_names}}"
  ]
}

resource "oci_identity_policy" "aqua-policy" {
  compartment_id = var.tenancy_ocid
  description    = "Data Science Aqua Policies"
  name           = var.aqua_policy_name
  statements     = local.use_aqua_root_policies ? local.aqua_root_policies : local.aqua_policies
}

resource "oci_identity_policy" "distributed_training_job_runs_policy" {
  compartment_id = var.tenancy_ocid
  description    = "Distributed Training Job Runs Policies"
  name           = var.distributed_training_policy_name
  statements     = local.use_aqua_root_policies ? length(local.bucket_names) > 0 ? concat(local.dt_jr_root_policies, local.dt_jr_root_policies_target_buckets) : local.dt_jr_root_policies : length(local.bucket_names) > 0 ? concat(local.dt_jr_policies, local.dt_jr_policies_target_buckets ) : local.dt_jr_policies
}



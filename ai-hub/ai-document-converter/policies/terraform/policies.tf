resource "oci_identity_dynamic_group" "ai_solution_group" {
  count = var.use_existing_dynamic_group_and_policies ? 0 : 1
  compartment_id = var.tenancy_ocid
  description    = "Dynamic Group for AI Solution"
  name           = "ai_solution_group-${random_string.randomstring.result}"
  matching_rule  = "any { all {resource.type='datasciencemodeldeployment',resource.compartment.id='${var.data_science_project_compartment_id}'}, all {resource.type='apigateway',resource.compartment.id='${var.compartment_id}'},all {resource.type='computecontainerinstance',resource.compartment.id='${var.vcn_compartment_id}'},all {resource.type='datasciencejobrun', resource.compartment.id='${var.data_science_project_compartment_id}'}}"
}

resource "oci_identity_policy" "ai_solution_policies" {
    count = var.use_existing_dynamic_group_and_policies ? 0 : 1
    compartment_id = "${var.tenancy_ocid}"
    description    = "Dynamic group policies for AI Solution"
    name           = "ai_solution_policies-${random_string.randomstring.result}"
    statements     = [
    "allow service datascience to use virtual-network-family in compartment id ${var.vcn_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to manage secret-family in compartment id ${var.vault_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to use virtual-network-family in compartment id ${var.vcn_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to use logging-family in compartment id ${var.log_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to manage data-science-family in compartment id ${var.data_science_project_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to manage generative-ai-family in tenancy",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to read repos in tenancy",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group[0].name} to use objects in compartment id ${var.compartment_id}"
  ]
    depends_on = [oci_identity_dynamic_group.ai_solution_group]
}
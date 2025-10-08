resource "oci_identity_dynamic_group" "ai_solution_group" {
  compartment_id = var.tenancy_ocid
  description    = "Dynamic Group for AI Solution"
  name           = "ai_solution_group-${random_string.randomstring.result}"
  matching_rule  = "any { all {resource.type='datasciencemodeldeployment',resource.compartment.id='${var.data_science_project_compartment_id}'}, all {resource.type='apigateway',resource.compartment.id='${var.compartment_ocid}'},all {resource.type='computecontainerinstance',resource.compartment.id='${var.vcn_compartment_id}'},all {resource.type='datasciencejobrun', resource.compartment.id='${var.data_science_project_compartment_id}'}}"
}

locals {
  policies = [
    "allow service datascience to use virtual-network-family in compartment id ${var.vcn_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to manage secret-family in compartment id ${var.vault_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to use virtual-network-family in compartment id ${var.vcn_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to use logging-family in compartment id ${var.log_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to manage data-science-family in compartment id ${var.data_science_project_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to manage generative-ai-family in tenancy",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to manage generative-ai-family in compartment id ${var.data_science_project_compartment_id}",
    "allow dynamic-group ${oci_identity_dynamic_group.ai_solution_group.name} to read repos in tenancy"
  ]
}

resource "oci_identity_policy" "ai_solution_policies" {
    compartment_id = "${var.tenancy_ocid}"
    description    = "Dynamic group policies for AI Solution"
    name           = "ai_solution_policies-${random_string.randomstring.result}"
    statements     = local.policies
    depends_on = [oci_identity_dynamic_group.ai_solution_group]
}
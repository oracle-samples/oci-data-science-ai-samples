locals {
  # List of applications with their attributes
  applications = [
    {
      name = "fetal-risk",
      # operator_boat_group_id = "xxx",
      operator_group_id = "ocid1.group.oc1..xxx",
      # provide only if the tenancy is different from tenancy where ML App is located. DO NOT PROVIDE tenancy of ML Application here.
      group_tenancy_id = null,
    },
    {
      name = "cardiovascular-risk",
      operator_group_id = "ocid1.group.oc1..yyy", #"yyy",
      # provide only if the tenancy is different from tenancy where ML App is located. DO NOT PROVIDE tenancy of ML Application here.
      group_tenancy_id = null,
    },
    # other applications ....
  ]
}

output "applications" {
  value = local.applications
}





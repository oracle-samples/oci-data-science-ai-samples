# OC1 only
locals {
  # OCI Data Science service tenancies for particular Data Science service environments in OC1
  # if non-OC1 real is needed variables data_science_tenancy_id and
  odsc_service_environment = {
    int = {
      type_suffix = "int"
      tenancy_id = "ocid1.tenancy.oc1..aaaaaaaaw3qvo5if3zvylobhcqprfzk62uyuo6mx5gmuwj5ump7jbe257rya"
    }
    preprod = {
      type_suffix = "pre"
      tenancy_id = "ocid1.tenancy.oc1..aaaaaaaad3w5enmveyue5ov4aj66xyqwryuqnftn5k55obgy6ocukuiwfo3a"
    }
    production = {
      type_suffix = ""
      tenancy_id = "ocid1.tenancy.oc1..aaaaaaaax5hdic7ya6r5rxsgpifff4l6xdxzltnrncdzp3m75ubbvzqqzn3q"
    }
  }

  odsc_env_details = lookup(local.odsc_service_environment, var.data_science_service_environment, null)
  type_suffix = local.odsc_env_details["type_suffix"]
  odsc_tenancy_id = local.odsc_env_details["tenancy_id"]
}

output "mlapp_type_suffix" {
  value = local.type_suffix
}

output "odsc_service_tenancy_id" {
  value = local.odsc_tenancy_id
}

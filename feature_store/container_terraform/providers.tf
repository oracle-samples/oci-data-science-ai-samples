data "oci_identity_tenancy" "tenant_details" {
  tenancy_id = var.tenancy_ocid
}

data "oci_identity_regions" "home_region" {
  filter {
    name   = "key"
    values = [data.oci_identity_tenancy.tenant_details.home_region_key]
  }
  count = var.home_region != "" ? 0 : 1
}

locals {
  home_region = var.home_region != "" ? var.home_region : lookup(data.oci_identity_regions.home_region.0.regions.0, "name")
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
}

provider "oci" {
  alias        = "home_region"
  tenancy_ocid = var.tenancy_ocid
  region       = local.home_region
}

locals {
  env_vars = {
    "MYSQL_USER" = "admin"
    "MYSQL_PASSWORD" = var.mysql_password
    "MYSQL_DB_URL" = "jdbc:mysql://${var.mysql_ip}:3306/FeatureStore?createDatabaseIfNotExist=true"
    "MYSQL_AUTH_TYPE" = "BASIC"
    "MYSQL_VAULT_SECRET_NAME"= ""
    "MYSQL_VAULT_OCID" = ""
  }
  policies = ["Allow dynamic-group ${oci_identity_dynamic_group.fs_container_dynamic_group.name} to read compartments in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.fs_container_dynamic_group.name} to read data-catalog-family in tenancy",
    "Allow dynamic-group ${oci_identity_dynamic_group.fs_container_dynamic_group.name} to inspect data-science-models in tenancy"]
}

data "oci_identity_availability_domains" "ADs" {
  compartment_id = var.compartment_ocid
}

resource "oci_identity_dynamic_group" "fs_container_dynamic_group" {
  compartment_id = var.tenancy_ocid
  name = format("%s%s", "fs-container-service-dynamic-group_", var.name_suffix)
  description = "dynamic group for feature store container"
  matching_rule = "ALL {resource.type='computecontainerinstance'}"
  provider = oci.home_region
}

resource "oci_identity_dynamic_group" "container_dynamic_group" {
  compartment_id = var.tenancy_ocid
  name = format("%s%s", "container-service-dynamic-group_", var.name_suffix)
  description = "dynamic group for container service"
  matching_rule = "ALL {resource.type='computecontainerinstance'}"
  provider = oci.home_region
}


resource "oci_identity_policy" "container_dynamic_group_policy" {
  compartment_id = var.tenancy_ocid
  name = format("%s%s", "container-service-read-repos-policy_", var.name_suffix)
  description = "dynamic group policy for container service"
  statements = ["Allow dynamic-group ${oci_identity_dynamic_group.container_dynamic_group.name} to read repos in tenancy"]
  provider = oci.home_region
}

resource "oci_container_instances_container_instance" "fs_container" {
  availability_domain = lookup(data.oci_identity_availability_domains.ADs.availability_domains[0], "name")
  compartment_id      = var.compartment_ocid
  shape               = var.container_shape
  display_name        = "Feature store API server"
  shape_config {
    ocpus = 1
    memory_in_gbs = 16
  }
  vnics {
      subnet_id           = "${var.subnet_ocid}"
      skip_source_dest_check = true
      is_public_ip_assigned = false
  }
  containers {
    image_url = var.img_uri
    environment_variables = local.env_vars
    display_name = "feature-store-container"
  }
}

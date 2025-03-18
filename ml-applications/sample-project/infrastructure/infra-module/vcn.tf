resource "oci_core_vcn" "mlapp_env" {
  count          = var.custom_subnet_id == "" ? 1 : 0
  cidr_block     = "10.0.0.0/16"
  compartment_id = var.mlapp_environment_compartment_id
  display_name   = local.resource_basename
}

resource "oci_core_subnet" "mlapp_env" {
  count             = var.custom_subnet_id == "" ? 1 : 0
  cidr_block        = "10.0.0.0/24"
  display_name      = local.resource_basename
  compartment_id    = var.mlapp_environment_compartment_id
  vcn_id            = oci_core_vcn.mlapp_env[0].id
  security_list_ids = [oci_core_vcn.mlapp_env[0].default_security_list_id]
  route_table_id    = oci_core_vcn.mlapp_env[0].default_route_table_id
  dhcp_options_id   = oci_core_vcn.mlapp_env[0].default_dhcp_options_id
}

data "oci_core_services" "oss" {
  filter {
    name   = "name"
    values = [".*All.*Services.*"]
    regex  = true
  }
}

resource "oci_core_service_gateway" "mlapp_env" {
  count          = var.custom_subnet_id == "" ? 1 : 0
  compartment_id = var.mlapp_environment_compartment_id

  services {
    service_id = data.oci_core_services.oss.services[0]["id"]
  }

  vcn_id       = oci_core_vcn.mlapp_env[0].id
  display_name = local.resource_basename
}

resource "oci_core_security_list" "mlapp_env" {
  count          = var.custom_subnet_id == "" ? 1 : 0
  compartment_id = var.mlapp_environment_compartment_id
  vcn_id         = oci_core_vcn.mlapp_env[0].id
  display_name   = local.resource_basename

  egress_security_rules {
    destination_type = "SERVICE_CIDR_BLOCK"
    destination      = data.oci_core_services.oss.services[0]["cidr_block"]
    protocol         = "all"
    stateless        = true
  }
}

resource "oci_core_nat_gateway" "mlapp_env" {
  count          = var.custom_subnet_id == "" ? 1 : 0
  compartment_id = var.mlapp_environment_compartment_id
  vcn_id         = oci_core_vcn.mlapp_env[0].id
  display_name   = local.resource_basename
}

resource "oci_core_default_route_table" "mlapp_env_default" {
  count                      = var.custom_subnet_id == "" ? 1 : 0
  manage_default_resource_id = oci_core_vcn.mlapp_env[0].default_route_table_id
  display_name               = local.resource_basename

  route_rules {
    destination       = data.oci_core_services.oss.services[0]["cidr_block"]
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.mlapp_env[0].id
  }
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_nat_gateway.mlapp_env[0].id
  }
}
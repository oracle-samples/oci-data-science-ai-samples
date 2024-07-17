locals {
  vcn_cidr_block = "10.0.0.0/16"
  calculate_cidr_block = var.vcn_ocid == "" ? false : true
  vcn_subnets = local.calculate_cidr_block ? data.oci_core_subnets.subnets[0].subnets : null
  subnet_ids =  local.calculate_cidr_block?[for subnet in local.vcn_subnets: subnet.id] : []
  cidrs = local.calculate_cidr_block? sort([for subnet in data.oci_core_subnet.subnets_dets: subnet.cidr_block]) : ["10.0.0.0/28"]

  last_cidr_block = split("/",local.cidrs["${(length(local.cidrs)-1)}"])

  parent_last_cidr_block_size = "${tonumber(local.last_cidr_block[1])-1}"<=26? "${tonumber(local.last_cidr_block[1])-1}" : 26
  parent_last_cidr_block = "${local.last_cidr_block[0]}/${tostring(local.parent_last_cidr_block_size)}"
  cidr_block_size = 28-tonumber(local.parent_last_cidr_block_size)
  private_cidr_block = cidrsubnet(local.parent_last_cidr_block, local.cidr_block_size, 1)
  public_cidr_block = cidrsubnet(local.parent_last_cidr_block, local.cidr_block_size, 2)
  internet_gateway_id = oci_core_internet_gateway.gateway.id
  vcn_id = oci_core_vcn.vcn.id
  subnet_names = {
    "private" = "fs-private-subnet"
    "public" = "fs-public-subnet"
  }
  subnets = {
    private = oci_core_subnet.private_subnet
    public = oci_core_subnet.public_subnet
  }
}

data "oci_core_subnets" "subnets" {
  count = local.calculate_cidr_block? 1 : 0
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_ocid
}

data "oci_core_subnet" "subnets_dets" {
  for_each = toset(local.subnet_ids)
  subnet_id = "${each.key}"
}

resource "oci_core_vcn" "vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = local.vcn_cidr_block
  display_name   = "feature-store-vcn"
}

resource "oci_core_subnet" "private_subnet" {
  display_name   =  local.subnet_names.private
  cidr_block     = local.private_cidr_block
  compartment_id = var.compartment_ocid
  prohibit_public_ip_on_vnic = true
  vcn_id         = local.vcn_id
  route_table_id = oci_core_route_table.private_route_table.id
  security_list_ids = [oci_core_security_list.security_list_private.id]
}

resource "oci_core_subnet" "public_subnet" {
  display_name =  local.subnet_names.public
  cidr_block     = local.public_cidr_block
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  route_table_id = oci_core_route_table.public_route_table.id
  security_list_ids = [oci_core_security_list.security_list_public.id]
  lifecycle {
    ignore_changes = [cidr_block]
  }
}

resource "oci_core_internet_gateway" "gateway" {
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  enabled = true
}

resource "oci_core_route_table" "public_route_table" {
  display_name = format("%s-route-table", local.subnet_names.public)
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  route_rules {
    network_entity_id = local.internet_gateway_id
    destination = "0.0.0.0/0"

  }
}
data "oci_core_services" "services" {}
resource "oci_core_service_gateway" "service_gateway" {
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  services {
    service_id = data.oci_core_services.services.services[1].id
  }
}

resource "oci_core_route_table" "private_route_table" {
  display_name = format("%s-route-table", local.subnet_names.private)
  compartment_id = "${var.compartment_ocid}"
  vcn_id         = local.vcn_id
  route_rules {
    network_entity_id = oci_core_service_gateway.service_gateway.id
    destination_type = "SERVICE_CIDR_BLOCK"
    destination = data.oci_core_services.services.services[1].cidr_block
  }
}
resource "oci_core_security_list" "security_list_public" {
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  display_name = format("%s-sec-rules",local.subnet_names.public)
  egress_security_rules {
    destination = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    protocol = "6"
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
  }
}

resource "oci_core_security_list" "security_list_private" {
  compartment_id = var.compartment_ocid
  vcn_id         = local.vcn_id
  display_name = format("%s-sec-rules", local.subnet_names.private)
  ingress_security_rules {
    protocol = "6"
    source   = local.public_cidr_block
    tcp_options {
        max=21000
        min=21000
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = local.private_cidr_block
    tcp_options {
      max=3306
      min=3306
    }
  }
  egress_security_rules {
    destination_type = "SERVICE_CIDR_BLOCK"
    destination = data.oci_core_services.services.services[1].cidr_block
    protocol    = "all"
  }
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
}



locals {
  subnet_ids = [for subnet in data.oci_core_subnets.subnets.subnets: subnet.id]
  cidrs = sort([for subnet in data.oci_core_subnet.subnets_dets: subnet.cidr_block])
  last_cidr_block = split("/",local.cidrs["${(length(local.cidrs)-1)}"])

  parent_last_cidr_prefix = "${tonumber(local.last_cidr_block[1])-1}"
  parent_last_cidr_block = "${local.last_cidr_block[0]}/${tostring(local.parent_last_cidr_prefix)}"

  next_cidr_block = cidrsubnet(local.parent_last_cidr_block, 1, 1)
  cidr_block = cidrsubnet(local.next_cidr_block,28-tonumber(local.parent_last_cidr_prefix),0)
  internet_gateway_id = length(data.oci_core_internet_gateways.gateways)>0?data.oci_core_internet_gateways.gateways.gateways[0].id:oci_core_internet_gateway.gateway[0].id
  subnet = var.use_existing_subnet? data.oci_core_subnet.existing_apigw_subnet[0] : oci_core_subnet.subnet[0]
#  nlb_egress_port = data.oci_network_load_balancer_backend_sets.backend_sets.backend_set_collection[0].items[0].backends[0].port
}

data "oci_core_subnet" "existing_apigw_subnet" {
  count = var.use_existing_subnet?1:0
  subnet_id = var.existing_subnet_id
}

data "oci_network_load_balancer_backend_sets" "backend_sets" {
  #Required
  network_load_balancer_id = var.kubernetes_nlb_id
}

data "oci_core_instance" "node_instance" {
  instance_id = data.oci_network_load_balancer_backend_sets.backend_sets.backend_set_collection[0].items[0].backends[0].target_id
}

data "oci_core_subnet" "node_subnet" {
  subnet_id = data.oci_core_instance.node_instance.subnet_id
}

data oci_network_load_balancer_network_load_balancer nlb {
  network_load_balancer_id = var.kubernetes_nlb_id
}

data oci_core_subnet nlb_subnet {
  subnet_id = data.oci_network_load_balancer_network_load_balancer.nlb.subnet_id
}
data "oci_core_vcn" "nlb_vcn" {
  vcn_id = data.oci_core_subnet.nlb_subnet.vcn_id
}

data "oci_core_subnets" subnets {
  vcn_id = data.oci_core_vcn.nlb_vcn.id
  compartment_id = data.oci_core_vcn.nlb_vcn.compartment_id
}

data "oci_core_subnet" "subnets_dets" {
  for_each = toset(local.subnet_ids)
  subnet_id = "${each.key}"
}

resource "oci_core_subnet" "subnet" {
  count = var.use_existing_subnet?0:1
  display_name =  var.subnet_name
  cidr_block     = local.cidr_block
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  route_table_id = oci_core_route_table.route_table.id
  security_list_ids = [oci_core_security_list.security_list_api_gw.id]
  lifecycle {
    ignore_changes = [cidr_block]
  }
}

data "oci_core_internet_gateways" "gateways"{
  compartment_id = var.compartment_id
  vcn_id = data.oci_core_vcn.nlb_vcn.id
}

resource "oci_core_internet_gateway" "gateway" {
  count = length(data.oci_core_internet_gateways.gateways)>0?0:1
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  enabled = true
}

resource "oci_core_route_table" "route_table" {
  display_name = format("%s-route-table", var.subnet_name)
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  route_rules {
    network_entity_id = local.internet_gateway_id
    destination = "0.0.0.0/0"
  }
}

resource "oci_core_security_list" "security_list_api_gw" {
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  display_name = format("%s-sec-rules",var.subnet_name)
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

resource "oci_core_security_list" "nlb_security_rules" {
  count = var.create_security_rules?1:0
  freeform_tags = {
    "subnet_id": data.oci_core_subnet.nlb_subnet.id
  }
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  display_name = format("%s-sec-rules",data.oci_core_subnet.nlb_subnet.display_name)
  egress_security_rules {
    destination = data.oci_core_subnet.node_subnet.cidr_block
    destination_type = "CIDR_BLOCK"
    protocol = "6"
    tcp_options {
      max=32767
      min=30000
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = local.subnet.cidr_block
    tcp_options {
        max=80
        min=80
    }
  }
  egress_security_rules {
    destination = data.oci_core_subnet.node_subnet.cidr_block
    destination_type = "CIDR_BLOCK"
    protocol = "6"
    tcp_options {
      max=10256
      min=10256
    }
  }
}

resource "oci_core_security_list" "node_security_rules" {
  count = var.create_security_rules?1:0
  freeform_tags = {
    "subnet_id": local.subnet.id
  }
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_vcn.nlb_vcn.id
  display_name = format("%s-sec-rules",data.oci_core_subnet.node_subnet.display_name)
  ingress_security_rules {
    protocol = "6"
    source   = data.oci_core_subnet.nlb_subnet.cidr_block
    tcp_options {
      max=32767
      min=30000
    }
  }
  egress_security_rules {
    destination = data.oci_core_subnet.nlb_subnet.cidr_block
    protocol    = "6"
    tcp_options {
      source_port_range {
        max = 32767
        min = 30000
      }
    }
  }
  ingress_security_rules {
    protocol    = "6"
    source      = data.oci_core_subnet.nlb_subnet.cidr_block
    tcp_options {
      max = 10256
      min = 10256
    }
  }
}

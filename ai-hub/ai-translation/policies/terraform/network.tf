# VCN
resource "oci_core_vcn" "aih_vcn" {
  count          = var.create_new_vcn ? 1 : 0
  cidr_block     = var.vcn_cidr
  compartment_id = var.compartment_id
  display_name   = var.vcn_display_name
}

# Gateways/ Route Table Enties for Public Subnet which will contain Load Balancer
resource "oci_core_internet_gateway" "igw" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "public-subnet-igw"
  enabled        = true
}

resource "oci_core_route_table" "public_subnet_route_table" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "Public Subnet Route Table"
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw[0].id
    destination_type  = "CIDR_BLOCK"
  }
}

# NAT Gateway and Service gateway for private subnet which will conatain the instance serving Ui Application

resource "oci_core_nat_gateway" "nat_gatway" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "private-subnet-nat-gtw"
}

resource "oci_core_service_gateway" "service_gateway" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "private-subnet-service-gtw"
  services {
    service_id = lookup(data.oci_core_services.all_oci_services.services[0], "id")
  }
}

resource "oci_core_route_table" "private_subnet_route_table" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "Private Subnet Route Table"
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.nat_gatway[0].id
    destination_type  = "CIDR_BLOCK"
  }
  route_rules {
    destination       = lookup(data.oci_core_services.all_oci_services.services[0], "cidr_block")
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.service_gateway[0].id
    description       = "Terraformed - Auto-generated at Service Gateway creation: All Services in region to Service Gateway"
  }
}

#Security List for Public Subnet

resource "oci_core_security_list" "public_subnet_security_list" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "PublicSubnetSL"

  # Inbound Rules
  ingress_security_rules {
    protocol    = "6" # TCP
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 80
      max = 80
    }
    description = "Allow HTTP traffic"
  }

  ingress_security_rules {
    // allow all SSH
    protocol = "6"
    source   = "0.0.0.0/0"

    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol    = "6" # TCP
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 443
      max = 443
    }
    description = "Allow HTTPS traffic"
  }

  # ingress_security_rules {
  #   protocol = 6
  #   source   = "0.0.0.0/0"

  #   source_type = "CIDR_BLOCK"
  #   tcp_options {
  #     max = 8080
  #     min = 8080
  #   }
  # }

  # Outbound Rules
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    description = "Allow all outbound traffic"
  }
}

resource "oci_core_security_list" "private_subnet_security_list" {
  count          = var.create_new_vcn ? 1 : 0
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.aih_vcn[0].id
  display_name   = "PrivateSubnetSL"
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  # HTTP Traffic
  ingress_security_rules {
    protocol = 6
    source   = "0.0.0.0/0"

    source_type = "CIDR_BLOCK"
    tcp_options {
      max = 80
      min = 80
    }
  }
  # SSH Access
  ingress_security_rules {
    protocol = 6
    source   = "0.0.0.0/0"

    source_type = "CIDR_BLOCK"
    tcp_options {
      max = 22
      min = 22
    }
  }
  # Allowing Traffic on port 8080
  ingress_security_rules {
    protocol = 6
    source   = "0.0.0.0/0"

    source_type = "CIDR_BLOCK"
    tcp_options {
      max = 8080
      min = 8080
    }
  }
  # Allowing Traffic on port 8000
  ingress_security_rules {
    protocol = 6
    source   = "0.0.0.0/0"

    source_type = "CIDR_BLOCK"
    tcp_options {
      max = 8000
      min = 8000
    }
  }
}

# Create Subnets

resource "oci_core_subnet" "app_oci_core_subnet" {
  count                      = var.create_new_vcn ? 1 : 0
  display_name               = "app-subnet-${formatdate("MMDDhhmm", timestamp())}"
  cidr_block                 = var.app_subnet_cidr
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.aih_vcn[0].id
  prohibit_internet_ingress  = true
  prohibit_public_ip_on_vnic = true
  security_list_ids          = [oci_core_security_list.private_subnet_security_list[0].id]
  route_table_id             = oci_core_route_table.private_subnet_route_table[0].id
}

resource "oci_core_subnet" "api_gw_oci_core_subnet" {
  count                      = var.create_new_vcn ? 1 : 0
  cidr_block                 = var.api_gw_subnet_cidr
  compartment_id             = var.compartment_id
  display_name               = "api-gw-subnet-${formatdate("MMDDhhmm", timestamp())}"
  vcn_id                     = oci_core_vcn.aih_vcn[0].id
  prohibit_internet_ingress  = false
  prohibit_public_ip_on_vnic = false
  security_list_ids          = [oci_core_security_list.public_subnet_security_list[0].id]
  route_table_id             = oci_core_route_table.public_subnet_route_table[0].id
}



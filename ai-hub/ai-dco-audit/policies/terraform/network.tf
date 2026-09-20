# Create Virtual Cloud Network (VCN)
resource "oci_core_vcn" "dco_audit_vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = "10.0.0.0/16"
  display_name   = "dco-audit-vcn"
  dns_label      = "dcoaudit"
}

# Create Subnet for Container Instance
resource "oci_core_subnet" "dco_audit_subnet" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.dco_audit_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "dco-audit-subnet"
  dns_label         = "dcoauditsubnet"
  security_list_ids = [oci_core_security_list.dco_audit_security_list.id]
  route_table_id    = oci_core_route_table.dco_audit_route_table.id
}

# Create Internet Gateway for Public Access
resource "oci_core_internet_gateway" "dco_audit_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.dco_audit_vcn.id
  display_name   = "dco-audit-igw"
  enabled        = true
}

# Create Route Table for Internet Access
resource "oci_core_route_table" "dco_audit_route_table" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.dco_audit_vcn.id
  display_name   = "dco-audit-route-table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.dco_audit_igw.id
  }
}

# Create Security List for Allowing Traffic
resource "oci_core_security_list" "dco_audit_security_list" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.dco_audit_vcn.id
  display_name   = "dco-audit-security-list"

  # Allow inbound HTTP/HTTPS traffic for Streamlit app
  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = false

    tcp_options {
      destination_port_range {
        min = 8501
        max = 8501
      }
    }
  }

  ingress_security_rules {
    protocol    = "6"  # TCP
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = false

    tcp_options {
      destination_port_range {
        min = 443
        max = 443
      }
    }
  }

  # Allow all outbound traffic
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    stateless   = false
  }
}
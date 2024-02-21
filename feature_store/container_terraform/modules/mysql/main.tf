locals {
  mysql_shape = var.mysql_shape==""?data.oci_mysql_shapes.mysql_shapes.shapes[0].name:var.mysql_shape
}


data "oci_identity_availability_domains" "ADs" {
  compartment_id = var.compartment_ocid
}

data "oci_mysql_shapes" "mysql_shapes" {
  compartment_id      = var.compartment_ocid
}


resource "oci_mysql_mysql_db_system" "mysql_db_system" {
  admin_password      = random_password.mysql_password.result
  admin_username      = "admin"
  availability_domain = lookup(data.oci_identity_availability_domains.ADs.availability_domains[0], "name")
  compartment_id          = var.compartment_ocid
  data_storage_size_in_gb = var.mysql_db_size
  description             = "MySQL DB for feature store"
  display_name            = var.mysql_db_name
  hostname_label          = "mysql-db"
  port       = "3306"
  port_x     = "33060"
  shape_name = var.mysql_shape
  subnet_id  = var.subnet_id
  lifecycle {
    ignore_changes = [admin_password, admin_username, defined_tags["Oracle-Tags.CreatedBy"], defined_tags["Oracle-Tags.CreatedOn"]]
  }
}

resource "random_password" "mysql_password" {
  length           = 16
  special          = true
  min_numeric      = 1
  override_special = ""
  min_lower = 1
  min_upper = 1
  min_special = 1
}

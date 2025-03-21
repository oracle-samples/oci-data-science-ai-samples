resource "oci_datascience_project" "demo" {
  compartment_id = var.compartment_id
  display_name   = "MyFirstDataScienceProject"
}
data "oci_objectstorage_namespace" "this" {
  compartment_id = var.app_impl.compartment_id
}
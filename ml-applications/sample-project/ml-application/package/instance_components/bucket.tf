data "oci_objectstorage_namespace" "this" {
  compartment_id = var.app_impl.compartment_id
}

resource "oci_objectstorage_bucket" "data_storage_bucket" {
  compartment_id = var.app_impl.compartment_id
  namespace      = data.oci_objectstorage_namespace.this.namespace
  name           = "ml-app-fetal-risk-bucket-${var.app_instance.id}"
  access_type    = "NoPublicAccess"

  # To allow Instance (tenant) isolation
  defined_tags   = {"${var.app_impl.package_arguments.mlapps_tag_namespace}.MlApplicationInstanceId" = var.app_instance.id}
}
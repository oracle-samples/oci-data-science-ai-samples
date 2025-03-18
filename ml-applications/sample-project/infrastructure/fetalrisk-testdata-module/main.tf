data "oci_objectstorage_namespace" "this" {
  compartment_id = var.compartment_id
}

resource "oci_objectstorage_bucket" "test_data_bucket" {
  compartment_id = var.compartment_id
  namespace      = data.oci_objectstorage_namespace.this.namespace
  name           = var.test_bucket_name
  access_type    = "NoPublicAccess"
}

resource "oci_objectstorage_object" "test_data" {
  bucket    = oci_objectstorage_bucket.test_data_bucket.name
  namespace = data.oci_objectstorage_namespace.this.namespace
  object    = "test_data.csv"
  content   = file("${path.module}/test_data.csv")
  content_type = "text/csv"
}

output "external_data_source_bucket_name" {
  value = oci_objectstorage_object.test_data.bucket
}
output "external_data_source_bucket_namespace" {
  value = oci_objectstorage_object.test_data.namespace
}
output "external_data_source_bucket_file_name" {
  value = oci_objectstorage_object.test_data.object
}
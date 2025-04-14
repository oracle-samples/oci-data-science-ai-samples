variable "compartment_id" {
  description = "Application-Environment specific compartment ID"
  type     = string
  nullable = false
}
variable "test_bucket_name" {
  description = "Name of environment e.g. dev, preprod"
  type = string
  nullable = false
}
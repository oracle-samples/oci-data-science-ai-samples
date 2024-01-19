output "fn_id" {
  value = oci_functions_function.test_function.id
}
output "policies" {
  value = local.policies
}

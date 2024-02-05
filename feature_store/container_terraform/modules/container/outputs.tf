output "ip" {
  value = oci_container_instances_container_instance.fs_container.vnics[0].private_ip
}

output "policies" {
  value = local.policies
}

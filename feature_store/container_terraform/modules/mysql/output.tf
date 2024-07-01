output "password" {
  value = random_password.mysql_password.result
}

output "ip" {
  value = oci_mysql_mysql_db_system.mysql_db_system.ip_address
}

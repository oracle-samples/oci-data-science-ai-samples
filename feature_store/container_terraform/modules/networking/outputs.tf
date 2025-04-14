output "private_subnet" {
  value = local.subnets.private.id
}

output "public_subnet" {
  value =  local.subnets.public.id
}

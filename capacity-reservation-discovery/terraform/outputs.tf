output "capacity_reservation_associations" {
  description = "Console-like, reservation-first rows for explicitly configured Data Science BYOR associations. This is not proof of active Compute consumption or Console CTA registration."
  value       = local.capacity_reservation_usage_report.rows
}

output "capacity_reservation_report" {
  description = "Full report including unresolved associations, warnings, scope, and limitations. The value is stored in Terraform state."
  value       = local.capacity_reservation_usage_report
}

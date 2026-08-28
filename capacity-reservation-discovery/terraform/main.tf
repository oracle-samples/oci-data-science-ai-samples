data "external" "capacity_reservation_usage" {
  program = [var.python_executable, "${path.module}/discover_capacity_reservation_usage_external.py"]

  query = {
    compartment_id        = var.compartment_id
    profile               = var.profile
    config_file           = var.config_file
    region                = var.region
    auth                  = var.auth
    discovery_script_path = var.discovery_script_path
  }
}

locals {
  capacity_reservation_usage_report = jsondecode(data.external.capacity_reservation_usage.result.report_json)
}

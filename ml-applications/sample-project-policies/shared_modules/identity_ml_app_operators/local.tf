locals {
  name_suffix           = "${var.application_name}_${var.environment_naming_suffix}"
  networking_compartment_id = var.networking_compartment_id != "" ? var.networking_compartment_id : var.app_compartment_id
}
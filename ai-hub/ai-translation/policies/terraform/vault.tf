resource "oci_kms_vault" "app_vault" {
  compartment_id = var.compartment_id
  display_name   = var.new_vault_display_name
  vault_type     = "DEFAULT"
  count          = var.use_existing_vault ? 0 : 1
}

resource "oci_kms_key" "app_key" {
  compartment_id = var.compartment_id
  display_name   = "${var.new_vault_display_name}-key"
  key_shape {
    algorithm = "AES"
    length    = 256
  }
  management_endpoint = oci_kms_vault.app_vault[0].management_endpoint
  count               = var.use_existing_vault ? 0 : 1
}

resource "oci_vault_secret" "idcs_app_client_secret" {
  depends_on = [
    oci_kms_vault.app_vault,
    oci_kms_key.app_key
  ]
  #Required
  compartment_id = var.compartment_id
  secret_content {
    #Required
    content_type = "BASE64"

    #Optional
    content = base64encode(oci_identity_domains_app.ai_application_confidential_app.client_secret)
    name    = "idcs_client_secret_${formatdate("MMDDhhmm", timestamp())}"
  }
  secret_name = "idcs_client_secret_${formatdate("MMDDhhmm", timestamp())}"
  vault_id    = var.use_existing_vault ? var.vault_id : oci_kms_vault.app_vault[0].id
  key_id      = var.use_existing_vault ? var.key_id : oci_kms_key.app_key[0].id
}
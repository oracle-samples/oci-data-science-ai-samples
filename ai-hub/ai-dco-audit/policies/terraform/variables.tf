variable "tenancy_ocid" {
  description = "OCID of your tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of the user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint for the API key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the private key file for OCI API authentication"
  type        = string
}

variable "region" {
  description = "OCI region (e.g., us-ashburn-1)"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_ocid" {
  description = "OCID of the compartment to deploy resources in"
  type        = string
}

variable "image_ocid" {
  description = "OCID of the image in OCI Container Registry (e.g., <region>.ocir.io/<tenancy>/<repo>/dco-access-audit:latest)"
  type        = string
}
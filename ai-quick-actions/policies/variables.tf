#*************************************
#          IAM Specific
#*************************************
variable "aqua_policy_name" {
  default = "DataScienceAquaPolicies"
}

variable "aqua_dg_name" {
  default = "DataScienceAquaDynamicGroup"
}

variable "distributed_training_dg_name" {
  default = "DistributedTrainingJobRunsDynamicGroup"
}

variable "distributed_training_policy_name" {
  default = "DistributedTrainingJobRunsPolicies"
}

#*************************************
#           TF Requirements
#*************************************
variable "tenancy_ocid" {
}
variable "region" {
}
variable "compartment_ocid" {
}
variable "user_model_buckets" {
  type = list
  description = "List buckets for storing fine tuning models and evaluation. Important: To save fine-tuned models, versioning has to be enabled in the selected Object Storage bucket."
}
variable "user_data_buckets" {
  type = list
  description = "List buckets for storing dataset used for fine tuning and evaluation."
}
#variable "user_ocid" {
#  default = ""
#}
#variable "private_key_path" {
#  default = ""
#}
#variable "fingerprint" {
#  default = ""
#}


#*************************************
#           Data Sources
#*************************************
data "oci_identity_compartment" "current_compartment" {
  #Required
  id = var.compartment_ocid
}

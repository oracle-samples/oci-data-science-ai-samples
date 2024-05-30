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
  default = []
  type = list(string)
  description = "List buckets for storing fine tuning models and evaluation. Important: To save fine-tuned models, versioning has to be enabled in the selected Object Storage bucket."
}
variable "user_data_buckets" {
  default = []
  type = list(string)
  description = "List buckets for storing dataset used for fine tuning and evaluation."
}

variable "deployment_type" {
  type = string
  description = "Type of deployment"
  validation {
    condition     = contains(["All policies", "Only admin policies", "Only resource policies"], var.deployment_type)
    error_message = "The deployment_type must be one of: 'All policies', 'Only admin policies', 'Only resource policies'."
  }
}

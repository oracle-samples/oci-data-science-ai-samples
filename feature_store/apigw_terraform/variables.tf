variable nlb_id {
  description = "Network load balancer ocid for the resource created after deploying feature store helm chart "
  type = string
}

variable "use_nlb_compartment" {
  description = "Uses network load balancer compartment for the stack deployment. If false, compartment id must be provided in 'compartment_id'"
  type = bool
  default = true
}

variable "automatically_provision_apigw_subnet" {
  description = "Creates a new Subnet. If false, the subnet ocid to use for api gateway must be provided"
  type = bool
  default = true
}

variable "api_gw_subnet_id" {
  description = "Subnet Id for api gateway. Leave blank to automatically provision a subnet"
  type = string
  default = ""
}

variable authorized_user_groups {
  description = "User group OCIDs authorized to access feature store environment"
  type = list(string)
}

variable function_img_ocir_url {
  description = "OCIR URL of the authorizer image exported from feature store marketplace listing"
  type = string
}

variable "tenancy_ocid" {
  type = string
  description = "OCID of the tenancy where the stack needs to be deployed"
}

variable "compartment_id" {
  type = string
  description = "OCID of the compartment where the stack needs to be deployed. If not provided, the stack will be deployed in the nlb compartment"
  default = ""
}

variable "region" {
  description = "Region in which the resources are to be provisioned"
  type = string
}

variable "create_security_rules" {
  description = "Should we automatically create required security groups for node and load balancer subnet? Note: These need be manually attached to the respective subnets once the stack is provisioned"
  type = bool
  default = true
}

variable "home_region" {
  description = "Home region of the tenancy. If not provided, the home region will be automatically populated using metadata from tenancyid"
  type = string
  default = ""
}

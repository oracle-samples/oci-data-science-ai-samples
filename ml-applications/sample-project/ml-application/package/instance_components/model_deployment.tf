data "archive_file" "default_model" {
  type        = "zip"
  output_path = "model.zip"
  source_dir  = "model/"
}

# TODO move this to application components to avoid creation per each instance
resource "oci_datascience_model" "fetalrisk_default" {
  #Required
  artifact_content_length      = data.archive_file.default_model.output_size
  model_artifact = data.archive_file.default_model.output_path #"model.zip"
  artifact_content_disposition = "attachment; filename=${data.archive_file.default_model.output_path}"
  compartment_id               = var.app_impl.compartment_id
  project_id                   = var.app_impl.package_arguments.data_science_project_id
  display_name                 = "${local.fetal_risk_usecase_name}_default"

  # TODO this should be uncomment once Terraform team solve issue with OracleTags
  # Default model does not need tag as it is used by ML App Implementation RP. It would be needed only if revert to default model in MD would was needed
  # defined_tags = {"${var.app_impl.package_arguments.mlapps_tag_namespace}.MlApplicationInstanceId" = var.app_instance.id}
}

locals {
  fetal_risk_usecase_name = "fetalrisk"
}

# A model deployment resource configurations for creating a new model deployment
resource "oci_datascience_model_deployment" "tf_model_deployment" {
  display_name = local.fetal_risk_usecase_name
  # Required
  compartment_id = var.app_impl.compartment_id

  model_deployment_configuration_details {
    # Required
    deployment_type = "SINGLE_MODEL"
    model_configuration_details {
      # Required
      instance_configuration {
        # Required
        instance_shape_name = "VM.Standard.E4.Flex"
        model_deployment_instance_shape_config_details {
          memory_in_gbs = 16
          ocpus         = 2
        }
      }
      model_id = var.current_model_id != null ? (contains(keys(var.current_model_id), local.fetal_risk_usecase_name) ?
                (var.current_model_id[local.fetal_risk_usecase_name] != null ? var.current_model_id[local.fetal_risk_usecase_name] :
                  oci_datascience_model.fetalrisk_default.id) : oci_datascience_model.fetalrisk_default.id) : oci_datascience_model.fetalrisk_default.id

      # Optional
      bandwidth_mbps = 10
      maximum_bandwidth_mbps = 15
      scaling_policy {
        # Required
        instance_count = 1
        policy_type    = "FIXED_SIZE"
      }
    }
  }
  project_id = var.app_impl.package_arguments.data_science_project_id
  category_log_details {
    #Optional
    access {
      #Required
      log_group_id = var.app_impl.package_arguments.data_science_log_group_id
      log_id       = var.app_impl.package_arguments.model_deployment_access_log_id
    }
    predict {
      #Required
      log_group_id = var.app_impl.package_arguments.data_science_log_group_id
      log_id       = var.app_impl.package_arguments.model_deployment_predict_log_id
    }
  }

  # To allow Instance (tenant) isolation
  defined_tags = {"${var.app_impl.package_arguments.mlapps_tag_namespace}.MlApplicationInstanceId" = var.app_instance.id}
}

output "model_deployment_id" {
  value = oci_datascience_model_deployment.tf_model_deployment.id
}

locals {
  # this can be either compartment of external subnet or 'shared' compartment in multiapp environment or application compartment (or root of application compartments)
  # DO NOT use this in where condition (as it would not work for root of application compartments in multiapp environment)
  subnet_compartment_id = coalesce(var.external_subnet_compartment_id, var.shared_resources_compartment_id, var.app_compartment_id)

  environment_name_resolved = var.environment_name != null && var.environment_name != "" ? var.environment_name : ""
  policy_name_suffix = var.policy_name_suffix != null && var.policy_name_suffix != "" ? "${var.policy_name_suffix}_${local.environment_name_resolved}" : local.environment_name_resolved
}

#######################################################################################
# Recommendation for ML Application is that ML Application should be in its own compartment.
# This policy expects that the recommendation is followed. Most of the policy statements are
# defined in way that they allows given Resource Principal to access resources
# in the compartment where the given Resource is located.
#######################################################################################

resource "oci_identity_policy" "ml_app_runtime" {
  compartment_id = var.tenancy_id # must be tenancy ID because some statements have "in tenancy" scope
  description    = "Policy statements necessary for ML Application runtime"
  name           = "ml_app_runtime_${local.policy_name_suffix}"
  statements     = [
    ####################################################################################################################
    # ML Application Implementation Resource Principals
    # Used by: ML App service for orchestration of DataScience resources defined as application and instance components

    # Data Science
    "Allow any-user to manage data-science-family in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # Object Storage
    "Allow any-user to manage object-family in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # Networking
    "Allow any-user to use subnets in compartment id ${local.subnet_compartment_id} where ${var.external_subnet_compartment_id != "" ? local.appimpl_in_app_compartment : var.shared_resources_compartment_id != "" ? local.appimpl_from_app_to_shared_compartment : local.appimpl_in_same_app_compartment}",
    # Logging
    "Allow any-user to read logging-family in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # Tagging instance components
    "Allow any-user to use tag-namespaces in tenancy where all {target.tag-namespace.name='${var.mlapps_tag_namespace}', request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}'}",
    # Some resources need this for their update
    "Allow any-user to use tag-namespaces in tenancy where all {target.tag-namespace.name='Oracle-Tags', request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}'}",

    ####################################################################################################################
    # ML Application Instance View Resource Principals
    # Used by:
    #   - Triggers for creation (execution) of JobRun or/and PipelineRun
    #   - ML App service for removal of runtime components (JobRuns and PipelineRuns)

    # Data Science
    "Allow any-user to {DATA_SCIENCE_PROJECT_READ,DATA_SCIENCE_JOB_READ,DATA_SCIENCE_PIPELINE_READ} in compartment id ${var.app_compartment_id} where all {request.principal.type='datasciencemlappinstanceview${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    "Allow any-user to manage data-science-job-runs in compartment id ${var.app_compartment_id} where all {request.principal.type='datasciencemlappinstanceview${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    "Allow any-user to manage data-science-pipeline-runs in compartment id ${var.app_compartment_id} where all {request.principal.type='datasciencemlappinstanceview${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # Networking
    "Allow any-user to use subnets in compartment id ${local.subnet_compartment_id} where ${var.external_subnet_compartment_id != "" ? local.appinstanceview_in_app_compartment : var.shared_resources_compartment_id != "" ? local.appinstanceview_from_app_to_shared_compartment : local.appinstanceview_in_same_app_compartment}",
    # Logging
    "Allow any-user to read logging-family in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstanceview${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",

    ####################################################################################################################
    # ML Application Instance Resource Principals
    # Used by:
    #   - ML App service to clean up Models and Objects from Object Storage buckets (in context of delete ML Application Instance operation)
    #   - Custom code running in JobRuns and PipelineRuns (created by Triggers) to any operation with relevant OCI resources belonging to given ML Application Instance

    # To be able to access various data sources and OCI services (e.g. Object Storage, Data Science Service, etc.)
    "Allow any-user to use virtual-network-family in compartment id ${local.subnet_compartment_id} where ${var.external_subnet_compartment_id != "" ? local.appinstance_in_app_compartment : var.shared_resources_compartment_id != "" ? local.appinstance_from_app_to_shared_compartment : local.appinstance_in_same_app_compartment}",
    # To be able to create models with MlApplications.MlApplicationInstanceId tag
    "Allow any-user to use tag-namespaces in tenancy where all {target.tag-namespace.name='${var.mlapps_tag_namespace}', request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}'}",
    # To be able to read/write customer related data (only to bucket dedicated for same ML Application Instance)
    "Allow any-user to {BUCKET_READ, OBJECT_INSPECT, OBJECT_READ, OBJECT_CREATE, OBJECT_DELETE, OBJECT_OVERWRITE} in compartment id ${var.app_compartment_id} where all { request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.id = target.bucket.tag.${var.mlapps_tag_namespace}.${var.mlapp_instance_id_tag}, request.principal.compartment.id = target.compartment.id}",
    # To be able to create model READ permission for project is required
    "Allow any-user to use data-science-projects in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # To update model in model deployment with newly trained model
    "Allow any-user to {DATA_SCIENCE_MODEL_DEPLOYMENT_INSPECT, DATA_SCIENCE_MODEL_DEPLOYMENT_READ, DATA_SCIENCE_MODEL_DEPLOYMENT_UPDATE, DATA_SCIENCE_MODEL_DEPLOYMENT_PREDICT} in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.id = target.resource.tag.${var.mlapps_tag_namespace}.${var.mlapp_instance_id_tag}, request.principal.compartment.id = target.compartment.id}",
    # Needed for JobRun cancel (done from Job Run)
    "Allow any-user to {DATA_SCIENCE_JOB_RUN_READ, DATA_SCIENCE_JOB_RUN_UPDATE} in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # Needed for PipelineRun cancel (done from pipeline step)
    "Allow any-user to {DATA_SCIENCE_PIPELINE_RUN_READ, DATA_SCIENCE_PIPELINE_RUN_UPDATE} in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",
    # To manage model (Used usually from training step)
    "Allow any-user to manage data-science-model in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.id = target.resource.tag.${var.mlapps_tag_namespace}.${var.mlapp_instance_id_tag}, request.principal.compartment.id = target.compartment.id }",
    # To create model. For create operations it is not possible to use tag-based policy (used usually from training step). See https://docs.oracle.com/en-us/iaas/Content/Tagging/Tasks/managingaccesswithtags.htm#lim2
    "Allow any-user to {DATA_SCIENCE_MODEL_CREATE} in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id} ",
    # To read secrets required for accessing various data sources (if you do not use OCI Secrets, please remove this policy)
    "Allow any-user to {SECRET_BUNDLE_READ} in compartment id ${var.app_compartment_id} where all { request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', request.principal.id = target.resource.tag.${var.mlapps_tag_namespace}.${var.mlapp_instance_id_tag}, request.principal.compartment.id = target.compartment.id}",

    # SAMPLE APP SPECIFIC - allowing usage of test data for ingestion. MUST BE REMOVED FOR ANY PRODUCTION USAGE
    "Allow any-user to {BUCKET_READ, OBJECT_INSPECT, OBJECT_READ} in compartment id ${var.app_compartment_id} where all { request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}', target.bucket.name = /test_data_*/ , request.principal.compartment.id = target.compartment.id}",

    ####################################################################################################################
    # ML Application Resource Principals
    # Used by: Prediction router to access Model Deployment prediction endpoint

    # To allow access to the Model Deployment prediction endpoint
    "Allow any-user to {DATA_SCIENCE_MODEL_DEPLOYMENT_PREDICT} in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datasciencemlapp${local.mlapp_type_suffix}', request.principal.compartment.id = target.compartment.id}",

    ####################################################################################################################
    # ODSC resource (JobRuns and/or PipelineRuns, Model Deployment) resource principals
    # Used by: JobRuns, PipelineRuns, and Model Deployment

    # To allow network access to OCI Services like logging service, Container registry, etc.
    "Allow any-user to use virtual-network-family in compartment id ${local.subnet_compartment_id} where ${var.external_subnet_compartment_id != "" ? local.odsc_resources_in_app_compartment : var.shared_resources_compartment_id != "" ? local.odsc_resource_from_app_to_shared_compartment : local.odsc_resources_in_same_app_compartment}",

    # PipelineRun/JobRun RP and Model Deployment RP send logs
    "Allow any-user to use log-content in compartment id ${var.app_compartment_id} where ${local.odsc_resources_in_same_app_compartment}",

    # PipelineRun/JobRun RP and Model Deployment RP reads docker images
    "Allow any-user to read repo in tenancy where ${local.odsc_resources_in_app_compartment}",

    # PipelineRun RP creates JobRun (For customer managed Jobs only. If you use pipeline service managed jobs this policy is not needed.)
    "Allow any-user to read data-science-projects in compartment id ${var.app_compartment_id} where ${local.odsc_resources_in_same_app_compartment}",
    "Allow any-user to read data-science-jobs in compartment id ${var.app_compartment_id} where ${local.odsc_resources_in_same_app_compartment}",
    "Allow any-user to manage data-science-job-runs in compartment id ${var.app_compartment_id} where ${local.odsc_resources_in_same_app_compartment}",

    ####################################################################################################################
    # Data Science Schedule Resource Principal
    # Used by: Data Science Scheduler
    # See also: https://docs.oracle.com/en-us/iaas/data-science/data-science-tutorial/get-started.htm

    # Allow calling Trigger (ML App Instance View trigger)
    "Allow any-user to use data-science-application-instance-view in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datascienceschedule', request.principal.compartment.id = target.compartment.id, request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app'}",
    # Allow logging
    "Allow any-user to use log-content in compartment id ${var.app_compartment_id} where all {request.principal.type = 'datascienceschedule', request.principal.compartment.id = target.compartment.id, request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app'}",

    ####################################################################################################################
    # Data Science service
    # Used by: Data Science service to be able to use custom networking in your tenancy.
    # See also: https://docs.oracle.com/en-us/iaas/data-science/data-science-tutorial/get-started.htm

    "Allow service datascience to use virtual-network-family in compartment id ${local.subnet_compartment_id}",
  ]
}

locals {
  ###########################################################
  # Where conditions for ML App Implementation RP
  ###########################################################

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app',
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app' and target must be in compartment tagged by MLApplications.compartment_type = 'shared'
  appimpl_from_app_to_shared_compartment = <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  target.resource.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'shared',
  request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app'
  appimpl_in_app_compartment =  <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs form compartment same as compartment of target resource,
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app'
  appimpl_in_same_app_compartment = <<-EOF
all {
  request.principal.compartment.id = target.compartment.id,
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappimpl${local.mlapp_type_suffix}'
}
EOF

  ###########################################################
  # Where conditions for ML App Instance RP
  ###########################################################

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app',
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app' and target must be in compartment tagged by MLApplications.compartment_type = 'shared'
  appinstance_from_app_to_shared_compartment = <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  target.resource.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'shared',
  request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app'
  appinstance_in_app_compartment =  <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs form compartment same as compartment of target resource,
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app'
  appinstance_in_same_app_compartment = <<-EOF
all {
  request.principal.compartment.id = target.compartment.id,
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappinstance${local.mlapp_type_suffix}'
}
EOF

    ###########################################################
  # Where conditions for ML App Instance View RP
  ###########################################################

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app',
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app' and target must be in compartment tagged by MLApplications.compartment_type = 'shared'
  appinstanceview_from_app_to_shared_compartment = <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  target.resource.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'shared',
  request.principal.type = 'datasciencemlappinstanceview${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs from compartment tagged by MLApplications.compartment_type = 'app'
  appinstanceview_in_app_compartment =  <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappinstanceview${local.mlapp_type_suffix}'
}
EOF

  # ML App Instance RPs form compartment same as compartment of target resource,
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app'
  appinstanceview_in_same_app_compartment = <<-EOF
all {
  request.principal.compartment.id = target.compartment.id,
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  request.principal.type = 'datasciencemlappinstanceview${local.mlapp_type_suffix}'
}
EOF

  ###########################################################
  # Where conditions for ODSC resources
  ###########################################################

  # JobRuns, PipelineRuns, ModelDeployments RPs from compartment tagged by MLApplications.compartment_type = 'app',
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app' and target must be in compartment tagged by MLApplications.compartment_type = 'shared'
  odsc_resource_from_app_to_shared_compartment = <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  target.resource.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'shared',
  any { request.principal.type = 'datasciencejobrun', request.principal.type = 'datasciencepipelinerun', request.principal.type = 'datasciencemodeldeployment' }
}
EOF

  # JobRuns, PipelineRuns, ModelDeployments RPs from compartment tagged by MLApplications.compartment_type = 'app'
  odsc_resources_in_app_compartment =  <<-EOF
all {
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  any { request.principal.type = 'datasciencejobrun', request.principal.type = 'datasciencepipelinerun', request.principal.type = 'datasciencemodeldeployment' }
}
EOF

  # JobRuns, PipelineRuns, ModelDeployments RPs form compartment same as compartment of target resource,
  # in addition RPs must be from compartment tagged by MLApplications.compartment_type = 'app'
  odsc_resources_in_same_app_compartment = <<-EOF
all {
  request.principal.compartment.id = target.compartment.id,
  request.principal.compartment.tag.${var.mlapp_env_tag_namespace}.${var.compartment_type_tag} = 'app',
  any { request.principal.type = 'datasciencejobrun', request.principal.type = 'datasciencepipelinerun', request.principal.type = 'datasciencemodeldeployment' }
}
EOF
}
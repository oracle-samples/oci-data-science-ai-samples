#
# OCI Data Science Model Deployment scaling.
#
# This code can be executed as an OCI Function to automatically scale up and down Data Science Model Deployments.
#
# Prerequisistes:
#  * Policies: 
#       Allow dynamic-group <dynamic_group_name> to manage ons-topics in compartment <compartment_name>
#       Allow dynamic-group <dynamic_group_name> to manage alarms in compartment <compartment_name>
#       Allow dynamic-group <dynamic_group_name> to read metrics in compartment <compartment_name> 
#       Allow dynamic-group <dynamic_group_name> to use log-content in compartment <compartment_name>
#  * Include Functions in the dynamic-group:
#       ALL {resource.type = 'fnfunc', resource.compartment.id = '<compartment_OCID>'}
#  * Create scale up alarms:
#       Cpu scale up alarm: must have title "model_deployment_high_cpu"
#       Memory scale up alarm: must have title "model_deployment_high_mem"

import io
import json
import oci
from fdk import response

MAX_INSTANCES = 10  # No more then 10 instances for deployment. Change this number to your liking.
LOW_CPU_THRESHOLD = 10
LOW_MEM_THRESHOLD = 10

VM_SHAPES = [
    ["VM.Standard2.1", "VM.Standard2.2", "VM.Standard2.4", "VM.Standard2.8", "VM.Standard2.16", "VM.Standard2.24"], # Standard VMs
]
VM_STANDARD = 0
VM_STANDARD_LEN = len(VM_SHAPES[VM_STANDARD])

# Create Alarm to fire when CPU utilization drops below the threshold, to scale the deployment down
def create_cpu_scale_down_alarm(alarm_id, model_deployment):
    print("Creating cpu scale down alarm", flush=True)
    
    # create a Monitoring client to communicate with the Monitoring service with Resource Principal authentication
    signer = oci.auth.signers.get_resource_principals_signer()
    monitoring_client = oci.monitoring.MonitoringClient(config={}, signer=signer)

    # get current alarm ID
    current_alarm = monitoring_client.get_alarm(alarm_id=alarm_id).data
    # check for existing alarm. No need for duplicates.
    alarm_summary_response = monitoring_client.list_alarms(compartment_id=current_alarm.compartment_id, display_name="model_deployment_low_cpu")
    if alarm_summary_response.data and (alarm_summary_response.query.find(model_deployment.id) != -1):
        print("Alarm already exists. Aborting alarm creation")
        return None

    alarm_query = 'CpuUtilization[5m]{resourceId = \"' + model_deployment.id + '\"}.mean() < ' + str(LOW_CPU_THRESHOLD)
    # create the alarm
    create_alarm_response = monitoring_client.create_alarm(
        create_alarm_details=oci.monitoring.models.CreateAlarmDetails(
            display_name="model_deployment_low_cpu",
            compartment_id=current_alarm.compartment_id,
            metric_compartment_id=current_alarm.metric_compartment_id,
            namespace=current_alarm.namespace,
            query=alarm_query,
            severity=current_alarm.severity,
            destinations=current_alarm.destinations,
            is_enabled=True,
            repeat_notification_duration="PT5M",
            body="Low cpu for model deployment. Instances can be scaled down to reduce costs",
            message_format="ONS_OPTIMIZED"
        )
    )

    print(json.dumps(create_alarm_response.data), flush=True)
    print("Cpu scale down alarm created", flush=True)


# Add an instance to the deployment to reduce CPU load on each instance
def scale_instance_up(alarm_id, model_deployment):
    print("Scaling instance up", flush=True)
    current_instance_count = model_deployment.model_deployment_configuration_details.model_configuration_details.scaling_policy.instance_count
    model_id = model_deployment.model_deployment_configuration_details.model_configuration_details.model_id
    print(f"current number of instance in the deployment: {current_instance_count}", flush=True)

    # increase the instance number
    new_instance_count = current_instance_count + 1
    if new_instance_count > MAX_INSTANCES:  # don't exceed the maximum number of allowed instances
        print("Max instances reached (", MAX_INSTANCES, "). Aborting scale up", flush=True)
        return None

    # create the model_deployment_configuration_details object
    update_model_deployment_details=oci.data_science.models.UpdateModelDeploymentDetails(
        model_deployment_configuration_details=oci.data_science.models.UpdateSingleModelDeploymentConfigurationDetails(            
            model_configuration_details=oci.data_science.models.UpdateModelConfigurationDetails(
                model_id=model_id,
                scaling_policy=oci.data_science.models.FixedSizeScalingPolicy(
                    policy_type="FIXED_SIZE",
                    instance_count=new_instance_count)
            )   
        )
    )
    
    print("New instance count: ", new_instance_count, flush=True)

    # create a scale down alarm
    create_cpu_scale_down_alarm(alarm_id=alarm_id, model_deployment=model_deployment)

    return update_model_deployment_details


# Reduce an instance from the deployment to reduce costs
def scale_instance_down(alarm_id, model_deployment):
    print("Scaling instance down", flush=True)
    current_instance_count = model_deployment.model_deployment_configuration_details.model_configuration_details.scaling_policy.instance_count
    model_id = model_deployment.model_deployment_configuration_details.model_configuration_details.model_id
    print(f"current number of instance in the deployment: {current_instance_count}", flush=True)

    if current_instance_count == 1:  # Can't reduce to less than 1 instance
        print("Deployment has 1 instance. Can't scale down. delete alarm.", flush=True)

        # create a Monitoring client to communicate with the Monitoring service with Resource Principal authentication
        signer = oci.auth.signers.get_resource_principals_signer()
        monitoring_client = oci.monitoring.MonitoringClient(config={}, signer=signer)
        # Delete the alarm
        delete_alarm_response = monitoring_client.delete_alarm(alarm_id=alarm_id)
        return None

    # decrease the instance number
    new_instance_count = current_instance_count - 1
    # create the model_deployment_configuration_details object
    update_model_deployment_details=oci.data_science.models.UpdateModelDeploymentDetails(
        model_deployment_configuration_details=oci.data_science.models.UpdateSingleModelDeploymentConfigurationDetails(            
            model_configuration_details=oci.data_science.models.UpdateModelConfigurationDetails(
                model_id=model_id,
                scaling_policy=oci.data_science.models.FixedSizeScalingPolicy(
                    policy_type="FIXED_SIZE",
                    instance_count=new_instance_count)
            )   
        )
    )
    
    print("New instance count: ", new_instance_count, flush=True)

    return update_model_deployment_details


# Create Alarm to fire when Memory utilization drops below the threshold, to scale the deployment down
def create_mem_scale_down_alarm(alarm_id, model_deployment):
    print("Creating mem scale down alarm", flush=True)

    # create a Monitoring client to communicate with the Monitoring service with Resource Principal authentication
    signer = oci.auth.signers.get_resource_principals_signer()
    monitoring_client = oci.monitoring.MonitoringClient(config={}, signer=signer)

    # get current alarm ID
    current_alarm = monitoring_client.get_alarm(alarm_id=alarm_id).data
    # check for existing alarm. No need for duplicates.
    alarm_summary_response = monitoring_client.list_alarms(compartment_id=current_alarm.compartment_id, display_name="model_deployment_low_mem")
    if alarm_summary_response.data and (alarm_summary_response.query.find(model_deployment.id) != -1):
        print("Alarm already exists. Aborting alarm creation", flush=True)
        return None

    alarm_query = 'MemoryUtilization[5m]{resourceId = \"' + model_deployment.id + '\"}.mean() < ' + str(LOW_MEM_THRESHOLD)
    # create the alarm
    create_alarm_response = monitoring_client.create_alarm(
        create_alarm_details=oci.monitoring.models.CreateAlarmDetails(
            display_name="model_deployment_low_mem",
            compartment_id=current_alarm.compartment_id,
            metric_compartment_id=current_alarm.metric_compartment_id,
            namespace=current_alarm.namespace,
            query=alarm_query,
            severity=current_alarm.severity,
            destinations=current_alarm.destinations,
            is_enabled=True,
            repeat_notification_duration="PT5M",
            body="Low memory for model deployment. Shapes can be scaled down to reduce costs",
            message_format="ONS_OPTIMIZED"
        )
    )

    print(json.dumps(create_alarm_response.data), flush=True)
    print("Mem scale down alarm created", flush=True)


# Change the VM shape to increase the available memory in use and reduce memory utilization
def scale_vm_up(alarm_id, model_deployment):
    print("Scaling VM shape up", flush=True)
    current_vm_shape = model_deployment.model_deployment_configuration_details.model_configuration_details.instance_configuration.instance_shape_name
    model_id = model_deployment.model_deployment_configuration_details.model_configuration_details.model_id
    print(f"current VM shape in the deployment: {current_vm_shape}", flush=True)

    try:
        # find the index of the VM shape in the supported shapes list
        vm_shape_index = VM_SHAPES[VM_STANDARD].index(current_vm_shape)
        print("vm_shape_index = ", vm_shape_index, " , type = ", type(vm_shape_index), flush=True)
        
        if vm_shape_index == VM_STANDARD_LEN:  # Can't scale up from the largest VM shape available
            print("VM shape is largest possible. Aborting scale up", flush=True)
            return None
        
        new_vm_shape = VM_SHAPES[VM_STANDARD][vm_shape_index+1]
    except:
        print("VM shape ", current_vm_shape, " not found in supported shapes for scaling. aborting scale", flush=True)
        return None

    # create the model_deployment_configuration_details object   
    update_model_deployment_details=oci.data_science.models.UpdateModelDeploymentDetails(
        model_deployment_configuration_details=oci.data_science.models.UpdateSingleModelDeploymentConfigurationDetails(            
            model_configuration_details=oci.data_science.models.UpdateModelConfigurationDetails(
                model_id=model_id,
                instance_configuration=oci.data_science.models.InstanceConfiguration(
                    instance_shape_name=new_vm_shape
                )
            )   
        )
    )

    print("New VM shape: ", new_vm_shape, flush=True)

    # Create an alarm to scale down the deployment when memory utilization drops below threshold
    create_mem_scale_down_alarm(alarm_id=alarm_id, model_deployment=model_deployment)

    return update_model_deployment_details


# Change the VM shape to decrease the available memory in use and reduce costs
def scale_vm_down(alarm_id, model_deployment):
    print("Scaling VM shape down", flush=True)
    current_vm_shape = model_deployment.model_deployment_configuration_details.model_configuration_details.instance_configuration.instance_shape_name
    model_id = model_deployment.model_deployment_configuration_details.model_configuration_details.model_id
    print(f"current VM shape in the deployment: {current_vm_shape}", flush=True)

    try:
        # find the index of the VM shape in the supported shapes list
        vm_shape_index = VM_SHAPES[VM_STANDARD].index(current_vm_shape)
        print("vm_shape_index = ", vm_shape_index, " , type = ", type(vm_shape_index), flush=True)

        if vm_shape_index == 0:  # Can't scale down from the smallest VM shape
            print("VM shape is smallest possible. Aborting scale down. Deleting alarm", flush=True)
            # create a Monitoring client to communicate with the Monitoring service with Resource Principal authentication
            signer = oci.auth.signers.get_resource_principals_signer()
            monitoring_client = oci.monitoring.MonitoringClient(config={}, signer=signer)
            # Delete the alarm
            delete_alarm_response = monitoring_client.delete_alarm(alarm_id=alarm_id)
            return None

        new_vm_shape = VM_SHAPES[VM_STANDARD][vm_shape_index-1]
    except:
        print("VM shape ", current_vm_shape, " not found in supported shapes for scaling. aborting scale", flush=True)
        return None

    # create the model_deployment_configuration_details object
    update_model_deployment_details=oci.data_science.models.UpdateModelDeploymentDetails(
        model_deployment_configuration_details=oci.data_science.models.UpdateSingleModelDeploymentConfigurationDetails(            
            model_configuration_details=oci.data_science.models.UpdateModelConfigurationDetails(
                model_id=model_id,
                instance_configuration=oci.data_science.models.InstanceConfiguration(
                    instance_shape_name=new_vm_shape)
            )   
        )
    )

    print("New VM shape: ", new_vm_shape, flush=True)

    return update_model_deployment_details

# main Function handler
def handler(ctx, data: io.BytesIO=None):
    print("INFO: Function starts", flush=True)
    alarm_msg = {} 
    try:
        # read the alarm message
        alarm_msg = json.loads(data.getvalue())
        print("INFO: Alarm message: ")
        print(alarm_msg, flush=True)    # print message for debugging
    except (Exception, ValueError) as ex:
        print(str(ex), flush=True)

    func_response = ""
    if alarm_msg["type"] == "OK_TO_FIRING" or alarm_msg["type"] == "REPEAT":      # handle the alarm if just started firing or if it was an intentional repeated firing
        alarm_metric_dimension = alarm_msg["alarmMetaData"][0]["dimensions"][0]   # assuming the first dimension matches the instance to resize
        alarm_id = alarm_msg["alarmMetaData"][0]["id"]
        model_deployment_id = alarm_metric_dimension["resourceId"]   # retrieve the model deployment OCID to scale
        print("INFO: model deployment to scale: ", model_deployment_id, flush=True)
        
        # create a Data Science client to communicate with the service with Resource Principal authentication
        signer = oci.auth.signers.get_resource_principals_signer()
        data_science_client = oci.data_science.DataScienceClient(config={}, signer=signer)
        # get the model deployment to update
        model_deployment = data_science_client.get_model_deployment(model_deployment_id).data

        # check that model deployment is in ACTIVE state, otherwise the CPU/Mem utilization is due to deployment update and not real load
        print("lifecycle state = ", model_deployment.lifecycle_state, flush=True)
        if (model_deployment.lifecycle_state == model_deployment.LIFECYCLE_STATE_ACTIVE):
            alarm_type = alarm_msg['title']
            print("Alarm type: ", alarm_type, flush=True)
            if (alarm_type == 'model_deployment_high_cpu'):  # high CPU -> increase number of instances (horizontal scale up) to reduce processing load on each instance
                update_model_deployment_details = scale_instance_up(alarm_id=alarm_id, model_deployment=model_deployment)
            elif (alarm_type == 'model_deployment_low_cpu'):  # low CPU -> decrease number of instances (horizontal scale down) to optimize processing load and reduce costs
                update_model_deployment_details = scale_instance_down(alarm_id=alarm_id, model_deployment=model_deployment)
            elif (alarm_type == 'model_deployment_high_mem'): # high memory -> upgrade VM shape to one with more memory (vertical scale up) to reduce memory load per VM
                update_model_deployment_details = scale_vm_up(alarm_id=alarm_id, model_deployment=model_deployment)
            elif (alarm_type == 'model_deployment_low_mem'):  # low memry -> downgrade VM shape to one with less memory (vertical scale down) to optimnize memory load and reduce costs
                update_model_deployment_details = scale_vm_down(alarm_id=alarm_id, model_deployment=model_deployment)
        
            # update the model deployment
            if (update_model_deployment_details is not None):
                resp = data_science_client.update_model_deployment(
                    model_deployment_id=model_deployment_id, 
                    update_model_deployment_details=update_model_deployment_details
                )
            func_response = "Deployment scaling completed"
        else:
            print("Deployment not in ACTIVE state. Scaling aborted", flush=True)
            func_response = "Deployment not in ACTIVE state. Scaling aborted"
    else:
        print('INFO: Nothing to do, alarm is not FIRING', flush=True)
        func_response = "Nothing to do, alarm is not FIRING"

    # send a response to the function inoker
    return response.Response(
        ctx, 
        response_data=func_response,
        headers={"Content-Type": "application/json"}
    )

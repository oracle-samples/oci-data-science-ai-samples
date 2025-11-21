# This is an automatically generated code sample.
# To make this code sample work in your Oracle Cloud tenancy,
# please replace the values for any parameters whose current values do not fit
# your use case (such as resource IDs, strings containing ‘EXAMPLE’ or ‘unique_id’, and
# boolean, number, and enum parameters with values not fitting your use case).

from http import HTTPMethod
import oci
import sys

print(oci.__version__)
# sys.exit()

# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info
# config = oci.config.from_file()

# Custom signer
config = oci.config.from_file(profile_name='default')
token_file = config['security_token_file']
token = None
with open(token_file, 'r') as f:
    token = f.read()
private_key = oci.signer.load_private_key_from_file(config['key_file'])

signer = oci.auth.signers.SecurityTokenSigner(token, private_key)


# Initialize service client with default config file
data_science_client = oci.data_science.DataScienceClient(config, signer=signer)


# Send the request to service, some parameters are not required, see API
# doc for more info
create_model_deployment_response = data_science_client.create_model_deployment(
    create_model_deployment_details=oci.data_science.models.CreateModelDeploymentDetails(
        project_id="ocid1.datascienceproject.oc1.iad.amaaaaaav66vvniaqsyu2nufljutkn4rzth2nz4q3zqslirct7eayl5ojpma",
        compartment_id="ocid1.tenancy.oc1..aaaaaaaahzy3x4boh7ipxyft2rowu2xeglvanlfewudbnueugsieyuojkldq",
        model_deployment_configuration_details=oci.data_science.models.SingleModelDeploymentConfigurationDetails(
            deployment_type="SINGLE_MODEL",
            model_configuration_details=oci.data_science.models.ModelConfigurationDetails(
                model_id="ocid1.datasciencemodel.oc1.iad.amaaaaaav66vvnia36wjp3kb542uicbssflwid55wqf6zzzbxk5ekhhja4eq",
                instance_configuration=oci.data_science.models.InstanceConfiguration(
                    instance_shape_name="VM.Standard.E4.Flex",
                    model_deployment_instance_shape_config_details=oci.data_science.models.ModelDeploymentInstanceShapeConfigDetails(
                        ocpus=1,
                        memory_in_gbs=16,
                        cpu_baseline="BASELINE_1_1"),
                    ),
                scaling_policy=oci.data_science.models.FixedSizeScalingPolicy(
                    policy_type="FIXED_SIZE",
                    instance_count=1
                ),
                bandwidth_mbps=10,
            ),
            environment_configuration_details=oci.data_science.models.OcirModelDeploymentEnvironmentConfigurationDetails(
                environment_configuration_type="OCIR_CONTAINER",
                server_port=8000,
                health_check_port=8000,
                predict_api_specification="openai",
                custom_http_endpoints=[
                    oci.data_science.models.InferenceHttpEndpoint(
                        endpoint_uri_suffix = "/v1/custom/completions",
                        http_methods = [
                            HTTPMethod.GET,
                            HTTPMethod.POST
                        ],
                    )
                ],
                image='iad.ocir.io/ociodscdev/dsmc/inferencing/odsc-vllm-serving:query-path-test-1',
                image_digest='sha256:6522a4728d8030f97a686b46c416797f7106ccef7e2687d6fa9b594e41809200',
                entrypoint=[],
                environment_variables={
                    'EXAMPLE_KEY_eSrrI': 'EXAMPLE_VALUE_K27qWX7kLrt6ZTDIGtdJ'})),
        display_name="MIE-Python-SDK-Text",
        description="Testing preview python sdk for MIE",
        ),
    )

# Get the data from response
print(create_model_deployment_response.data)
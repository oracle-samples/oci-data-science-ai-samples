# This is an automatically generated code sample.
# To make this code sample work in your Oracle Cloud tenancy,
# please replace the values for any parameters whose current values do not fit
# your use case (such as resource IDs, strings containing ‘EXAMPLE’ or ‘unique_id’, and
# boolean, number, and enum parameters with values not fitting your use case).

import oci
from http import HTTPMethod

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
update_model_deployment_response = data_science_client.update_model_deployment(
    model_deployment_id="ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaav66vvniawqof2ppnqeocdyrkqto2ntkem2cbrm2fqebfx7cqmysq",
    update_model_deployment_details=oci.data_science.models.UpdateModelDeploymentDetails(
        display_name="MIE-Python-SDK-Text-Update",
        description="Sample update for python sdk for MIE",
        model_deployment_configuration_details=oci.data_science.models.UpdateSingleModelDeploymentConfigurationDetails(
            deployment_type="SINGLE_MODEL",
            environment_configuration_details=oci.data_science.models.UpdateOcirModelDeploymentEnvironmentConfigurationDetails(
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
                    'EXAMPLE_KEY_eSrrI': 'EXAMPLE_VALUE_K27qWX7kLrt6ZTDIGtdJ'}
            )
        ),
    )
)

# Get the data from response
print(update_model_deployment_response.headers)
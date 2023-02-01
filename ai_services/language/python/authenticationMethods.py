import oci

def authenticateWithConfigFile():
    # It's assuming there is a default OCI config file "~/.oci/config", and a profile in that config with the name "DEFAULT"
    # Default config file and profile
    default_config = oci.config.from_file()

    ai_client = oci.ai_language.AIServiceLanguageClient(default_config)

    return ai_client

# https://github.com/oracle/oci-python-sdk/blob/master/examples/resource_principals_example.py
def authenticateWithResourcePrincipal():
    # Create a Response Pricipals signer
    print("=" * 80)
    print("Intializing new signer")
    rps = oci.auth.signers.get_resource_principals_signer()

    # Print the Resource Principal Security Token
    # This step is not required to use the signer, it just shows that the security
    # token can be retrieved from the signer.
    print("=" * 80)
    print("Resource Principal Security Token")
    print(rps.get_security_token())

    # Note that the config is passed in as an empty dictionary.  A populated config
    # is not needed when using a Resource Principals signer
    ai_client = oci.ai_language.AIServiceLanguageClient({}, signer=rps)

    return ai_client

# https://github.com/oracle/oci-python-sdk/blob/master/examples/instance_principals_examples.py
def authenticateWithInstancePrincipal():
    # By default this will hit the auth service in the region returned by http://169.254.169.254/opc/v2/instance/region on the instance.
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    # In the base case, configuration does not need to be provided as the region and tenancy are obtained from the InstancePrincipalsSecurityTokenSigner
    ai_client = oci.identity.IdentityClient(config={}, signer=signer)

    return ai_client


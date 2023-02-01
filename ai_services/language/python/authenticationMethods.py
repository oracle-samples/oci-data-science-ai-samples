import oci

def authenticateWithConfigFile():
    # It's assuming there is a default OCI config file "~/.oci/config", and a profile in that config with the name "DEFAULT"
    # Default config file and profile
    default_config = oci.config.from_file()

    # Since config is a dict, you can also build it manually and check it with config.validate_config().
    config_with_key_file = {
        "user": 'ocid1.user.oc1..aaaaaaaa65abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmn',
        "key_file": '~/.oci/oci_api_key.pem',
        "fingerprint": '11:22:33:44:55:66:77:88:99:0a:1b:2c:3d:4e:5f:6g',
        "tenancy": 'ocid1.tenancy.oc1..aaaaaaaa5nfwo53cezleyy6t73v6rn6knhu3molvptnl3kcq34l5ztenancy',
        "region": 'us-phoenix-1'
    }

    # If you want to use the private key which is not in the key file, key_content can be the backup of key_file.
    pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
    pem_suffix = '\n-----END RSA PRIVATE KEY-----'
    key = "aaaaabbbbbbbcccccc..."  # The content of your private key
    key_content = '{}{}{}'.format(pem_prefix, key, pem_suffix)

    config_with_key_content = {
        "user": 'ocid1.user.oc1..aaaaaaaa65abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmn',
        "key_content": key_content,
        "fingerprint": '11:22:33:44:55:66:77:88:99:0a:1b:2c:3d:4e:5f:6g',
        "tenancy": 'ocid1.tenancy.oc1..aaaaaaaa5nfwo53cezleyy6t73v6rn6knhu3molvptnl3kcq34l5ztenancy',
        "region": 'us-phoenix-1'
    }

    ai_client = oci.ai_language.AIServiceLanguageClient(default_config)
    # ai_client = oci.ai_language.AIServiceLanguageClient(config_with_key_file)
    # ai_client = oci.ai_language.AIServiceLanguageClient(config_with_key_content)

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


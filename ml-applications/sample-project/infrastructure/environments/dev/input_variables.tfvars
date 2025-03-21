# Environment name (it should be same as name of environment directory)
environment_name = "dev"

# ML Application name
application_name = "fetalrisk"

# Environment and application specific compartment ID
environment_compartment_id = "ocid1.compartment.oc1..aaaaaaaafrobyownitwra7gqjv3hjsnsjraexuv42eujql2fax4hkg3ge7ta"

# OCI profile (it must be presented in oci configuration file)
# For more information refer to: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm
oci_config_profile = "DEFAULT"

# OCI Region where all resources should be located (e.g. "us-ashburn-1")
# For list of regions and their identifiers: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
region = "us-phoenix-1"

# Custom subnet used for Data Science Jobs running in ML Application (optional value)
# If the this value is not provided VCN and Subnet are created
custom_subnet_id = ""
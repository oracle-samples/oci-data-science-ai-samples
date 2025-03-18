# ML Application provider tenancy ID (where ML Application and underlying resources are supposed to be located)
tenancy_id = "ocid1.tenancy.oc1..aaaaaaaafwgqzxcwlkkpl5i334qpv62s375upsw2j4ufgcizfnnhjd4l55ia"
# OCI home region - policies can only be created in the home region
region = "us-ashburn-1"
# OCI Profile (defined in OCI config file), if not provided DEFAULT is used
oci_config_profile = "DEFAULT"

# ML Application name
application_name = "fetalrisk"

# Name of deployment environment for ML App
environment_name = "dev"

# Compartment ID of already existing subnet which should be reused for ML Application (leave empty string if you are going to create new subnet in application compartment later)
subnet_compartment_id = ""

# ID of application team members group (if empty string no policies for application team members is created)
app_team_group_id = ""





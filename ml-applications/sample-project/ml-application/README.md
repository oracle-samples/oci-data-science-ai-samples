ML Application Development
=======================================

Create New Environment
-----------------------------------
Steps to create new environment:
1. Navigate to `<project_root>/ml-application/environments`. Copy the existing environment directory (for example, `dev`) and rename the copy to the new environment name, e.g., `qa`, `integration` (ideally it should be same as in infrastructure/environment directory).  
   * For a personal development environment, we recommend copying your `dev` directory (already configured for your tenancy) and using the naming convention `dev-yourname` (e.g., `dev-john`). You can leave all values in `input_variables.tfvars` as they are, except for the property `environment_name`, which should be updated to the new environment name, e.g., `dev-yourname`.
1. Open a terminal and navigate to your environment directory (assuming your current directory is project root):
   ```bash
   cd infrastructure/environments/<your-env-dir-path>
   ```
1. Run following command:
   ```bash
   terraform output
   ```
1. Take output of the command and: 
   - replace all " =" with ":" to convert the output to yaml format.
   - (relevant to fetalrisk only) use value of x_test_data parameter as value of configuration parameter with key `external_data_source` in `ml-application/environment/<your-env-dir-path>/testdata-instance.json`
     - Note: this is a configuration of (Object Storage) URL for test data. Value should looks like "oci://test_data_fetalrisk_dev@**<objectst_storage_namespace>**/test_data.csv"
   - (relevant to fetalrisk only) remove properties starting with x (like x_test_data) from yaml formated content
   - use such modified content as content of `ml-application/environment/<your-env-dir-path>/arguments.yaml`
1. Edit the `ml-application/environment/<your-env-dir-path>/env-config.yaml` file (each property has an explanation in the file) in your new environment directory.
   - For a personal development environment, you can leave it as is just change property `environment_naming_suffix`.

Initialize ML App CLI
-----------------------
```bash
cd ml-application
source ./mlapp init
```

Before you start using _mlapp_ CLI please check your proxy setting is correct (if it is needed).

### Proxy Troubleshooting (Internal Oracle Customer only)
Before you start using _mlapp_ CLI please configure your proxy. Proxy setting is not needed if you use OCNA VPN.

* If you use **Oracle Corporate VCN** and ML Application from non-production OCI Data Science service, you must edit 
proxy environment variables in a following way:
    ```bash
    export HTTPS_PROXY=http://www-proxy-hqdc.us.oracle.com:80
    export HTTP_PROXY=http://www-proxy-hqdc.us.oracle.com:80
    export http_proxy=http://www-proxy-hqdc.us.oracle.com:80
    export https_proxy=http://www-proxy-hqdc.us.oracle.com:80
    export NO_PROXY=localhost,127.0.0.1,.oraclecorp.com,datascience-int.us-ashburn-1.oci.oc-test.com
    ```

ML App CLI Usage
--------------------
ML App CLI allows full development cycle including ML Application build, deployment and testing.  

Use following command for _mlapp_ CLI help:
```bash
mlapp -h
```
similarly, for details of particular mlapp commands:
```bash
mlapp deploy -h
```

### Example Usage
Build ML Application
```bash
mlapp build
```
Deploy ML Application
```bash
mlapp deploy
```
Deploy ML Application to non-default environment
```bash
mlapp deploy -e dev
```
Undeploy ML Application and remove all instances
```bash
mlapp undeploy --cascade-delete
```
Instantiate ML Application (create ML Application Instance)
```bash
mlapp instantiate
```
Calling provider's trigger
```bash
mlapp trigger
```
Calling prediction endpoint
```bash
mlapp predict
```
Build and deploy ML Application
```bash
mlapp build && mlapp deploy
```
Remove all Instances and undeploy ML Application (including Implementation)
```bash
mlapp undeploy --cascade-delete
```
Test of ML Application without prediction
```bash
mlapp build && mlapp deploy && mlapp instantiate && mlapp trigger -wmd fetalrisk && mlapp predict
```

Development Best Practice and Hints
------------------------------------
### Warning (DO NOT DO)
- If your solution is already in production never rename Terraform resource name. In this case: ```resource "oci_objectstorage_bucket" "data_storage_bucket" { ``` do not change name ```data_storage_bucket```. Terraform recreates the resource and you would lose data.

### Design recommendations

#### Parameterization
ML Applications supports tree types of parameterization:
- For **deployment environment specific parameters** (different for each deployment environment, e.g. subnet) - Use package arguments (defined in descriptor.yaml)
- For **instance specific parameters** (different for each instance, e.g. DB connection string and credentials for ingestion) - use configuration schema (defined in descriptor.yaml)
- For **training execution parameters** (different for each training execution, e.g. training parameters) - Use trigger parameters (defined in instance-components/pippeline.trigger.yaml)

#### Terraform recommendation
- Use simple decorative definition of resources without any advanced Terraform concepts like foreach or count
- Do not use modules if you really do not have reason for that like reusability of code between multiple ML Applications. It just introduces necessary complication with multiple layers of variables.

### Helpful hints
#### OCI Session token hint
Note: This hint is only for those who use session token authentication.
To avoid the need to manually get/refresh session token every hour, you can obtain session token only once using (standard way):
```bash
oci session authenticate --tenancy-name <tenancy_name> --profile-name <profile_name> --region <region>
```
and then refresh session token automatically in separate terminal window/tab using:
```bash
watch -n 1800 oci session refresh --profile oc1
```
This command refreshes the token every 30 minutes and displays the time and result of the last refresh. Note that the token can only be refreshed for a limited time.
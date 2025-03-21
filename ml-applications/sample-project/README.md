ML Application Sample Project
====================================

ML Application Foundations
-----------------------------
### ML Application - TL;DR
ML Application enables OCI customers to implement end-to-end AI solutions built as standardized, portable packages. These packages can be deployed across multiple OCI regions or even different OCI tenancies.

A solution defined as an ML Application can be instantiated multiple times, ensuring proper data and process segregation. This capability allows authors of ML Applications, such as SaaS organizations, to easily introduce new AI features that can be instantiated for each of their customers.

Using ML Applications, OCI customers can build and provide their AI solutions to other OCI customers as a service, without exposing their intellectual property.

### ML Application Basic Terms
* Provider (or ML Application Provider) - author/owner of ML Application which provides implemented AI use-case to other OCI customers (here called consumers) as a service. Provider and consumer can be in many cases same OCI customer (in such case usually one organization develop/own/maintain ML Application and another organization consume it).
* Consumer (or ML Application Consumer) - OCI customer who instantiate ML Application and benefit from implemented AI use-case
* package (or ML Application package) - standard portable package with blueprint for ML Application. It contains 3 main parts:
  * application-components - Terraform definition of resources which are shared for all Instances. E.g. Data Science Job which can be parameterized and executed for each Instance with Instance specific parameters.
  * instance-components - Terraform and non-terraform definition of resources which are created for each Instance (never shared among Instances).
  * descriptor.yaml (called package descriptor) - defines:
    * version of package
    * package arguments - environment specific parameters of package
    * configuration schema - schema for instance specific parameters ()
* ML Application API Resources:
  * ML Application - Key resource representing certain AI/ML use-case
  * ML Application Implementation (sometimes referred as just Implementation) - Resource representing one solution for given AI/ML use-case (in future one ML Application will be able to have multiple ML Application Implementation)
  * ML Application Implementation Version - deployed version of ML Application Implementation
  * ML Application Instance (sometimes referred as just Instance) - instance of given ML Application (Implementation). Usually Instance is mapped to Saas customer.
  * ML Application Instance View (somtimes referred as Instance View) - more detailed view of instance with detailed information regarding underlying resources (building blocks) related to given instance. 

Project Structure
---------------------
- __*infrastructure*__ - project infrastructure definition (e.g. Data Science Project, Logs and Log Groups, )
  - __*environments*__ - environment specific configurations
    - __*dev*__ - development environment specific configuration
    - __*dev-personal*__ - just placeholder for developer personal environment specific configuration
    - __*preprod*__ - just a placeholder for preproduction environment specific configuration
    - __*production*__ - just a placeholder production environment specific configuration
  - __*fetalrisk-testdata-module*__ - terraform module with test data for testing this ML Application
  - __*infra-module*__ - terraform module with infrastructure resource necessary for this ML Application
  - _README.md_ - readme file explaining how to create environment infrastructure
- __*ml-application*__ - ML Application package + build and deployment scripts
  - __*environments*__ - environment specific configurations
    - __*dev*__ - development environment specific configuration
    - __*dev-personal*__ - just placeholder for developer personal environment specific configuration
    - __*preprod*__ - preproduction environment specific configuration
    - __*production*__ - production environment specific configuration
  - __*package*__ - source code for ML Pipeline steps, model, etc. (including unit tests). This project contains also example of the source code.
    - __*application-components*__ - directory with all the Terraform definitions of application components
    - __*instance-components*__  - directory with all the Terraform and non-terraform definition of instance components
    - __*descriptor.yaml*__ - defines various parameters for given package
  - __*scripts*__ - mlapp CLI related scripts
  - *target* - created after first ```mlapp build``` command execution (it contains temporary files and built artifacts)
  - _README.md_ - readme file explaining how to build, deploy, develop, and test ML Application 
- _README.md_ - this readme file


Quick Start
---------------
### Prerequisites
**Required:**
- You must have Oracle Cloud Infrastructure account (tenancy)
- Terraform installed and configured
  - [Terraform: Set Up OCI Terrafom](https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/tf-provider/01-summary.htm)
  - If you have already OCI CLI installed and configured, you can just install terraform and specify profile in _provider.tf_ (_provider.tf_ is already defined in sample dev environment). 
  ```
  provider "oci" {
  region = var.region
  config_file_profile = var.oci_config_profile
  }
  ```
- Python 3 installed
- All necessary required policies and tags must be created in your tenancy. You can use Terraform scripts from [ml-application-sample-project-infrastructure](https://bitbucket.oci.oraclecorp.com/projects/ML_APPLICATION/repos/ml-application-sample-project-infrastructure/browse)
to create necessary policies. 

**Recommended (there are even alternatives):**
- PyCharm for editing ML Application (ideally with Terraform plugin installed)

### Create Infrastructure for ML Application

Follow steps in section **Create New Environment** in [ML Application README.md](./infrastructure/README.md]) for detailed step for infrastructure creation.

### Build/Deploy/Test ML Application

Navigate to section _ML App CLI Usage_ in [ML Application README.md](./ml-application/README.md])

OCI Command Line for ML Applications
--------------------------------------
Apart from using mlapp CLI you can aslo use standard OCI CLI for all operations with ML Application related resources.
For now (LA release), OCI CLI preview is needed to be installed. Use the latest one (recommendation is to prepare Python virtual environment)
pip install --pre --trusted-host artifactory.oci.oraclecorp.com --index-url https://artifactory.oci.oraclecorp.com/api/pypi/global-dev-pypi/simple oci-cli==3.37.13+preview.1.5990

Each command starts with (please change 'region', 'profile' based on your needs):
```bash
oci --profile aiapps0 --region us-ashburn-1 \
```
If you need to use non-production ML Application Service (int) add also parameter ```--endpoint https://datascience-int.us-ashburn-1.oci.oc-test.com```

ML Application Instance:
- Create
  ```bash
  <oci_command_start>
    data-science ml-app-instance create-with-iam-auth \
    --compartment-id <compartmentId> \
    --ml-app-id <mlAppId> \
    --ml-app-implementation-id <mlAppImplId> \
    --configuration <configuration>
  ```
  example of configuration: ```'[{"key":"external_data_source","value":"SampleIngestionBucket"}]'```
- Delete
  ```bash
  <oci_command_start>
    data-science ml-app-instance delete --ml-app-instance-id <ocid> 
  ```
  
Trigger invocation:
```bash
  <oci_command_start>
    data-science ml-app-instance-view trigger --ml-app-instance-view-id ocid1.datasciencemlappinstanceviewint.oc1.iad.amaaaaaa2o4m44iad4m6i6ll2wvx5vlqs5mu27n4f246s3wsrp6n53ar47dq --trigger-name ADTrainingTrigger
```

Prediction request:
```bash
<oci_command_start>
  raw-request --http-method POST --target-uri https://datascience-int.us-ashburn-1.oci.oc-test.com/20190101/mlApplicationInstances/ocid1.datasciencemlappinstanceint.oc1.iad.amaaaaaa2o4m44iapg6fppiga5e4dfjdzcfbcrr2gg2b2qlqkwjilapnwwia --request-body file:///home/...
```

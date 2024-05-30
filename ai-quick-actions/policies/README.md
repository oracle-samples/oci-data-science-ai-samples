# Policies

- [Home](../README.md)
- [CLI](../cli-tips.md)
- [Model Deployment](../model-deployment-tips.md)
- [Model Evaluation](../evaluation-tips.md)
- [Model Fine Tuning](../fine-tuning-tips.md)

> **Note:** To get started using AI quick actions, an admin in the tenancy needs to install the required policies for AI Quick Actions.  You can use [Oracle Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm) (ORM) stack or configure them manually.

- [Policies](#policies)
- [Setting Up Policies Using (ORM) stack](#setting-up-policies-using-orm-stack)
- [Setting Up Policies Manually](#setting-up-policies-manually)
  - [Dynamic Groups](#dynamic-groups)
  - [Policies](#policies-1)

## Setting Up Policies Using (ORM) stack

> **Note:** Even if you already have the policies to use Data Science service, you still need to use the terraform configuration file to set up the policies to use AI Quick Actions. To successfully execute the Terraform script, you must have administrative rights.

Before running the Terraform script, ensure you have the following permissions granted:

```bash
allow group <your_admin_group> to manage orm-stacks in TENANCY
allow group <your_admin_group> to manage orm-jobs in TENANCY
allow group <your_admin_group> to manage dynamic-groups in TENANCY
allow group <your_admin_group> to manage policies in TENANCY
allow group <your_admin_group> to read compartments in TENANCY
```

Click to deploy the stack  [![Deploy to Oracle Cloud][magic_button]][magic_stack]


After clicking the button, you will be redirected to the Oracle Cloud Infrastructure Console.  You will need to sign in if you are not already signed in.  You can select the kind of policies that need to be deployed for AQUA:
1. All policies - This will deploy all the policies needed for AQUA in one go.
2. Only admin policies - This will deploy only the minimal set of policies that are required to be defined at the root compartment by the tenancy administrator for AQUA.
3. Only resource policies - This will deploy the required policies that are required to be defined at the compartment level provided that the tenancy administrator has already defined the admin policies for AQUA.

![Setup 1](../web_assets/policies1.png)

> **Note:** To save fine-tuned models, versioning has to be enabled in the selected Object Storage bucket. See [here](https://docs.oracle.com/iaas/data-science/using/ai-quick-actions-fine-tuning.htm) for more information.

![Setup 3](../web_assets/policies3.png)

After the stack is created and its Stack details page opens, click Plan from the Terraform Actions menu.  Wait for it to complete.  After it is completed, click Apply from the Terraform Actions menu.  These actions will add the needed policies.


# Setting Up Policies Manually
> **Note:** If you already have policies for the Data Science service, you will still need to implement additional policies to enable AI Quick Actions.

### Dynamic Groups
- ``aqua-dynamic-group``

  ```bash
  any {all {resource.type='datasciencenotebooksession', resource.compartment.id='<your_compartment_ocid>'}, all {resource.type='datasciencemodeldeployment',resource.compartment.id='<your_compartment_ocid>'}, all {resource.type='datasciencejobrun', resource.compartment.id='<your_compartment_ocid>'}}
  ```
- ``distributed_training_job_runs``
  ```bash
  any {all {resource.type='datasciencejobrun', resource.compartment.id='<your_compartment_ocid>'}}
  ```

### Policies

- ``aqua_policies``
  ```bash
  Define tenancy datascience as ocid1.tenancy.oc1..aaaaaaaax5hdic7ya6r5rxsgpifff4l6xdxzltnrncdzp3m75ubbvzqqzn3q

  Endorse any-user to read data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}

  Endorse any-user to inspect data-science-models in tenancy datascience where ALL {target.compartment.name='service-managed-models'}

  Endorse any-user to read object in tenancy datascience where ALL {target.compartment.name='service-managed-models', target.bucket.name='service-managed-models'}

  Allow dynamic-group aqua-dynamic-group to manage data-science-model-deployments in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-models in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to use logging-family in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-jobs in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-job-runs in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to use virtual-network-family in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to read resource-availability in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-projects in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-notebook-sessions in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to manage data-science-modelversionsets in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to read buckets in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to read objectstorage-namespaces in compartment <your-compartment-name>

  Allow dynamic-group aqua-dynamic-group to inspect compartments in tenancy

  Allow dynamic-group aqua-dynamic-group to manage object-family in compartment <your-compartment-name> where any {target.bucket.name='<your-bucket-name>'}
  ```

- ``dt_jr_policies``

  ```bash
  Allow dynamic-group distributed_training_job_runs to use logging-family in compartment <your-compartment-name>

  Allow dynamic-group distributed_training_job_runs to manage data-science-models in compartment <your-compartment-name>

  Allow dynamic-group distributed_training_job_runs to read data-science-jobs in compartment <your-compartment-name>

  Allow dynamic-group distributed_training_job_runs to manage objects in compartment <your-compartment-name> where any {target.bucket.name='<your-bucket-name>'}

  Allow dynamic-group distributed_training_job_runs to read buckets in compartment <your-compartment-name> where any {target.bucket.name='<your-bucket-name>'}
  ```

These policies and dynamic groups set up the necessary permissions to enable AI Quick Actions within your OCI environment. Remember to replace placeholders like ``<your_compartment_ocid>`` and ``<your_compartment-name>`` with actual values from your OCI setup.

> **Note:** To save fine-tuned models, versioning has to be enabled in the selected Object Storage bucket. See [here](https://docs.oracle.com/iaas/data-science/using/ai-quick-actions-fine-tuning.htm) for more information.

![Setup 3](../web_assets/policies3.png)
- [magic_button]: https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg
- [magic_stack]: https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-samples/oci-data-science-ai-samples/releases/latest/download/oci-ods-aqua.zip
- [Home](../README.md)
- [CLI](../cli-tips.md)
- [Model Deployment](../model-deployment-tips.md)
- [Model Evaluation](../evaluation-tips.md)
- [Model Fine Tuning](../fine-tuning-tips.md)

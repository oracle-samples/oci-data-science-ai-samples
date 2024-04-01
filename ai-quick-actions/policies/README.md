# ORM Policies

To install required policies for AI Quick Actions you can use [Oracle Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm) (ORM) stack. Download terraform configuration file [oci-ods-aqua-orm.zip](./oci-ods-aqua-orm.zip) with the infrastructure instructions for the dynamic groups and polices. For steps on creating stacks, see [Creating a Stack from a Zip File](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/create-stack-local.htm#top).

![Setup 1](../web_assets/policies1.png)

![Setup 2](../web_assets/policies2.png)

> **Note:** To save fine-tuned models, versioning has to be enabled in the selected Object Storage bucket. See [here](https://docs.oracle.com/iaas/data-science/using/ai-quick-actions-fine-tuning.htm) for more information.

![Setup 3](../web_assets/policies3.png)

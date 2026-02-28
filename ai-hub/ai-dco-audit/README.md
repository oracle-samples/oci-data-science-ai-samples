# README: Terraform Script for Physical Access Auditing Deployment on OCI

## Overview
This Terraform script automates the deployment of a Physical Access Auditing solution on Oracle Cloud Infrastructure (OCI). As the latest AI Hub solution on Oracle's AI Platform, this application leverages advanced AI capabilities to streamline auditing processes for physical access data, ensuring compliance and security. The deployment uses OCI Container Instances and API Gateway to provide a scalable, secure environment for running the application, supporting multiple concurrent users with complete data isolation.

This README provides instructions on how to use the provided Terraform scripts to launch your own instance of the Physical Access Auditing application, enabling you to create a tailored solution for your organization's needs.

## Purpose
The Physical Access Auditing solution is designed to assist organizations in managing and auditing access logs against permissions data. Deploying this application on OCI allows you to harness Oracle's robust cloud infrastructure for scalability, security, and performance. The Terraform scripts included in this repository simplify the setup process, creating the necessary networking, compute, and gateway resources to run the application.

## Oracle AI Platform and AI Hub Context
Oracle's AI Platform provides a comprehensive suite of tools and services to build, deploy, and manage AI-powered applications. The AI Hub, a central component of this platform, offers pre-built solutions, templates, and integrations to accelerate AI adoption across various use cases. The Physical Access Auditing application represents the latest AI Hub solution, integrating AI-driven data processing to enhance auditing accuracy and efficiency. By deploying this solution, you gain access to cutting-edge AI capabilities hosted on OCI, tailored for enterprise-grade security and scalability.

## Prerequisites
Before using these Terraform scripts to deploy the Physical Access Auditing application, ensure you have the following:
- **Terraform Installed**: Download and install Terraform from [https://www.terraform.io/downloads.html](https://www.terraform.io/downloads.html). Ensure it’s configured with OCI credentials (via `~/.oci/config` or environment variables). Refer to OCI’s Terraform provider documentation for setup.
- **OCI Account and Credentials**: Access to OCI Console with a user account or service account that has permissions to create resources (e.g., Container Instances, API Gateway, networking) in a compartment. Obtain necessary OCIDs (tenancy, user, compartment) and API keys or tokens if required by your organization.
- **Docker Image in OCI Container Registry (OCR)**: Build and push the Physical Access Auditing Docker image to OCR as per the project documentation. Note the image URL (e.g., `<region>.ocir.io/<tenancy-namespace>/<repository>/physical-access-audit:latest`).

## Folder Structure
The Terraform scripts are organized as follows:
```
terraform-physical-audit/
├── providers.tf          # OCI provider configuration
├── variables.tf          # Input variables for customization
├── network.tf            # VCN, subnet, and networking resources
├── container_instance.tf # Container Instance for running the app
├── api_gateway.tf        # API Gateway for secure access
├── policies.tf           # IAM policies for permissions
└── terraform.tfvars      # Variable values (customize with your details)
```

## Deployment Instructions
Follow these steps to launch your own instance of the Physical Access Auditing application using Terraform. This will create a scalable environment on OCI to host the app for multiple users.

### Step 1: Clone or Download This Repository
- Download or clone this repository to your local machine or build server where Terraform is installed.
- Navigate to the directory containing the Terraform scripts:
  ```bash
  cd path/to/terraform-physical-audit
  ```

### Step 2: Customize `terraform.tfvars`
- Open `terraform.tfvars` in a text editor and update the variable values with your OCI details:
  ```hcl
  tenancy_ocid     = "ocid1.tenancy.oc1..example"
  user_ocid        = "ocid1.user.oc1..example"
  fingerprint      = "12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef"
  private_key_path = "~/.oci/oci_api_key.pem"
  region           = "us-ashburn-1"
  compartment_ocid = "ocid1.compartment.oc1..example"
  image_ocid       = "us-ashburn-1.ocir.io/<tenancy-namespace>/<repository>/physical-access-audit:latest"
  ```
- Replace placeholders with your actual OCI tenancy OCID, user OCID, fingerprint, private key path, region, compartment OCID, and the image URL in OCR. Ensure the image URL points to the Physical Access Auditing image you’ve pushed to OCI Container Registry.

### Step 3: Initialize Terraform
- Initialize the Terraform working directory to download the OCI provider and set up the environment:
  ```bash
  terraform init
  ```
- This will download necessary plugins and prepare the configuration.

### Step 4: Review the Deployment Plan
- Generate and review the deployment plan to see what resources Terraform will create:
  ```bash
  terraform plan
  ```
- Check the output to ensure resources like VCN, subnet, Container Instance, API Gateway, and policies match your expectations. Adjust `terraform.tfvars` or scripts if needed.

### Step 5: Apply the Configuration to Deploy
- Deploy the resources to OCI by applying the Terraform configuration:
  ```bash
  terraform apply
  ```
- Confirm by typing `yes` when prompted. This will create the necessary infrastructure in your OCI compartment, including:
  - A Virtual Cloud Network (VCN) and subnet for networking.
  - A Container Instance to run the Physical Access Auditing app.
  - An API Gateway for secure, public access to the app.
  - IAM policies granting necessary permissions.
- Deployment may take a few minutes. Monitor the output for any errors.

### Step 6: Access the Application
- After successful deployment, find the API Gateway endpoint in the OCI Console:
  - Go to **Developer Services > API Gateway > Gateways > physical-access-audit-gateway > Deployments > physical-access-audit-deployment**.
  - Note the endpoint URL (e.g., `https://<gateway-id>.<region>.oci.customer-oci.com/audit/app`).
- Access the app via this URL in a browser. Initially, for testing, you may also access the Container Instance directly via its public IP (if assigned) at `http://<instance-ip>:8501`, though API Gateway is the recommended secure entry point.

### Step 7: Scaling for Multiple Users
- The initial deployment starts with one Container Instance. To support up to 100 concurrent users, scale the instance replicas:
  - In OCI Console, go to **Developer Services > Container Instances > physical-access-audit-instance**.
  - Update the replica count manually or configure auto-scaling policies based on CPU or request load.
  - Alternatively, update `oci_container_instances_container_instance.dco_audit_instance` in `container_instance.tf` to increase replicas and re-apply Terraform.
- Compute resources (OCPUs, memory) can also be scaled in `shape_config` within `container_instance.tf` based on load testing.

## Customization
- **Compute Resources**: Adjust `shape_config` in `container_instance.tf` (e.g., increase `ocpus` and `memory_in_gbs`) for higher performance if supporting many users.
- **Networking**: Modify CIDR blocks or security rules in `network.tf` if your VCN setup requires specific configurations.
- **Image URL**: Ensure `image_ocid` in `terraform.tfvars` points to the correct Physical Access Auditing image in OCI Container Registry.

## Security and Isolation
- **Data Isolation**: The application uses session state and UUID-based temporary directories to ensure no data is shared between user sessions, critical for handling sensitive access data.
- **API Gateway**: Provides secure access with potential for authentication (e.g., via OCI IAM or OAuth, configurable post-deployment in OCI Console).
- **Policies**: The IAM policies in `policies.tf` grant necessary permissions; customize `<your-group-name>` to match your OCI group for user access.

## Destroying Resources
When no longer needed, destroy the deployed resources to avoid costs:
```bash
terraform destroy
```
Confirm by typing `yes`. This will remove all created resources (VCN, Container Instance, API Gateway, etc.) from OCI.

## Troubleshooting
- **Terraform Errors**: If `terraform init`, `plan`, or `apply` fails, check error messages for missing credentials, incorrect OCIDs, or permission issues. Ensure your OCI user has permissions to create resources in the compartment.
- **Deployment Issues**: If Container Instance or API Gateway fails to deploy, check OCI Console for resource status and logs. Adjust `shape` or networking in scripts if resource limits are exceeded.
- **Access Issues**: If unable to access the app via API Gateway endpoint, verify the Container Instance is running (check public IP at `http://<instance-ip>:8501`) and ensure security lists allow traffic on port 8501 or 443.
- For assistance, refer to OCI documentation or internal support resources.

## Conclusion
By launching this Terraform configuration, you can create your own instance of the Physical Access Auditing application, the latest AI Hub solution on Oracle's AI Platform. This deployment harnesses OCI’s scalable infrastructure to support multiple users securely, enabling efficient auditing of physical access data. Customize the setup as needed to fit your organization’s requirements, and scale resources to handle increased demand.

For further customization or scaling guidance, consult Oracle’s AI Platform documentation or reach out to internal support channels for tailored assistance.
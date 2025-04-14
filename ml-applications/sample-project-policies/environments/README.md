Deployment Environments
==========================
Each directory represents one deployment environment. Each environment has its main.tf which reference modules based on 
requirements for given environment and input_variables.tfvars containing parameter values.

Feel free to copy/rename example environments to configure your own deployment environments.

Example environments:
- **dev** 
  - Simple deployment environment suitable mainly for quick PoC
  - Creates single compartment, tags for tenant isolation and necessary policies for ML App and ML App developers/operators
- **dev-multiapp**
  - Production ready deployment environment prepared for multiple ML Applications developed by multiple teams (having their IAM groups in same or in remote tenancy like Boat tenancy)
  - Creates:
    - Environment root compartment and compartment each application in it
    - Compartment for resources shared across all applications (like Vault)
    - Policies for ML App runtime as well as policies for each development team. Policies ensures ML App Instance (Saas tenant) isolation, application isolation and they follow least privilege principle.
    - Tags necessary for tenant isolation and shared resources. These tags are used by policies to ensure  

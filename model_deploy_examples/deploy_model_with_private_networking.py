import argparse
import json
import logging
import sys
import os
import time
import oci
import oci.data_science as data_science
from oci.data_science.models import (
    CreateDataSciencePrivateEndpointDetails,
    CreateModelDeploymentDetails, 
    ModelConfigurationDetails,
    InstanceConfiguration, 
    FixedSizeScalingPolicy,
    CategoryLogDetails, 
    LogDetails,
    SingleModelDeploymentConfigurationDetails
)
from oci.signer import Signer

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Model Deployment with Private Endpoint")

class ModelDeploymentError(Exception):
    """Custom exception for model deployment errors."""
    pass

class ModelDeployment:
    def __init__(self, oci_config_file: str = "~/.oci/config", config_json_path: str = "model_deployment_config.json"):
        self.model_deployment_id = None
        self.private_endpoint_id = None
        self.config_file = oci_config_file
        self.config_json_path = config_json_path
        self.active = False
        
        # Load configuration and initialize clients
        self._load_config()
        self._validate_config()
        self._initialize_clients()

    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(self.config_json_path):
                raise ModelDeploymentError(f"Configuration file {self.config_json_path} not found")
            
            with open(self.config_json_path, 'r') as fp:
                data = json.load(fp)
            
            # Model Deployment - Required parameters
            self.project_id = data.get('project_id')
            self.compartment_id = data.get('compartment_id')
            self.deployment_name = data.get('deployment_name')
            self.model_id = data.get('model_id')
            self.instance_shape_name = data.get('instance_shape_name')
            self.subnet_id = data.get('subnet_id')
            
            # Model Deployment - Optional parameters with defaults
            self.instance_count = int(data.get('instance_count', 1))
            self.bandwidth_mbps = int(data.get('bandwidth_mbps', 10))
            
            # Private Endpoint Configuration
            self.pe_compartment_id = data.get('private_endpoint_compartment_id', self.compartment_id)
            self.pe_display_name = data.get('private_endpoint_display_name', f"{self.deployment_name}_private_endpoint")
            self.pe_description = data.get('private_endpoint_description', 'Data Science Private Endpoint')
            self.pe_subnet_id = data.get('private_endpoint_subnet_id', self.subnet_id)
            self.pe_nsg_ids = data.get('private_endpoint_nsg_ids', [])
            
            # Use existing private endpoint if specified
            self.existing_private_endpoint_id = data.get('existing_private_endpoint_id')
            
            # Logging configuration
            self.access_log_id = data.get('access_log_id')
            self.predict_log_id = data.get('predict_log_id')
            self.log_group_id = data.get('log_group_id')
            
            logger.info(f"Configuration loaded for deployment: {self.deployment_name}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise ModelDeploymentError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ModelDeploymentError(f"Failed to load configuration: {e}")

    def _validate_config(self):
        """Validate required configuration parameters."""
        if not (self.project_id and self.compartment_id and self.model_id):
            logger.error("Model deployment failed. Missing required parameters: project_id, compartment_id, or model_id")
            raise ModelDeploymentError("Missing required parameters: project_id, compartment_id, or model_id")
        
        if not self.subnet_id and not self.pe_subnet_id:
            logger.error("Either subnet_id or private_endpoint_subnet_id is required")
            raise ModelDeploymentError("Either subnet_id or private_endpoint_subnet_id is required")
        
        logger.info("Configuration validation completed successfully")

    def _initialize_clients(self):
        """Initialize OCI clients and authentication."""
        try:
            config_path = os.path.expanduser(self.config_file)
            if not os.path.exists(config_path):
                raise ModelDeploymentError(f"OCI config file not found: {config_path}")
            
            # Initialize OCI configuration and clients
            self.oci_config = oci.config.from_file(config_path, "DEFAULT")
            self.data_science_client = data_science.DataScienceClient(config=self.oci_config)
            self.data_science_composite_client = data_science.DataScienceClientCompositeOperations(
                self.data_science_client
            )
            
            # Initialize signer for authentication
            self.auth = Signer(
                tenancy=self.oci_config['tenancy'],
                user=self.oci_config['user'],
                fingerprint=self.oci_config['fingerprint'],
                private_key_file_location=self.oci_config['key_file'],
                pass_phrase=self.oci_config.get('pass_phrase')
            )
            
            logger.info("OCI clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCI clients: {e}")
            raise ModelDeploymentError(f"Failed to initialize OCI clients: {e}")

    def create_private_endpoint(self):
        """Create a Data Science private endpoint."""
        if self.existing_private_endpoint_id:
            logger.info(f"Using existing private endpoint: {self.existing_private_endpoint_id}")
            self.private_endpoint_id = self.existing_private_endpoint_id
            return self.private_endpoint_id
        
        logger.info("Starting to create Data Science private endpoint")
        
        try:
            # Create private endpoint configuration
            create_pe_details = CreateDataSciencePrivateEndpointDetails(
                compartment_id=self.pe_compartment_id,
                display_name=self.pe_display_name,
                description=self.pe_description,
                subnet_id=self.pe_subnet_id,
                nsg_ids=self.pe_nsg_ids if self.pe_nsg_ids else None
            )
            
            # Create private endpoint and wait for completion
            start_time = time.time()
            create_pe_response = self.data_science_composite_client.create_data_science_private_endpoint_and_wait_for_state(
                create_data_science_private_endpoint_details=create_pe_details,
                wait_for_states=["ACTIVE", "FAILED"]
            )
            
            elapsed_time = time.time() - start_time
            
            if create_pe_response.data.lifecycle_state == "ACTIVE":
                self.private_endpoint_id = create_pe_response.data.id
                logger.info(f"Private endpoint created successfully in {elapsed_time:.2f} seconds")
                logger.info(f"Private Endpoint ID: {self.private_endpoint_id}")
                return self.private_endpoint_id
            else:
                logger.error(f"Private endpoint creation failed with state: {create_pe_response.data.lifecycle_state}")
                raise ModelDeploymentError(f"Private endpoint creation failed with state: {create_pe_response.data.lifecycle_state}")
        
        except Exception as e:
            logger.error(f"Failed to create private endpoint: {e}")
            raise ModelDeploymentError(f"Private endpoint creation failed: {e}")

    def create_model_deployment(self):
        """Create a model deployment with private endpoint."""
        if not self.private_endpoint_id:
            raise ModelDeploymentError("Private endpoint ID not available")
        
        logger.info(f"Starting to create model deployment with private endpoint: {self.private_endpoint_id}")
        
        try:
            # Configure instance with private endpoint
            self.instance_configuration = InstanceConfiguration()
            self.instance_configuration.instance_shape_name = self.instance_shape_name
            self.instance_configuration.subnet_id = self.subnet_id
            self.instance_configuration.private_endpoint_id = self.private_endpoint_id
            
            # Configure scaling policy
            self.scaling_policy = FixedSizeScalingPolicy()
            self.scaling_policy.instance_count = self.instance_count
            
            # Create model configuration
            model_config_details = ModelConfigurationDetails(
                model_id=self.model_id,
                bandwidth_mbps=self.bandwidth_mbps,
                instance_configuration=self.instance_configuration,
                scaling_policy=self.scaling_policy
            )
            
            # Create single model deployment configuration
            single_model_deployment_config_details = SingleModelDeploymentConfigurationDetails(
                deployment_type="SINGLE_MODEL",
                model_configuration_details=model_config_details
            )
            
            # Create model deployment details
            create_model_deployment_details = CreateModelDeploymentDetails(
                display_name=self.deployment_name,
                model_deployment_configuration_details=single_model_deployment_config_details,
                compartment_id=self.compartment_id,
                project_id=self.project_id
            )
            
            # Add logging configuration if provided
            if self.log_group_id and (self.predict_log_id or self.access_log_id):
                create_model_deployment_details.category_log_details = self.create_logging(
                    self.log_group_id, self.access_log_id, self.predict_log_id
                )
            
            # Create model deployment and wait for completion
            start_time = time.time()
            create_model_deployment_response = self.data_science_composite_client.create_model_deployment_and_wait_for_state(
                create_model_deployment_details=create_model_deployment_details,
                wait_for_states=["SUCCEEDED", "FAILED"]
            )
            
            elapsed_time = time.time() - start_time
            work_request_resources = create_model_deployment_response.data.resources
            self.model_deployment_id = work_request_resources[0].identifier
            
            if create_model_deployment_response.data.status == "SUCCEEDED":
                logger.info(f"Model deployment created successfully in {elapsed_time:.2f} seconds")
                logger.info(f"Model Deployment ID: {self.model_deployment_id}")
                self.active = True
            else:
                logger.error("Failed to create model deployment")
                raise ModelDeploymentError("Model deployment creation failed")
                
        except Exception as e:
            logger.error(f"Failed to create model deployment: {e}")
            raise ModelDeploymentError(f"Model deployment creation failed: {e}")

    def write_model_deployment_info(self):
        """Write model deployment and private endpoint information to configuration file."""
        try:
            if not self.model_deployment_id:
                raise ModelDeploymentError("No model deployment ID available")
            
            model_deployment = self.data_science_client.get_model_deployment(
                model_deployment_id=self.model_deployment_id
            )
            
            # Get private endpoint details if available
            private_endpoint_details = None
            if self.private_endpoint_id:
                try:
                    pe_response = self.data_science_client.get_data_science_private_endpoint(
                        data_science_private_endpoint_id=self.private_endpoint_id
                    )
                    private_endpoint_details = {
                        "id": pe_response.data.id,
                        "display_name": pe_response.data.display_name,
                        "state": pe_response.data.lifecycle_state,
                        "subnet_id": pe_response.data.subnet_id,
                        "fqdn": getattr(pe_response.data, 'fqdn', None)
                    }
                except Exception as e:
                    logger.warning(f"Could not retrieve private endpoint details: {e}")
            
            # Create backup of original config
            if os.path.exists(self.config_json_path):
                backup_path = f"{self.config_json_path}.backup"
                with open(self.config_json_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Configuration backup created: {backup_path}")
            
            # Update configuration file
            with open(self.config_json_path, 'r+') as f:
                data = json.load(f)
                data['model_deployment_url'] = getattr(model_deployment.data, 'model_deployment_url', None)
                data['model_deployment_id'] = model_deployment.data.id
                data['created_private_endpoint_id'] = self.private_endpoint_id
                
                if private_endpoint_details:
                    data['private_endpoint_details'] = private_endpoint_details
                
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            
            logger.info(f"Deployment info written to {self.config_json_path}")
            logger.info(f"Model Deployment ID: {model_deployment.data.id}")
            logger.info(f"Private Endpoint ID: {self.private_endpoint_id}")
            
            if hasattr(model_deployment.data, 'model_deployment_url'):
                logger.info(f"Model Deployment URL: {model_deployment.data.model_deployment_url}")
            
        except Exception as e:
            logger.error(f"Failed to write deployment info: {e}")
            raise ModelDeploymentError(f"Failed to write deployment info: {e}")

    def create_logging(self, log_group_id: str, access_log_id: str, predict_log_id: str) -> CategoryLogDetails:
        """Create logging configuration for model deployment."""
        try:
            category_log_details = CategoryLogDetails()
            
            if access_log_id:
                access_log_details = LogDetails()
                access_log_details.log_id = access_log_id
                access_log_details.log_group_id = log_group_id
                category_log_details.access = access_log_details
            
            if predict_log_id:
                predict_log_details = LogDetails()
                predict_log_details.log_id = predict_log_id
                predict_log_details.log_group_id = log_group_id
                category_log_details.predict = predict_log_details
            
            return category_log_details
            
        except Exception as e:
            logger.error(f"Failed to create logging configuration: {e}")
            raise ModelDeploymentError(f"Failed to create logging configuration: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deploy A Model with Private Endpoint")
    parser.add_argument("--oci_config_file", nargs="?", 
                       help="Config file containing OCIDs", 
                       default="~/.oci/config")
    parser.add_argument("--config_json", nargs="?",
                       help="JSON configuration file path",
                       default="model_deployment_config.json")
    parser.add_argument("--pe_only", action="store_true",
                       help="Create only private endpoint")
    parser.add_argument("--md_only", action="store_true",
                       help="Create only model deployment (requires existing private endpoint)")
    
    args = parser.parse_args()
    
    try:
        # Initialize model deployment
        md = ModelDeployment(args.oci_config_file, args.config_json)
        # Create both private endpoint and model deployment
        md.create_private_endpoint()
        md.create_model_deployment()
        md.write_model_deployment_info()
        logger.info("Private endpoint and model deployment completed successfully!")
        
    except ModelDeploymentError as e:
        logger.error(f"Deployment error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

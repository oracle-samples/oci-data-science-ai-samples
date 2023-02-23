import time
import oci
print(f'OCI Client SDK version: {oci.__version__}')
config = oci.config.from_file()

compartment_id = "<COMPARTMENT_ID>" #TODO Specify your compartmentId here
bucket_name = "<BUCKET_NAME>" #TODO Specify name of your training data bucket here
namespace_name = "<NAMESPACE_NAME>" #TODO Specify the namespace here
object_names = ["<object_name>"]

project_name = "<PROJECT_NAME>" #TODO specify project name here
model_name = "<MODEL_NAME>" #TODO specify the model name here
endpoint_name = "<ENDPOINT_NAME>" #TODO specify endpoint name

ai_client = oci.ai_language.AIServiceLanguageClient(config)

#create project
project_details = oci.ai_language.models.CreateProjectDetails(compartment_id=compartment_id,display_name=project_name)
print(f"Creating project with details:{project_details}")
project = ai_client.create_project(project_details)
print(f"create_project returned: {project.data}")

#wait till project state becomes ACTIVE
project_id = project.data.id
project_status = project.data.lifecycle_state
while (project.data.lifecycle_state == "CREATING"):
    print('Waiting for project creation to complete...')
    time.sleep(1*60) #sleep for 1 minute
    project = ai_client.get_project(project_id)

project = ai_client.get_project(project_id)
project_status = project.data.lifecycle_state
print(f"Project status changed from CREATING to {project_status}")

#creating model
location_details = oci.ai_language.models.ObjectListDataset(location_type="OBJECT_LIST", namespace_name=namespace_name, bucket_name=bucket_name, object_names=object_names)
# For Text classification, multi-class and multi-labe classification types are supported
classification_mode = oci.ai_language.models.ClassificationType(classification_mode="MULTI_CLASS")
model_details = oci.ai_language.models.CreateModelDetails(
    project_id = project.data.id,
    model_details = oci.ai_language.models.TextClassificationModelDetails(classification_mode=classification_mode,model_type="TEXT_CLASSIFICATION", language_code="en"),
    display_name = model_name,
    compartment_id = compartment_id,
    training_dataset = oci.ai_language.models.ObjectStorageDataset(dataset_type="OBJECT_STORAGE", location_details=location_details)
)

print(f"creating model with details:{model_details}")
model_response = ai_client.create_model(model_details)
print(f"create_model returned: {model_response.data}")

model_details = ai_client.get_model(model_response.data.id)

#wait till model state becomes ACTIVE
while (model_details.data.lifecycle_state == "CREATING"):
    print('Waiting for model creation and training to complete...')
    time.sleep(1*60) #sleep for 1 minute
    model_details = ai_client.get_model(model_response.data.id)

print(f"Model status changed from CREATING to {model_details.data.lifecycle_state}")

print("Printing model evaluation results")
print(model_details.data.evaluation_results)

print("Creating an end point")
endpoint_details = oci.ai_language.models.CreateEndpointDetails(
    compartment_id = compartment_id,
    model_id = model_details.data.id,
    inference_units = 1,
    display_name = endpoint_name
)

endpoint_response = ai_client.create_endpoint(endpoint_details)
print(f"create_endpoint call returned{endpoint_response.data}")
end_point_details = ai_client.get_endpoint(endpoint_response.data.id)

#wait till endpoint state becomes ACTIVE
while (end_point_details.data.lifecycle_state == "CREATING"):
    print('Waiting for endpoint creation to complete...')
    time.sleep(1*60) #sleep for 1 minute
    end_point_details = ai_client.get_endpoint(end_point_details.data.id)

print(f"End point status changed from CREATING to {end_point_details.data.lifecycle_state}")

text_to_analyze = "I am unable to use printer, seeing printer error."

print(f"Analyzing the text: {text_to_analyze}")
txtc_text_for_testing = oci.ai_language.models.BatchDetectLanguageEntitiesDetails(endpoint_id = end_point_details.data.id, documents = [oci.ai_language.models.TextDocument(key = "1", text = text_to_analyze)])
txtc_inference_result = ai_client.batch_detect_language_entities(txtc_text_for_testing)
print("inference result for custom TXTC:")
print(txtc_inference_result.data)

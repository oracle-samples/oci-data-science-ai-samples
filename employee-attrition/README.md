# Employee Attrition 

This example is a modified version of the employee attrition notebook that is available in the OCI Data Science service notebook session.

- includes an optional section to run a data flow application. You can skip that part of the notebook altogether and the notebook 
  should run without errors. 
- includes saving of a random forest model to the catalog (and testing of the artifact)
- includes the Model deployment section (done through the console) 
- includes invoking of the deployed model at the bottom of the notebook.  

## Instructions 

Throughout the notebook we use resource principals to authenticate to the model catalog and model deployment (both to create  
and call/invoke the model deployment). If you want to use resource principals, make sure that your notebook session is part 
of a dynamic group that is authorized to access those resources and perform those actions. Alternatively, you can use the 
config+key flow and take the identity of a user principal when accessing those resources. Make sure you are part of a user group that 
is authorized to access the model catalog and model deployment and perform the create and predict actions. 

### Additional Instructions

* Run the notebook inside the "General Machine Learning for CPU version 1.0" conda environment. 
* Create a folder : /home/datascience/dataflow if you want to execute the data flow section of the notebook 
* Install the (preview) OCI Python SDK which covers the model deployment API. 
* Before you execute the "Invoke the Model HTTP Endpoint" section, make sure you have the right endpoint URI. You can 
  copy that URI from the model deployment details page in the console before your demo. 

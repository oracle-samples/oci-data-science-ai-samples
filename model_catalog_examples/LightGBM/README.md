
# Model: LightGBM Model
 Once you have an active endpoint, you can send requests from any
 HTTP client.
 Utilizing OCI Request Signatures for secure connection,
 you can use web clients such as Postman, Fiddler, or curl, or your
 own client application, for testing purposes.
The OCI-CLI is included in the OCI Cloud Shell environment and is pre-authenticated. This example invokes a model deployment with the CLI:

```bash
oci raw-request \
  --http-method POST \
  --target-uri <model-deployment-url>/predict \
  --request-body \
'{
  "CRIM": {
    "0": 0.00632,
    "1": 0.02731,
    "2": 0.02729,
    "3": 0.03237,
    "6": 0.08829
  },
  "ZN": {
    "0": 18.0,
    "1": 0.0,
    "2": 0.0,
    "3": 0.0,
    "6": 12.5
  },
  "INDUS": {
    "0": 2.31,
    "1": 7.07,
    "2": 7.07,
    "3": 2.18,
    "6": 7.87
  },
  "CHAS": {
    "0": 0.0,
    "1": 0.0,
    "2": 0.0,
    "3": 0.0,
    "6": 0.0
  },
  "NOX": {
    "0": 0.538,
    "1": 0.469,
    "2": 0.469,
    "3": 0.458,
    "6": 0.524
  },
  "RM": {
    "0": 6.575,
    "1": 6.421,
    "2": 7.185,
    "3": 6.998,
    "6": 6.012
  },
  "AGE": {
    "0": 65.2,
    "1": 78.9,
    "2": 61.1,
    "3": 45.8,
    "6": 66.6
  },
  "DIS": {
    "0": 4.09,
    "1": 4.9671,
    "2": 4.9671,
    "3": 6.0622,
    "6": 5.5605
  },
  "RAD": {
    "0": 1.0,
    "1": 2.0,
    "2": 2.0,
    "3": 3.0,
    "6": 5.0
  },
  "TAX": {
    "0": 296.0,
    "1": 242.0,
    "2": 242.0,
    "3": 222.0,
    "6": 311.0
  },
  "PTRATIO": {
    "0": 15.3,
    "1": 17.8,
    "2": 17.8,
    "3": 18.7,
    "6": 15.2
  },
  "B": {
    "0": 396.9,
    "1": 396.9,
    "2": 392.83,
    "3": 394.63,
    "6": 395.6
  },
  "LSTAT": {
    "0": 4.98,
    "1": 9.14,
    "2": 4.03,
    "3": 2.94,
    "6": 12.43
  }
}'

```
Example CLI response:
```
{"prediction": [25.967499846125445, 22.03428725444988, 31.2184389389109, 30.417110598250456, 21.188401444506223]}
```
To call the model endpoint from python using the requests package:
```python
import requests
import oci
import json
from oci.signer import Signer
# model deployment endpoint. Here we assume that the notebook region is the same as the region where the model deployment occurs.
# Alternatively you can also go in the details page of your model deployment in the OCI console. Under "Invoke Your Model", you will find the HTTP endpoint
# of your model.
uri = <your-model-deployment-uri>
# your payload:
input_data = {
  "CRIM": {
    "0": 0.00632,
    "1": 0.02731,
    "2": 0.02729,
    "3": 0.03237,
    "6": 0.08829
  },
  "ZN": {
    "0": 18.0,
    "1": 0.0,
    "2": 0.0,
    "3": 0.0,
    "6": 12.5
  },
  "INDUS": {
    "0": 2.31,
    "1": 7.07,
    "2": 7.07,
    "3": 2.18,
    "6": 7.87
  },
  "CHAS": {
    "0": 0.0,
    "1": 0.0,
    "2": 0.0,
    "3": 0.0,
    "6": 0.0
  },
  "NOX": {
    "0": 0.538,
    "1": 0.469,
    "2": 0.469,
    "3": 0.458,
    "6": 0.524
  },
  "RM": {
    "0": 6.575,
    "1": 6.421,
    "2": 7.185,
    "3": 6.998,
    "6": 6.012
  },
  "AGE": {
    "0": 65.2,
    "1": 78.9,
    "2": 61.1,
    "3": 45.8,
    "6": 66.6
  },
  "DIS": {
    "0": 4.09,
    "1": 4.9671,
    "2": 4.9671,
    "3": 6.0622,
    "6": 5.5605
  },
  "RAD": {
    "0": 1.0,
    "1": 2.0,
    "2": 2.0,
    "3": 3.0,
    "6": 5.0
  },
  "TAX": {
    "0": 296.0,
    "1": 242.0,
    "2": 242.0,
    "3": 222.0,
    "6": 311.0
  },
  "PTRATIO": {
    "0": 15.3,
    "1": 17.8,
    "2": 17.8,
    "3": 18.7,
    "6": 15.2
  },
  "B": {
    "0": 396.9,
    "1": 396.9,
    "2": 392.83,
    "3": 394.63,
    "6": 395.6
  },
  "LSTAT": {
    "0": 4.98,
    "1": 9.14,
    "2": 4.03,
    "3": 2.94,
    "6": 12.43
  }
}

auth = Signer(
tenancy=<your-tenancy-ocid>,
user=<your-user-ocid>,
fingerprint=<your-fingerprint>,
private_key_file_location=<your-pem-key-path>)

# post request to model endpoint:
response = requests.post(uri, json=input_data, auth=auth)
# Check the response status. Success should be an HTTP 200 status code
assert response.status_code == 200, "Request made to the model predict endpoint was unsuccessful"
# print the model predictions. Assuming the model returns a JSON object.
expected_response = json.loads(response.content)
assert expected_response == {"prediction": [25.967499846125445, 22.03428725444988, 31.2184389389109, 30.417110598250456, 21.188401444506223]}
```


# Model: XGBoost Model ONNX
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
  "mean_radius": {
    "4": 20.29,
    "5": 12.45
  },
  "mean_texture": {
    "4": 14.34,
    "5": 15.7
  },
  "mean_perimeter": {
    "4": 135.1,
    "5": 82.57
  },
  "mean_area": {
    "4": 1297.0,
    "5": 477.1
  },
  "mean_smoothness": {
    "4": 0.1003,
    "5": 0.1278
  },
  "mean_compactness": {
    "4": 0.1328,
    "5": 0.17
  },
  "mean_concavity": {
    "4": 0.198,
    "5": 0.1578
  },
  "mean_concave_points": {
    "4": 0.1043,
    "5": 0.08089
  },
  "mean_symmetry": {
    "4": 0.1809,
    "5": 0.2087
  },
  "mean_fractal_dimension": {
    "4": 0.05883,
    "5": 0.07613
  },
  "radius_error": {
    "4": 0.7572,
    "5": 0.3345
  },
  "texture_error": {
    "4": 0.7813,
    "5": 0.8902
  },
  "perimeter_error": {
    "4": 5.438,
    "5": 2.217
  },
  "area_error": {
    "4": 94.44,
    "5": 27.19
  },
  "smoothness_error": {
    "4": 0.01149,
    "5": 0.00751
  },
  "compactness_error": {
    "4": 0.02461,
    "5": 0.03345
  },
  "concavity_error": {
    "4": 0.05688,
    "5": 0.03672
  },
  "concave_points_error": {
    "4": 0.01885,
    "5": 0.01137
  },
  "symmetry_error": {
    "4": 0.01756,
    "5": 0.02165
  },
  "fractal_dimension_error": {
    "4": 0.005115,
    "5": 0.005082
  },
  "worst_radius": {
    "4": 22.54,
    "5": 15.47
  },
  "worst_texture": {
    "4": 16.67,
    "5": 23.75
  },
  "worst_perimeter": {
    "4": 152.2,
    "5": 103.4
  },
  "worst_area": {
    "4": 1575.0,
    "5": 741.6
  },
  "worst_smoothness": {
    "4": 0.1374,
    "5": 0.1791
  },
  "worst_compactness": {
    "4": 0.205,
    "5": 0.5249
  },
  "worst_concavity": {
    "4": 0.4,
    "5": 0.5355
  },
  "worst_concave_points": {
    "4": 0.1625,
    "5": 0.1741
  },
  "worst_symmetry": {
    "4": 0.2364,
    "5": 0.3985
  },
  "worst_fractal_dimension": {
    "4": 0.07678,
    "5": 0.1244
  }
}'

```
Example CLI response:
```
{"prediction": ["malignant", "malignant"]}
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
  "mean_radius": {
    "4": 20.29,
    "5": 12.45
  },
  "mean_texture": {
    "4": 14.34,
    "5": 15.7
  },
  "mean_perimeter": {
    "4": 135.1,
    "5": 82.57
  },
  "mean_area": {
    "4": 1297.0,
    "5": 477.1
  },
  "mean_smoothness": {
    "4": 0.1003,
    "5": 0.1278
  },
  "mean_compactness": {
    "4": 0.1328,
    "5": 0.17
  },
  "mean_concavity": {
    "4": 0.198,
    "5": 0.1578
  },
  "mean_concave_points": {
    "4": 0.1043,
    "5": 0.08089
  },
  "mean_symmetry": {
    "4": 0.1809,
    "5": 0.2087
  },
  "mean_fractal_dimension": {
    "4": 0.05883,
    "5": 0.07613
  },
  "radius_error": {
    "4": 0.7572,
    "5": 0.3345
  },
  "texture_error": {
    "4": 0.7813,
    "5": 0.8902
  },
  "perimeter_error": {
    "4": 5.438,
    "5": 2.217
  },
  "area_error": {
    "4": 94.44,
    "5": 27.19
  },
  "smoothness_error": {
    "4": 0.01149,
    "5": 0.00751
  },
  "compactness_error": {
    "4": 0.02461,
    "5": 0.03345
  },
  "concavity_error": {
    "4": 0.05688,
    "5": 0.03672
  },
  "concave_points_error": {
    "4": 0.01885,
    "5": 0.01137
  },
  "symmetry_error": {
    "4": 0.01756,
    "5": 0.02165
  },
  "fractal_dimension_error": {
    "4": 0.005115,
    "5": 0.005082
  },
  "worst_radius": {
    "4": 22.54,
    "5": 15.47
  },
  "worst_texture": {
    "4": 16.67,
    "5": 23.75
  },
  "worst_perimeter": {
    "4": 152.2,
    "5": 103.4
  },
  "worst_area": {
    "4": 1575.0,
    "5": 741.6
  },
  "worst_smoothness": {
    "4": 0.1374,
    "5": 0.1791
  },
  "worst_compactness": {
    "4": 0.205,
    "5": 0.5249
  },
  "worst_concavity": {
    "4": 0.4,
    "5": 0.5355
  },
  "worst_concave_points": {
    "4": 0.1625,
    "5": 0.1741
  },
  "worst_symmetry": {
    "4": 0.2364,
    "5": 0.3985
  },
  "worst_fractal_dimension": {
    "4": 0.07678,
    "5": 0.1244
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
assert expected_response == {"prediction": ["malignant", "malignant"]}
```

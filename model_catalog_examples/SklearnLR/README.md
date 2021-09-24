
# Model: Sklearn Linear Regression
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
  "avg_area_income": {
    "19": 62085.2764,
    "24": 59748.855489999994,
    "7": 78394.33928,
    "27": 64626.880979999994,
    "2": 61287.06718,
    "26": 82173.62608,
    "22": 64490.650270000006,
    "25": 56974.476539999996,
    "10": 80527.47207999999,
    "16": 79706.96306000001,
    "3": 63345.24005,
    "1": 79248.64245
  },
  "avg_area_house_age": {
    "19": 5.739410844,
    "24": 5.339339881,
    "7": 6.989779747999999,
    "27": 5.44335959,
    "2": 5.86588984,
    "26": 4.018524685,
    "22": 4.21032287,
    "25": 8.287562194,
    "10": 8.093512681,
    "16": 5.067889591,
    "3": 7.188236095,
    "1": 6.002899808
  },
  "avg_area_number_of_rooms": {
    "19": 7.091808104,
    "24": 7.748681606,
    "7": 6.620477995,
    "27": 6.988753539,
    "2": 8.51272743,
    "26": 6.992698757,
    "22": 5.4780877310000005,
    "25": 7.312879971,
    "10": 5.0427468,
    "16": 8.219771123,
    "3": 5.586728665,
    "1": 6.7308210189999995
  },
  "avg_area_number_of_bedrooms": {
    "19": 5.49,
    "24": 4.23,
    "7": 2.42,
    "27": 4.0,
    "2": 5.13,
    "26": 2.03,
    "22": 4.31,
    "25": 4.33,
    "10": 4.1,
    "16": 3.12,
    "3": 3.26,
    "1": 3.09
  },
  "area_population": {
    "19": 44922.1067,
    "24": 27809.986539999998,
    "7": 36516.35897,
    "27": 27784.742280000002,
    "2": 36882.1594,
    "26": 38853.91807,
    "22": 40358.96011,
    "25": 40694.869510000004,
    "10": 47224.35984,
    "16": 39717.81358,
    "3": 34310.24283,
    "1": 40173.07217
  }
}'

```
Example CLI response:
```
{"prediction": [1106393.5877871541, 887092.3361580996, 1545515.3180535873, 897445.6116376189, 1228049.2092442792, 1270982.1851120456, 634382.9075092981, 1390303.7282403158, 1624476.66881089, 1557072.3490927117, 1027224.6711514872, 1464234.3492581965]}
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
  "avg_area_income": {
    "19": 62085.2764,
    "24": 59748.855489999994,
    "7": 78394.33928,
    "27": 64626.880979999994,
    "2": 61287.06718,
    "26": 82173.62608,
    "22": 64490.650270000006,
    "25": 56974.476539999996,
    "10": 80527.47207999999,
    "16": 79706.96306000001,
    "3": 63345.24005,
    "1": 79248.64245
  },
  "avg_area_house_age": {
    "19": 5.739410844,
    "24": 5.339339881,
    "7": 6.989779747999999,
    "27": 5.44335959,
    "2": 5.86588984,
    "26": 4.018524685,
    "22": 4.21032287,
    "25": 8.287562194,
    "10": 8.093512681,
    "16": 5.067889591,
    "3": 7.188236095,
    "1": 6.002899808
  },
  "avg_area_number_of_rooms": {
    "19": 7.091808104,
    "24": 7.748681606,
    "7": 6.620477995,
    "27": 6.988753539,
    "2": 8.51272743,
    "26": 6.992698757,
    "22": 5.4780877310000005,
    "25": 7.312879971,
    "10": 5.0427468,
    "16": 8.219771123,
    "3": 5.586728665,
    "1": 6.7308210189999995
  },
  "avg_area_number_of_bedrooms": {
    "19": 5.49,
    "24": 4.23,
    "7": 2.42,
    "27": 4.0,
    "2": 5.13,
    "26": 2.03,
    "22": 4.31,
    "25": 4.33,
    "10": 4.1,
    "16": 3.12,
    "3": 3.26,
    "1": 3.09
  },
  "area_population": {
    "19": 44922.1067,
    "24": 27809.986539999998,
    "7": 36516.35897,
    "27": 27784.742280000002,
    "2": 36882.1594,
    "26": 38853.91807,
    "22": 40358.96011,
    "25": 40694.869510000004,
    "10": 47224.35984,
    "16": 39717.81358,
    "3": 34310.24283,
    "1": 40173.07217
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
assert expected_response == {"prediction": [1106393.5877871541, 887092.3361580996, 1545515.3180535873, 897445.6116376189, 1228049.2092442792, 1270982.1851120456, 634382.9075092981, 1390303.7282403158, 1624476.66881089, 1557072.3490927117, 1027224.6711514872, 1464234.3492581965]}
```

# Create OCI Function for invoking Model Deployment predict endpoint
This project helps create a function that will be used as a backend for API Gateway. API Gateway endpoint can then be used as a proxy server infront of Model deployment endpoint. Refer [page](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatingfirst.htm) to refer details about creating a sample function.
For more examples, refer functions examples [repo](https://github.com/oracle-samples/oracle-functions-samples).

# Adding Function as API Gateway Backend
Refer [page](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewayusingfunctionsbackend.htm) to find details about how to use function as API Gateway.

# Build using fn cli
```bash
fn -v deploy --app <app-name>
```

# oci-cli based function invocation
```bash
oci fn function invoke --function-id <function-ocid> --file "-" --body '{"ENDPOINT":"<predict-url>", "PAYLOAD": "<json-payload>"}'
```

## Sample:
```bash
oci fn function invoke --function-id <function-ocid> --file "-" --body '{"ENDPOINT":"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/<md-ocid>/predict", "PAYLOAD": "{\"index\": \"1\"}"}'
```

# fn cli based invocation
```bash
fn invoke <app-name> <function-name>
```

## Sample:
```bash
echo -n '{"ENDPOINT":"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/<md-ocid>/predict", "PAYLOAD": "{\"index\": \"1\"}"}' | fn invoke <app-name> <function-name>
```

# More information
The sample code in [func.py](./func.py) also shows how to get headers and request body. Required headers can also be passed to downstream call, if needed.
Other ways of function invocation can be found [here](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinvokingfunctions.htm)

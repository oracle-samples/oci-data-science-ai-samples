# OCI Job Monitor UI tool

Incubator project to augment the OCI console with useful functionality to support development of Data Science Jobs.

This job monitor is a Python Flask app build on top of [Oracle ADS](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html). It allows users to monitor the status and outputs of OCI data science job runs.

![Job Monitor UI](assets/images/job_monitor.png)

Features:

* See the status of recent job runs in your project in a single page.
* See logs of each job run with auto-refresh.
  * Logs are rendered with ANSI color code.
  * Support showing 1000+ log messages at the same time.
  * Logs will be displayed separately even if multiple job runs using same log ID.
  * See YAML representation of the job.
* Download the logs of a job run in a text file.
* Delete job and the corresponding runs.
* Run a new job, including distributed training job, with YAML.

## How to run

### Requirements

This tool requires `oci>=2.45.1` and `oracle-ads>=2.4.2`.

```bash
pip install oci oracle-ads flask --upgrade
```

This tool uses OCI API key for authentication. The `DEFAULT` profile in the API key will be used.

### Command Line

To start the Flask app, simply run the following command and open <http://127.0.0.1:5000/> with your browser.

```bash
OCI_PYTHON_SDK_NO_SERVICE_IMPORTS=1 FLASK_APP=job_monitor flask run
```

The dropdown options for selecting compartment ID and project ID does not support tenancy override (e.g. ociodsccust) at the moment. For that, you will need to specify the compartment ID and project ID in the URL:

```bash
http://127.0.0.1:5000/<COMPARTMENT_OCID>/<PROJECT_OCID>
```

> To change the profile and the location of the OCI KEY use following environment variables in the command line:
> OCI_KEY_PROFILE="DEFAULT"
> OCI_KEY_PROFILE="~/.oci/config"

Example:

```bash
OCI_PYTHON_SDK_NO_SERVICE_IMPORTS=1 OCI_KEY_PROFILE="DEFAULT" FLASK_APP=job_monitor flask run
```

To override tenancy, you can add the `override_tenancy` key to your OCI API key profile. For example:

```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxx
fingerprint=xxxxx
tenancy=ocid1.tenancy.oc1..xxxxx
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
override_tenancy=ocid1.tenancy.oc1..yyyyy
```

### VS Code Launch Config

The following config can be used in the VS Code `launch.json` to launch the Flask app. You may need to change the value of `FLASK_APP` to your local path if your default directory is not the root of this project.

```json
{
    "name": "Jobs Monitor",
    "type": "python",
    "request": "launch",
    "module": "flask",
    "env": {
        "FLASK_APP": "job_monitor.py",
        "FLASK_ENV": "development",
        "OCI_PYTHON_SDK_NO_SERVICE_IMPORTS": "1",
        // "RECORDING": "1",
        // OCI_KEY_PROFILE="DEFAULT",
        // OCI_KEY_PROFILE="~/.oci/config"
    },
    "args": [
        "run",
        "--no-debugger"
    ],
    "jinja": true
},
```

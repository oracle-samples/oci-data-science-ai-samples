# Jobs Client SDK Samples in Java

This section shows how to you use the Java OCI Client SDK to create, edit, run and monitor Jobs.

## Installation

Make sure you have the latest Java JDK installed on your machine or Docker. The project contains preset `pom.xml` file with the required OCI SDK and Dependancies. You can open the project for example using IntelliJ Community version and try the code.

## Setup

Before you can run the Java Classes, you need to setup following environment variables:

```bash
export PROJECT=<project ocid>
export COMPARTMENT=<compartment ocid>
export SUBNET=<subnet ocid>
export LOGGROUP=<log group ocid>
export TENANCY=<ini tenancy name>
export CONFIG=$HOME/.oci/config
```

- `PROJECT`: Data Science Service Project OCID
- `COMPARTMENT`: Data Science Service Project Compartment OCID
- `SUBNET`: VCN Private Subnet OCID to be used by the Job
- `LOGGROUP`: Log Group OCID to be used by the Job Runs to create the logs
- `TENANCY`: The name of the tenancy as set in the $HOME/.oci/config
- `CONFIG`: OCI API Key configuration location

## Samples

The project contains following files under `src/main/java`:

- `hello_world_job.py` - simple job that can be used as Job artifact
- `job_java.java` - simple Job sample in Java
- `MLJobs.java` - Java Class implementing the client OCI SDK for Jobs
- `Test.java` - Java class testing the client SDK
- `TestDelete.java` - Java class testing only the delete Job and JobRun of the client SDK for Jobs

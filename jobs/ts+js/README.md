# TypeScript and JavaScript Support for the OCI SDK

The OCI SDK supports the JavaScript langauge. This code shows how to use it.

## Install

To be able to run the sample you have to have NodeJS installed on your environment. We recommend using NVM (Linux and MacOS), in case you would like to maintain several versions at the same time.

- [NVM](https://github.com/nvm-sh/nvm)

### Node Versions

The Node and NPM versions used to test the code:

- Node >= v14.18.1
- NPM >= 8.1.1

### Oracle Cloud Infrastructure SDK for TypeScript and JavaScript

You have to install the latest version in order to test this code.

- [oci-typescript-sdk](https://github.com/oracle/oci-typescript-sdk)

To install the Oracle OCI Node SDK

```bash
npm install oci-sdk --save
```

### Run

Set your environment variables:

```bash
export PROJECT=<project ocid>
export COMPARTMENT=<compartment ocid>
export SUBNET=<subnet ocid>
export LOGGROUP=<log group ocid>
export TENANCY=<ini tenancy name>
export CONFIG=$HOME/.oci/config
```

- PROJECT: Data Science Service Project OCID
- COMPARTMENT: Data Science Service Project Compartment OCID
- SUBNET: VCN Private Subnet OCID to be used by the Job
- LOGGROUP: Log Group OCID to be used by the Job Runs to create the logs
- TENANCY: The name of the tenancy as set in the $HOME/.oci/config
- CONFIG: OCI API Key configuration location

Run the client to test Job creation and Job Run.

```bash
node client.js
```

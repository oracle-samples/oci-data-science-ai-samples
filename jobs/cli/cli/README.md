# CLI Jobs Testing

## Installation

If you want to try this samples on your local machine, we would recommend you to install and use Conda, as it allows for a good Python environment control

| :exclamation:  You would need Python 3.7+ to use the Python OCI SDK |
|-----------------------------------------|

### Using Conda

Download and install the Conda.

```bash
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh >> miniconda.sh
bash ./miniconda.sh -b -p $HOME/miniconda
cd $HOME/miniconda
./conda init <zsh or shell>
```

Create new conda environment with Python 3.7

```bash
conda create -n jobs python=3.7
```

Activate it.

```bash
conda activate jobs
```

Download and install the OCI CLI

```bash
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
pip install oci
```

## Setup

Set your tenancy variables.

| :exclamation:  Replace PROJECT, COMPARTMENT, SUBNET, LOGGROUP, TENANCY, and CONFIG with your own! |
|-----------------------------------------|

```bash
export PROJECT=<project ocid>
export COMPARTMENT=<compartment ocid>
export SUBNET=<subnet ocid>
export LOGGROUP=<log group ocid>
export TENANCY=<ini tenancy name>
export CONFIG=$HOME/.oci/config
```

You can always check the help to understand the command.

```bash
oci data-science job create --help
```

## Job

```bash
oci data-science job create --display-name clijob --project-id $PROJECT --compartment-id $COMPARTMENT --configuration-details file://job_config_details.json --infrastructure-configuration-details file://job_infra_config_details.json --log-configuration-details file://job_log_configuration_details.json --config-file $CONFIG --profile $TENANCY
```

Get the job OCID and export it to use for the rest of the commands.

```bash
export JOB=ocid1.datasciencejob.oc1.iad.amaaaaaanif7xwiaktme3tic34wss5d63afhvl27mfep4cxvqoa7za3cly3a
```

```bash
oci data-science job create-job-artifact --job-id $JOB --job-artifact-file hello_world_job.py --content-disposition 'attachment; filename=hello_world_job.py' --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job get-artifact-content --job-id $JOB --file download.py --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job head-job-artifact --job-id $JOB --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job list --compartment-id $COMPARTMENT --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job update --job-id $JOB --display-name clijobupdate --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job get --job-id $JOB --config-file $CONFIG --profile $TENANCY
```

## Job Run

```bash
oci data-science job-run --help
```

```bash
oci data-science job-run create --compartment-id $COMPARTMENT --job-id $JOB --project-id $PROJECT --configuration-override-details file://job_configuration_override_details.json  --log-configuration-override-details file://job_log_configuration_override_details.json --config-file $CONFIG --profile $TENANCY
```

```bash
export JOBRUN=ocid1.datasciencejobrun.oc1.iad.aaaaaaaaeqjepijojvlxmunjidu6bvw7aep32gelazccxlkt5skxncar37iq
```

```bash
oci data-science job-run get --job-run-id $JOBRUN --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job-run update --job-run-id $JOBRUN --display-name jobrunupdated --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job-run list --compartment-id $COMPARTMENT --job-id $JOB --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job-run cancel --job-run-id $JOBRUN --config-file $CONFIG --profile $TENANCY
```

## Delete

```bash
oci data-science job-run delete --job-run-id $JOBRUN --config-file $CONFIG --profile $TENANCY
```

```bash
oci data-science job delete --job-id $JOB --config-file $CONFIG --profile $TENANCY
```

## List Shapes

```bash
oci data-science job-shape list --compartment-id $COMPARTMENT --config-file $CONFIG --profile $TENANCY
```

## Advanced

Search for a job by lifecycle status and display name

```bash
jobOCID=`oci data-science job list --compartment-id $COMPARTMENT --display-name $YOURJOBNAME --lifecycle-state ACTIVE | grep ocid1.datasciencejob.oc1 | cut -d "\"" -f 4`
```

... then use that $jobOCID for operations like:

Delete a Job

```bash
oci data-science job delete --job-id $jobOCID
```

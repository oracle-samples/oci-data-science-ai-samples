# Simple bash script Job

This script can be ran as a Job too. Notice it takes Command Line Arguments. This means for this script to be successful you have to provide a command line arguments on a Job Run.

Programatically the command line arguments can be set over the `commandLineArguments` property like this:

On Job

```json
"jobConfigurationDetails": {
    "jobType": "DEFAULT",
    "environmentVariables": {
    },
    "commandLineArguments": "100 linux \"hi there\""
}
```

On Job Run

```json
"jobConfigurationOverrideDetails": {
    "jobType": "DEFAULT",
    "environmentVariables": {
    },
    "commandLineArguments": "100 linux \"hi there\""
}
```

## Run

You can run this file as a Job from the **python/sdk** folder:

```bash
python python/sdk/mljobs.py -f shell/shell-with-args.sh
```

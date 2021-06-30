> # "No module name ads" Error

### This error message is commonly seen when either of these two scenarios happen: 

1. Make sure you have a conda environment installed.
Steps for this:

    - click on the plus sign in the left-hand menu bar
    - click environment explore
    - choose a conda pack, e.g. general machine learning for cpu
    - click install
    - copy installation command shown on the card
    - run installation command in terminal
    - activate installed environment, e.g. `conda activate /home/datascience/conda/mlcpuv1`
    - open a notebook and choose the installed environment as kernel
    - `import ads`

    More information here: https://blogs.oracle.com/ai-and-datascience/post/new-conda-environment-feature-available-in-oracle-cloud-infrastructure-data-science

2. Confirm you have Internet access from the notebook session
  
    - Try `curl oracle.com` in terminal to see if you have Internet access to service gateway connection

    - Ensure that your VCN and subnet are configured to route traffic through either the NAT gateway or the service gateway so that the conda environments can be listed

    - Connectivity is required in order to use Conda Environments. Choose a different VCN/Subnet for your Notebook Session or see our documentation for [automated](https://docs.oracle.com/en-us/iaas/data-science/using/orm-configure-tenancy.htm) and [manual](https://docs.oracle.com/en-us/iaas/data-science/using/configure-tenancy.htm#create-vcn) instructions in how to configure your OCI Virtual Network

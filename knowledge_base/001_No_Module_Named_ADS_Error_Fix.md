# "No module name ads" Error

## This error message is commonly seen when either of these two scenarios happens:

1. Ensure that a conda environment is installed. If you do not have one installed, follow these steps to install one:
    1. Select File -> New Launcher to open the Launcher tab.
    1. Click Environment Explorer.
    1. Review the available conda environments and determine which one you would like to install. Ensure that the conda environment contains the ADS library. It will be listed along with the other key libraries that are installed. If you are not sure which conda environment to install, we suggest you use General Machine Learning for CPUs.
    1. Select the Install tab in the environment card.
    1. Copy the installation command shown on the card.
    1. Select File -> New -> Terminal to open a terminal tab.
    1. Paste the installation command into the terminal tab and run the command.
    1. Select File -> New -> Notebook to open a new notebook.
    1. In the Select Kernel dialog choose the conda environment that you installed. If it does not appear wait a few seconds and try again.
    1. In a cell type `import ads` and execute the cell. ADS should now be available.

For more information see the blog post [New Conda Environment feature available in Oracle Cloud Infrastructure Data Science](https://blogs.oracle.com/ai-and-datascience/post/new-conda-environment-feature-available-in-oracle-cloud-infrastructure-data-science).

1. Confirm that you have Internet access from the notebook session. Follow these steps to confirm this.
    1. Select File -> New -> Terminal to open a terminal tab.
    1. Run the command `curl -s oracle.com > /dev/null | echo $?`.
    1. If `0` is returned then you have Internet access. Any other value suggests that you do not have internet access.

- Ensure that your VCN and subnet are configured to route traffic through either a NAT gateway or service gateway. The most common cause of this is that the public VCN was selected when configuring the notebook session. The private VCN should have been selected. This may not be the case for your network configuration but for most configurations, this is the issue. To change the VCN, go to the Notebook Sessions page in the OCI console and select Deactivate. When the notebook session has deactivated, activate it by clicking the Activate button. At this time a dialog will appear and you can change the VCN.
- Connectivity is required in order to use conda environments. Choose a different VCN/Subnet for your Notebook Session or see our documentation for [automated](https://docs.oracle.com/en-us/iaas/data-science/using/orm-configure-tenancy.htm) and [manual](https://docs.oracle.com/en-us/iaas/data-science/using/configure-tenancy.htm#create-vcn) instructions in how to configure your OCI Virtual Network

___

*Oracle Cloud Infrastructure (OCI)*

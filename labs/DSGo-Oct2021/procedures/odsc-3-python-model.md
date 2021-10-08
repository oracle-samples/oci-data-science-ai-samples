# Lab 3 - Build A Model Using Python

## Introduction

This lab will guide you through a practical example of how to train, evaluate, and catalog a machine learning model. The notebook you will use describes the details of the use case.

Estimated lab time: 15 minutes

### Objectives
In this lab you will:
* Learn how to install a conda environment in your notebook session
* Execute Python code in a notebook to explore data, prepare data, train a model, and evaluate the model.
* Store the model in the model catalog

### Prerequisites
* You are signed-in to Oracle Cloud
* You have navigated to Data Science
* You have selected the **DataScienceHOL** compartment
* You have opened the project you created in Lab 1
* You have a notebook session in your project that is Active

## **STEP 1:** Open a Notebook Session

1. Confirm you have completed all the prerequisites and are viewing your Data Science project. (Your project name and notebook session name will be different than what is shown in the image.)
    ![](images/ds-project-holuser.png)

1. Under Resources, click **Notebook Sessions** if it is not already selected.

1. Click on the notebook session named **LabNotebookSession** to open it.

1. Click on **Open**. It will open in a separate browser tab. If prompted to sign-in, provide your Oracle Cloud credentials.
  ![](images/ns-open.png)

1. Ensure you are viewing the browser tab/window displaying *LabNotebookSession*.  
  ![](images/notebook-session.png)

  This is JupyterLab. It can be seen that the screen is split into two sections. By default, the left side has the file browser open but it can change based on what navigation icons are selected on the far left side of the screen. The right side of the screen contains the workspace. It will have a notebook, terminal, console, launcher, notebook examples, etc..

  There is a menu across the top of the screen. For this lab, the most interesting menu item is *Run*. It will allow you to execute code cells in the notebook. It is recommended that you manually execute the cells one at a time as you progress through the notebook. It is important that you execute them in order. To do this from the keyboard, press *shift + enter* in a cell and it will execute it and advance to the next cell. Alternatively, you can run all of the cells at once. To do this, click on Run then "Run All".

## **STEP 2:** Install a Conda Environment   TODO

A Conda environment is a collection of libraries, programs, components and metadata. It defines a reproducible set of libraries that are used with notebook session, model deployments, and jobs. The Data Science Conda environments included with the service also include many sample notebooks. The following instructions will guide you through installing a Conda that works with the prepared notebook.

  1. In the *Launcher* tab, click **Environment Explorer**
    ![](images/notebook_launcher.png)

  1. In the *Environment Explorer* tab, select the **Data Science Conda Environment** filter button, select **CPU** architecture filter, then scroll down until you find the TODO **tensorflow26** conda. (If you see no results, use the refresh button on the right side of the filter bar of the Environment Explorer.)
    ![](images/notebook_ee_condaTF.png)

  1. Select the **Install** tab and then click the **copy** button to copy the installation command.
    TODO change image
    ![](images/notebook_ee_condaPT.png)

  1. Go back to the *Launcher* tab and select **Terminal** to open a terminal window.

  1. Paste the command into the terminal window and hit **Return** to execute it. (The command that you previously copied is  TODO `odsc conda install -s pytorch18_p37_cpu_v1`)

  1. You will receive a prompt related to what version number you want. Press `Enter` to select the default.

  It takes about 3-5 minutes for the conda package to be installed. You can continue with the next step while you're waiting for the installation to be completed.

## **STEP 3:** Download the notebook
A notebook has been prepared containing all the necessary Python code to explore the data, train the model, evaluate the model, and store it in the model catalog.

TODO
  - download zip of repo and upload just the notebook
  - clone repo to notebook session

  1. The files needed for this workshop are located in the **oci-data-science-ai-samples** public repository on Github. Open this [Github link](https://github.com/oracle/oci-data-science-ai-samples/archive/refs/heads/master.zip) to download a zip of the repository and save it to your local machine.

  1. Unzip the repository and find `oci-data-science-ai-samples-dsgo.zip\oci-data-science-ai-samples-dsgo\labs\DSGo-Oct2021\notebooks\employee-attrition.ipynb`

  x. (https://github.com/wprichard/oci-data-science-ai-samples/tree/master/labs/DSGo-Oct2021) in a new tab of your web browser.

  x. In Github, open the notebook folder and download the notebook `employee-attrition.ipynb` to you local computer. (Right click the file and select `Save file as`.)

  1. Drag and drop the downloaded `employee-attrition.ipynb` from your computer's file explorer into your notebook session's root folder.
    TODO image

  1. Before proceeding, confirm that your conda installation (from the previous step) is complete. Switch back to the terminal tab in the notebook session and confirm that your conda is now installed.
    TODO image

## **STEP 4:** Open the Notebook
You will open the notebook and step through it.

  1. In the notebook session's file browser, open notebook **employee-attrition.ipynb**

  Select the file browser on the left side of the user interface if it is not already visible. Double-click on **employee-attrition.ipynb**. A new tab opens in the workspace on the right.

  1. Notice in the upper right corner of the notebook tab, it displays the name of the conda environment being used by this notebook. TODO - switch conda?

  1. Now you will work in the notebook. Scroll through each cell and read the explanations. When you encounter a `code` cell, execute it (using **shift + enter**) and view the results. For executable cells, the "\[ ]" changes to a "[\*]" while executing, then a number "[1]" when complete .

  (If you run short on time, you can use the *Run* menu to run the remaining cells and the review the results.)

  1. **Stop** when you get to the cell that says to ***Deploy your model through Model Deployment***. We'll deploy in the next lab and come back to the notebook after we deploy the model.


**You can [proceed to the next lab](#next).**

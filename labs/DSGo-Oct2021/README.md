# DSGo Employee Attrition Workshop

This lab is built for use as a workshop at the Data Science Go (DSGo) conference in October 2021. It uses Oracle Cloud Infrastructure (OCI) Data Science to create a model to predict employee attrition. The workshop guides the user through developing a machine learning model and performing all the steps to deploy the model into production. The user creates a machine learning model then creates a model artifact and stores it in the Model Catalog. Using the console, the model is deployed and then called as a REST API endpoint to perform inference operations on the model.

### Prerequisites
  - None

This workshop is designed for users that will register for a new OCI trial account with free cloud credits.  The workshop provides instructions to sign up for a free trial account and then configure the tenancy for Data Science. The remainder of the workshop guides the user through the activities to build, train, and deploy a machine learning model.

**DSGo participants need to sign-up for their OCI account with the same email that was provided to Oracle when registering for the workshop.** By doing so, DSGo participants receive additional free cloud credits and no payment method verification.

Other users of this workshop may sign-up for a standard OCI trial account that provides free cloud credits but requires payment method verification as an identity check. (The user is not charged during the free trial and the user has the option to continue with free tier services or explicitly convert to a paid account at the end of the trial. Note that OCI Data Science is not included in the OCI free tier.)

If you choose to use an existing OCI trial account, your 30-day trial must still be active and you must have credits remaining on your account to cover the services used in this workshop. (Your trial status is displayed in the OCI console.)

You may of course also use a paid OCI account, however the instructions are designed for a new trial account, and your account will be charged for the services used during this workshop.

### Workshop Modules
  - [Lab 0 - Setup a tenancy for OCI Data Science](procedures/odsc-0-tenancy-setup-stack.md)
  - [Lab 1 - Introduction, Sign-in, and Navigation](procedures/odsc-1-intro.md)
  - Lab 2 - removed
  - [Lab 3 - Build A Model Using Python](procedures/odsc-3-python-model.md)
  - [Lab 4 - Deploy A Model and Invoke It](procedures/odsc-4-deploy-model.md)
  - [Lab 5 - Shutting Down a Notebook Session](procedures/odsc-5-notebook-shutdown.md)

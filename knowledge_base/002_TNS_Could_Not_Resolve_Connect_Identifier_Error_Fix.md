# "ORA-12154: TNS:could not resolve the connect identifier specified" Error

## This error message commonly shows up for the following 2 reasons:
1. Incorrect wallet configuration.
   1. Follow [instructions here](https://github.com/oracle/oci-data-science-ai-samples/blob/master/environment_examples/database/autonomous_database.ipynb), if you haven't already, to download the wallet and unzip it locally.
   2. Next, within `~/.database` directory there should be a folder with your database name. Within your database name directory you will find your database configuration files.  There are several things to confirm:
      1. Check that `sqlnet.ora` file has the wallet location referenced. 
      For example sqlnet.ora will have a part like `(METHOD_DATA = (DIRECTORY="/home/datascience/.database/MyDatabase")))`
      2. Check the connection identifier is found in the `tns_names.ora`. 
      For example there should be a section like `dbtest123_low = (description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=...`
      3. Lastly check connection with sql*plus. This will confirm username/password and wallet are valid. Template for command:
      `sqlplus <user_name>/<password>@<protocol>://<host>:<port>/<service_name>?wallet_location="<unziped_wallet_location>"`
2. Incorrect connection identifier (specified as `database_name` in credentials dictionary in `autonomous_database.ipynb` notebook).
   - If this is ADW then when updating credentials, for database name we want to be using the [connection identifier](https://docs.oracle.com/cd/E11882_01/network.112/e41945/glossary.htm#BGBBGCEG) which will usually end in _high, _medium or _low. All three allow you to connect to the same database but they give different levels of number of concurrent SQL statements allowed to be run along with different CPU and IO resources available for each.

Note: This error message will not show up if you have an incorrect user name or password, in that case you will get "ORA-01017: invalid username/password; logon denied"

Futher documentation provided [here](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/user_guide/configuration/configuration.html?highlight=autonomous%20database#setup-for-adb) as well.

___

*Oracle Cloud Infrastructure (OCI)*

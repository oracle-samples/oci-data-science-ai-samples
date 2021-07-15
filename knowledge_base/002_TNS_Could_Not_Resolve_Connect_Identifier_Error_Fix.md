# "ORA-12154: TNS:could not resolve the connect identifier specified" Error

## This error message commonly shows up for the following 2 reasons:
1. Incorrect wallet configuration when using an Oracle database.
   1. If you have not already downloaded and unzipped the wallet, follow these [instructions](https://github.com/oracle/oci-data-science-ai-samples/blob/master/environment_examples/database/autonomous_database.ipynb) to do so.
   2. Locate the path that contains your database configuration files. If you followed these [instructions](https://github.com/oracle/oci-data-science-ai-samples/blob/master/environment_examples/database/autonomous_database.ipynb) they will be in a sub-folder of the `~/.database` folder. The sub-folder in generally the name of the database and it is the location of the wallet files. Using the wallet files, confirm:
      1. The `sqlnet.ora` file must have the wallet location referenced.  This would be the path to the location where the `sqlnet.ora` file is located (do not include the filename, just the path).
      For example sqlnet.ora will have a part like `(METHOD_DATA = (DIRECTORY="/home/datascience/.database/MyDatabase")))`
      2. Examine the `tns_names.ora` file and ensure that the connection identifier you are using is identical to one of the ones listed in that file.
      For example there should be a section like `dbtest123_low = (description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=...` where `dbtest123` is generally the name of your database.
       3. Use sql*plus to confirm that your username, password, and wallet are valid. From a terminal window inside the notebook session use a command like the following:
       - Template for commad:
       `sqlplus <user_name>/<password>@<protocol>://<host>:<port>/<service_name>?wallet_location="<unziped_wallet_location>"`
        e.g. `sqlplus admin/admin_password@tcps://adb.us-ashburn-1.oraclecloud.com:1522/q9tjyjeyzhxqwla_db202011251996_high.adwc.oraclecloud.com?wallet_location="/home/datascience/.database/DB202011251996"`
        - You can find the `protocol`, `host`, `port` and `service_name` values in the  [`tnsnames.ora`](https://docs.oracle.com/cd/B28359_01/network.111/b28317/tnsnames.htm#NETRF007) file
2. Incorrect connection identifier (specified as `database_name` in credentials dictionary in `autonomous_database.ipynb` notebook).
   - For most databases, the `database_name` variable is the name of the database. However, for any of the autonomous databases (ADB) you will need to use the connection identifier. Generally, this is the name of the database followed by `_high`, `_medium` or `_low`. However, your database may have non-standard connection identifier names. The `tns_names.ora` file contains a list of connection identifiers.

Note: This error message will not show up if you have an incorrect username or password, in that case, you will get "ORA-01017: invalid username/password; logon denied"

Futher documentation provided [here](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/user_guide/configuration/configuration.html?highlight=autonomous%20database#setup-for-adb) as well.

___

*Oracle Cloud Infrastructure (OCI)*

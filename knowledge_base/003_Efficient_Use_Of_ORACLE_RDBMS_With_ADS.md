# Using Oracle RDBMS with Pandas in OCI Data Science Notebooks

When using the Oracle RDBMS with Python the most common representation of tabular data is  a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) - once in a dataframe there are many operations that can be performed from visualization to persisting in a variety of formats.

The Pandas `read_sql(...)` function is a general, database independent, approach that uses [SQLAlchemy - Object Relational Mapper](https://www.sqlalchemy.org/) to arbitrate between specific database types and Pandas.

> Read SQL query or database table into a DataFrame.

>This function is a convenience wrapper around read_sql_table and `read_sql_query` (for backward compatibility). It will delegate to the specific function depending on the provided input. A SQL query will be routed to read_sql_query, while a database table name will be routed to `read_sql_table`.

ADS (2.3.1+) (found in the Conda pack: *"Data Exploration and Manipulation for CPU V2"*) recommends using the **ADS provided drop-in altertive**, this can be up to 15x faster than `Pandas.read_sql()` since it bypasses the ORM, and is written to take advantage of being specific for the Oracle RDBMS.

Rather than `pd.read_sql` instead use the Pandas mixin, `pd.DataFrame.read_sql(...)`

## Examples of querying data from Oracle RDBMS


>         Examples:
        --------
        >>> connection_parameters = {
                "user_name": "<username>",
                "password": "<password>",
                "service_name": "{service_name}_{high|med|low}",
                "wallet_location": "/full/path/to/my_wallet.zip",
            }
        >>> import pandas as pd
        >>> import ads

>       >>> # simple read of a SQL query into a dataframe with no bind variables
>       >>> df = pd.DataFrame.ads.read_sql(
            "SELECT * FROM SH.SALES",
            connection_parameters=connection_parameters,
        )

>       >>> # read of a SQL query into a dataframe with a bind variable. Use bind variables
>       >>> # rather than string substitution to avoid the SQL injection attack vector.
>       >>> df = pd.DataFrame.ads.read_sql(
              """
              SELECT
                *
              FROM
                SH.SALES
              WHERE
                ROWNUM <= :max_rows
              """,
              bind_variables={
                max_rows = 100
              },
              connection_parameters=connection_parameters,
        )

## Performance

The performance is limited by three things:

 - Generational latency, how long the database takes to return rows, use of indexes and writing efficient SQL mitigates this performance bottleneck.

 - Network saturation, once the network is saturated data cannot be delivered between database and notebook environment any faster. OCI networking is very fast and this is not usually a concern, except for example when the network path goes over VPN or other more complex routing topologies.

- CPU latency in the notebook, python has to marshall the byte stream delivered by the database into python data types before being promoted to Numpy objects for Pandas. There is additionally a cryptographic CPU overhead since the data in transit is secured with PKI (Public key infrastructure.)

## Writing data to the Oracle RDBMS (from a Pandas DataFrame)

Typically this would be done using `df.to_sql`, however, once again, this will use the ORM to marshall data and is inefficient. Instead use the Pandas ADSS mixin.

Given a dataframe (`df`) writing this to the database is as simple as:

>        >>> df.ads.to_sql(
            table_name,
            connection_parameters=connection_parameters,
            if_exists="replace"
        )

The resulting data types, if the table was created, would be:

>
                "bool": "NUMBER(1)",
                "int16": "NUMBER(5)",
                "int32": "NUMBER(10)",
                "int64": "NUMBER(19)",
                "float16": "NUMBER(5, 4)",
                "float32": "NUMBER(10, 4)",
                "float64": "NUMBER(19, 4)",
                "int16": "INTEGER",
                "int32": "INTEGER",
                "int64": "INTEGER",
                "float16": "FLOAT",
                "float32": "FLOAT",
                "float64": "FLOAT",
                "datetime64": "TIMESTAMP",

When a table is created the length of VARCHAR2 columns is computed from the longest string in the column. The ORM would default to CLOB data which is stored outside of the main table space and is inefficient and awkward to use. ADS fixes this by creating the correct in-table-space data type and sets the right length. 

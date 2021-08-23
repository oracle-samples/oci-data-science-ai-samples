# Using Oracle RDBMS with Pandas in OCI Data Science Notebooks

When using the [Oracle RDBMS](https://www.oracle.com/database/) with Python the most common representation of tabular data is  a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) - once in a dataframe there are many operations that can be performed, from visualization to persisting in a variety of formats.

## Reading data from the Oracle RDBMS (to a Pandas DataFrame)


The Pandas `read_sql(...)` function is a general, database independent, approach that uses [SQLAlchemy - Object Relational Mapper](https://www.sqlalchemy.org/) to arbitrate between specific database types and Pandas.

> Read SQL query or database table into a DataFrame.

>This function is a convenience wrapper around read_sql_table and `read_sql_query` (for backward compatibility). It will delegate to the specific function depending on the provided input. A SQL query will be routed to read_sql_query, while a database table name will be routed to `read_sql_table`.

ADS (2.3.1+) (found in the Conda pack: *"Data Exploration and Manipulation for CPU V2"*) recommends using the **ADS provided drop-in alternative**, this can be up to 15x faster than `Pandas.read_sql()` since it bypasses the ORM, and is written to take advantage of being specific for the Oracle RDBMS.

Rather than `pd.read_sql` instead use the Pandas ADS accessor drop-in replacement, `pd.DataFrame.read_sql(...)`

### Examples of querying data from Oracle RDBMS


```python  

  >>> connection_parameters = {
          "user_name": "<username>",
          "password": "<password>",
          "service_name": "{service_name}_{high|med|low}",
          "wallet_location": "/full/path/to/my_wallet.zip",
      }
  >>> import pandas as pd
  >>> import ads

  >>> # simple read of a SQL query into a dataframe with no bind variables      
  >>> df = pd.DataFrame.ads.read_sql(
        "SELECT * FROM SH.SALES",
        connection_parameters=connection_parameters,
    )

  >>> # read of a SQL query into a dataframe with a bind variable. Use bind variables
  >>> # rather than string substitution to avoid the SQL injection attack vector.
  >>> df = pd.DataFrame.ads.read_sql(
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
```

### Performance

The performance is limited by three things:

- Generational latency, how long the database takes to return rows, use of indexes and writing efficient SQL mitigates this performance bottleneck.

- Network saturation, once the network is saturated data cannot be delivered between database and notebook environment any faster. OCI networking is very fast and this is not usually a concern, except for example when the network path goes over VPN or other more complex routing topologies.

- CPU latency in the notebook, python has to marshall the byte stream delivered by the database into python data types before being promoted to Numpy objects for Pandas. There is additionally a cryptographic CPU overhead since the data in transit is secured with PKI (Public key infrastructure.)

### Large result sets

If a database query returns more rows that the memory of the client permits there are a couple of easy options. The simplest is to use a larger client shape, along with increased compute performance, larger shapes come with more RAM.

If that's not an option then you can use the `pd.DataFrame.ads.read_sql` mixin in chunk mode, where the result is no longer a Pandas DataFrame, but rather an iterator over a sequence of DataFrames. Using this makes possible, for example, reading a large data set and writing it to Object storage, or local file system with the following example.

```python
	for i, df in enumerate(pd.DataFrame.ads.read_sql(
	        "SELECT * FROM SH.SALES",
	        chunksize=100000 # rows per chunk,
	        connection_parameters=connection_parameters,
	      ))
	   # each df will contain up to 100000 rows (chunksize)
	   # to write the data to object storage use oci://bucket#namespace/part_{i}.csv"
	   df.to_csv(f"part_{i}.csv")
```

### Very Large result sets

If the data exceeds what's practical in a notebook, then the next step would be to use [OCI Data Flow Service](https://www.oracle.com/big-data/data-flow/), this partitions the data across multiple nodes and can handle data of any size, up to the size of the cluster.
   

## Writing data to the Oracle RDBMS (from a Pandas DataFrame)

Typically this would be done using `df.to_sql`, however, once again, this will use the ORM to marshall data and is less efficient that code that has been optimized for a specific database.

Instead use the Pandas ADS accessor mixin.

Given a dataframe (`df`) writing this to the database is as simple as:

```python
	>>> df.ads.to_sql(
	    "MY_TABLE",
	    connection_parameters=connection_parameters,
	    if_exists="replace"
	)
```

The resulting data types (if the table was created by ADS, as opposed to inserting into an existing table), would be governed by the below table:

|Pandas|Oracle|
|------|------|
|bool|NUMBER(1)|
|int16|NUMBER(5)|
|int32|NUMBER(10)|
|int64|NUMBER(19)|
|float16|NUMBER(5| 4)|
|float32|NUMBER(10| 4)|
|float64|NUMBER(19| 4)|
|int16|INTEGER|
|int32|INTEGER|
|int64|INTEGER|
|float16|FLOAT|
|float32|FLOAT
|float64|FLOAT|
|datetime64|TIMESTAMP|
|string|VARCHAR2(<max length of actual data>)|


When a table is created the length of any `VARCHAR2` columns is computed from the longest string in the column. The ORM would default to `CLOB` data which is not correct, nor is it efficient. CLOBS are stored efficiently by the database but the c api to query them works differently, the non LOB columns are returned to the client through a cursor, but LOBs are handled differently, resulting in an additional network fetch per row, per LOB column. ADS deals with this by creating the correct data type, and setting the right `VARCHAR2` length.

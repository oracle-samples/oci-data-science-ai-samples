## Overview

Customers store time-series data collected from Enterprise Apps,
Edge devices, Sensors … in ADW, ATP, Object Store, and on-premises database systems.
AD Service requires time series data sets in persistent stores to be in a particular format
(/schema) and imposes strict restrictions on names of columns, column types & the number of signal columns.
Customers need the ability to pre-process (enrich/transform) data points stored in their persistent storage systems (detailed above),
convert the data into the format expected by AD Service, and then consume it to train models and perform inference.

## Solution

Through this repo, we would like to demonstrate multiple ways through which you can transform, preprocess and cleanse your
data to detect anomalies on the same. These examples span across 2 solutions, namely OCI Data Flow and OCI Data Integration Service
and can perform a wide variety of preprocessing based on the data demands.


<b>Important links</b>:

1. OCI Anomaly Detection service Data [requirements](https://docs.oracle.com/en-us/iaas/Content/anomaly/using/data-require.htm#data_require)
2. [OCI Data Flow](https://www.oracle.com/big-data/data-flow/)
3. [OCI Data Integration Service](https://docs.oracle.com/en-us/iaas/data-integration/home.htm)

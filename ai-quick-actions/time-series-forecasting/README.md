# Time Series Forecasting with Pretrained Models

## Overview

Oracle AI Quick Actions now support hosting and using pretrained time-series forecasting models with a few clicks. As
part of this, we’ve added support for the Granite-TimeSeries TTM (TinyTimeMixer) model, which offers lightweight,
high-accuracy forecasting for multivariate time series data. This is the first of several pretrained models we aim to
support through our AI Quick Actions interface.

Granite TTM provides state-of-the-art performance in zero-shot scenarios and is especially well-suited for short-to-mid
range forecasting on CPU-only environments.

## Deploying the Model using AI Quick Action

Users can navigate to the **AI Quick Actions UI** and select **Model Explorer**. From there, select
`granite-timeseries-ttm-r1` from the provided models and then click **"Deploy"**. Once deployed, an endpoint URL will be
provided for invoking predictions via a REST API.
The deployment handles model loading, environment setup, and endpoint exposure automatically.

## Request Payload Structure

| Key              | Type          | Required | Description                                                                                                                 |
|------------------|---------------|----------|-----------------------------------------------------------------------------------------------------------------------------|
| historical_data  | object        | Yes      | Dictionary representing historical data                                                                                     |
| timestamp_format | string        | No       | Format of the timestamp values in the timestamp_column e.g. "%Y-%m-%d %H:%M:%S"                                             |
| timestamp_column | string        | Yes      | Name of the datetime column                                                                                                 |
| target_columns   | array[string] | Yes      | Columns to be predicted                                                                                                     |
| id_columns       | array[string] | No       | List of column names which identify different time series in a multi-time series input (For multi-series forecast use case) | 

### Example Payload For Single Time Series Forecast (without id_columns)

```json
{
"historical_data": 
  {
    "instant": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "dteday": ["2011-01-01 00:00:00", "2011-01-01 01:00:00", "2011-01-01 02:00:00", "2011-01-01 03:00:00", "2011-01-01 04:00:00",
                "2011-01-01 05:00:00", "2011-01-01 06:00:00", "2011-01-01 07:00:00", "2011-01-01 08:00:00", "2011-01-01 09:00:00",
                "2011-01-01 10:00:00", "2011-01-01 11:00:00", "2011-01-01 12:00:00", "2011-01-01 13:00:00", "2011-01-01 14:00:00"],
    "season": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "yr": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "mnth": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "hr": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "holiday": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "weekday": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    "workingday": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "weathersit": [1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2],
    "temp": [0.24, 0.22, 0.22, 0.24, 0.24, 0.24, 0.22, 0.2, 0.24, 0.32, 0.38, 0.36, 0.42, 0.46, 0.46],
    "atemp": [0.2879, 0.2727, 0.2727, 0.2879, 0.2879, 0.2576, 0.2727, 0.2576, 0.2879, 0.3485, 0.3939, 0.3333, 0.4242, 0.4545, 0.4545],
    "hum": [0.81, 0.8, 0.8, 0.75, 0.75, 0.75, 0.8, 0.86, 0.75, 0.76, 0.76, 0.81, 0.77, 0.72, 0.72],
    "windspeed": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0896, 0.0, 0.0, 0.0, 0.0, 0.2537, 0.2836, 0.2836, 0.2985, 0.2836],
    "casual": [3, 8, 5, 3, 0, 0, 2, 1, 1, 8, 12, 26, 29, 47, 35],
    "registered": [13, 32, 27, 10, 1, 1, 0, 2, 7, 6, 24, 30, 55, 47, 71],
    "cnt": [16, 40, 32, 13, 1, 1, 2, 3, 8, 14, 36, 56, 84, 94, 106]
	},
"timestamp_column": "dteday",
"timestamp_format": "%Y-%m-%d %H:%M:%S",
"target_columns": ["cnt","casual"]
}
```
### Sample Output 
```json

{
  "forecast": [
    {
      "cnt_prediction": [79.7074593556, 67.1107353027, ...],
      "casual_prediction": [26.6367874235, 21.9595151501, ...]
    }
  ]
}
```

### Example Payload For Multi-Time Series Forecast (with id_columns)
```json
{
  "historical_data": {
    "Store": [1, 2, 2, 1, 1, 2],
    "Date": ["2013-01-01", "2013-01-01", "2013-01-02", "2013-01-02", "2013-01-03", "2013-01-03"],
    "Sales": [10, 10, null, 223, 10, 3232],
    "DayOfWeek": [2, 2, 3, 3, 4, 4],
    "Customers": [0, 0, 650, 668, 578, 555]
  },
  "timestamp_column": "Date",
  "target_columns": ["Sales"],
  "timestamp_format": "%Y-%m-%d",
  "id_columns": ["Store"]
}
```

### Sample Output 
```json
{
  "forecast": [
    {
      "Sales_prediction": [41.57, 44.79, ..., 70.84],
      "Store": 1
    },
    {
      "Sales_prediction": [1594.56, 1407.68, ..., 1151.16],
      "Store": 2
    }
  ]
}
```

### FAQ

#### What is the model's context and forecast length?

This model uses a context window of 512 past points and forecasts 96 future points by default

#### What happens if my data has missing timestamps or gaps?

Missing values are handled by the TimeSeriesPreprocessor from the tsfm library. If the data contains missing values,
they must be included as null in the input payload otherwise it can lead to errors like: "All arrays must be of the same
length".

#### Is GPU required?

No. TTM is CPU-efficient and suitable for inference on standard OCI compute shapes.

#### Can I monitor the deployed endpoint?

Yes, standard OCI endpoint monitoring (logs, metrics) is supported.

## References

 [Granite TTM on Hugging Face](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1)

 [IBM Research Paper](https://arxiv.org/abs/2401.03955)
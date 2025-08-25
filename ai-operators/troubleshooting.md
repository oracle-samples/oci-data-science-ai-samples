# ADS Forecast Operator Troubleshooting

Below is a consolidated catalogue of every error class that can be raised by the ADS Forecast Operator, why it occurs, and how to fix or prevent it.

| Error / Exception | When & Why it is Raised | How to Resolve / Prevent |
| :--- | :--- | :--- |
| **ForecastSchemaYamlError** | Your `forecast.yaml` is syntactically valid YAML but violates the schema (missing required keys, wrong data-types, invalid enum values, etc.). | • Run `adgits operator verify -f forecast.yaml` to see the exact field that is wrong.<br>• Cross-check against `ads/opctl/operator/lowcode/forecast/schema.yaml` and correct the offending key or value. |
| **ForecastInputDataError** | A required dataset cannot be read or fails validation (e.g. empty file, wrong delimiter, corrupt parquet). | • Ensure the URL / path is correct and accessible (OCI auth for Object Storage, local path otherwise).<br>• Confirm the file format matches the `format:` field. |
| **DataMismatchError** | 1. Historical dataset’s columns do not equal the set of expected columns (`Transformations._check_historical_dataset()`).<br>2. Additional data are not aligned with the historical index or horizon (`ForecastDatasets.AdditionalData`). | • Verify the CSV or DB table has exactly: `target_column`, `datetime_column`, and optional `target_category_columns`.<br>• For additional data, make sure every (Date, Series) that exists in historical data is present, and that it also extends at least `horizon` rows into the future. |
| **InvalidParameterError** | A generic guard around many configuration & ingestion problems. Typical triggers:<br>• `datetime_column.format` does not match the literal dates.<br>• Unsupported `format:` value in an InputData section.<br>• Neither `url` nor `connect_args` provided. | • Supply the correct `strftime` format (`%Y-%m-%d`, `%d/%m/%Y`, …).<br>• Use one of the allowed formats (`csv`, `excel`, `parquet`, etc.).<br>• Provide at least one of `url`, `sql`, or `table_name` when using a database connection. |
| **InsufficientDataError** | The auto-select path cannot create the requested number of back-tests (k-fold) because each fold must have at least `2 × horizon` observations (`ModelEvaluator.generate_cutoffs`). | • Decrease `num_backtests`.<br>• Provide a longer history for the smallest series.<br>• Switch off auto-select and choose a model explicitly. |
| **UnSupportedModelError** | `spec.model` (or the best candidate from auto-select) is not in the factory’s `_MAP`. | • Choose one of the supported values: `prophet`, `arima`, `neuralprophet`, `automlx`, `autots`, or `auto-select`. |
| **ValueError – AUTOMLX explanation mode** | `explanations_accuracy_mode == AUTOMLX` but the selected model is not AutoMLX. | • Set `explanations_accuracy_mode` to `HIGH_ACCURACY`, `BALANCED` or `FAST_APPROXIMATE`, or force the model to `automlx`. |
| **Exception – “Could not determine datetime type … specify format explicitly”** | Datetime parsing failed because the operator could not infer the format. | • Add `datetime_column.format:` in YAML with an explicit strftime string matching the file. |
| **Generic training / prediction exceptions** | Any framework-specific failure that bubbles up during `_build_model()` (e.g. fitting fails due to constant series, convergence failures, memory errors). The operator catches many of these and either:<br>• Records the message in `errors.json` and continues with the remaining series. | • Inspect `errors.json` inside `output_directory` for the real stack trace. |

---

### Quick Triage Checklist

- Run `ads operator verify -f forecast.yaml` – fixes most schema issues before execution.
- Preview the first few rows of every CSV you reference; check column names.
- Validate your datetime column with `pd.to_datetime(..., format='…')` in a notebook.
- For Forecasting with additional data, make sure every (Date, Series) that exists in historical data is present, and that it also extends at least `horizon` rows into the future.

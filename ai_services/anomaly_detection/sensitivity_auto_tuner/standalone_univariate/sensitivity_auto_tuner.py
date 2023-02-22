import oci
import pandas as pd
import argparse
import numpy as np

from oci.ai_anomaly_detection.models import UnivariateModelTrainingRequestDetails, \
    UnivariateInlineSignalRequestData, UnivariateInlineSignalValueRequestData, \
    InlineUnivariateInferenceWorkflowRequestDetails
import time
from sklearn import metrics
from oci.ai_anomaly_detection import AnomalyDetectionClient


def get_inference_results(label_df: pd.DataFrame,
                          window_size: int,
                          sensitivity: float,
                          ad_client: AnomalyDetectionClient,
                          request: UnivariateInlineSignalRequestData):
    univariate_model_training_request_details = UnivariateModelTrainingRequestDetails(window_size=window_size)
    univariate_iw_request = InlineUnivariateInferenceWorkflowRequestDetails(
        are_all_data_points_required=True,
        training_request_details=univariate_model_training_request_details,
        request_type="INLINE",
        sensitivity=sensitivity,
        signal_data=[request])

    detect_response = ad_client.univariate_inference_workflow_request(univariate_iw_request)

    anomaly_data = detect_response.data.detection_results
    ret = pd.DataFrame(
        columns=["timestamp", "signalname", "anomaly_score", "actual_value", "estimated_value", "is_anomaly"])
    # Adding detected anomaly labels
    i = 0
    signal_name = anomaly_data[0].signal_name
    for anomaly in anomaly_data[0].values:
        row = [str(anomaly.timestamp)[:-6],
               signal_name,
               anomaly.anomaly_score,
               anomaly.actual_value,
               anomaly.estimated_value,
               anomaly.is_anomaly]
        i += 1
        ret.loc[len(ret)] = row

    # Create report

    y_true = label_df.anomaly.iloc[window_size - 1:].reset_index(drop=True).squeeze()
    y_pred = ret['is_anomaly'].astype(int).to_numpy()


    # TPR (TP/(TP+FN)) is >= 80%
    # FPR (FP/(FP+TN)) is <= 15%

    cm = metrics.confusion_matrix(y_true, y_pred)
    tpr = metrics.recall_score(y_true, y_pred)
    fpr = cm[0][1] / (cm[0][1] + cm[0][0])

    row_res = {'TPR': tpr,
               'FPR': fpr,
               'Sensitivity': sensitivity
               }

    print(f"sensitivity:{sensitivity}, TPR:{tpr} , FPR:{fpr}\n")
    return row_res


def tune_sensitivity(results: pd.DataFrame,
                     des_tpr: float,
                     des_fpr: float):
    # Sort by highest TPR
    results = results.sort_values('TPR', ascending=False)
    # DF with the rows that have TPR >= des_tpr
    results = results.loc[(results['TPR'] >= des_tpr)]
    # DF with the rows that have FPR <= des_fpr
    best_fpr = results.loc[(results['FPR'] <= des_fpr)]

    if not results.empty:
        if best_fpr.empty:
            # If there is no row that satisfies FPR <= des_fpr, then we return the lowest possible FPR
            results = results.loc[(results['TPR'] == results['TPR'].iloc[-1])]
            results = results.sort_values('FPR')
        else:
            # If there is an entry that satisfies FPR <= des_fpr , then we apply the function of TPR * (1 - FPR)
            # and sort for the function
            best_fpr['function'] = best_fpr.apply(lambda row: row['TPR'] * (1 - row['FPR']), axis=1)
            results = best_fpr.sort_values('function', ascending=False)
            results = results.head(1)
        print(f"Optimal Sensitivity to use: {results['Sensitivity'].iloc[0]}\n")
        print(f"TPR:{results['TPR'].iloc[0]} , FPR: {results['FPR'].iloc[0]}")
    else:
        print("No values match desired metrics")


def setup(des_tpr: float,
          des_fpr: float,
          label_df: pd.DataFrame,
          ad_client: AnomalyDetectionClient,
          window_size: int):

    # Generate sensitivity samples
    sensitivity_samples = np.arange(0, 1, 0.01)
    # sensitivity_samples = [0.6601652074029946, 0.23891188415967424]

    # Prepare inline request data
    signal_names = 'value'
    value = []
    for index, row in label_df.iterrows():
        requestData = {"timestamp": row['timestamp'], "value": row['value']}
        value.append(UnivariateInlineSignalValueRequestData(**requestData))

    univariate_inline_signal_request_data = UnivariateInlineSignalRequestData(signal_name=signal_names, values=value)
    results = pd.DataFrame(columns=['TPR',
                                    'FPR',
                                    'Sensitivity'])

    # Perform inference for each sensitivity sample
    total_start_time = time.time()
    for sensitivity_sample in sensitivity_samples:
        res = get_inference_results(label_df=label_df,
                                    window_size=window_size,
                                    sensitivity=sensitivity_sample,
                                    ad_client=ad_client,
                                    request=univariate_inline_signal_request_data)
        results = pd.concat([results, pd.DataFrame.from_records([res])], ignore_index=True)

    total_end_time = time.time()
    print(f"Total time taken: {total_end_time - total_start_time}")
    tune_sensitivity(results, des_tpr, des_fpr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sensitivity Auto Tuner')
    parser.add_argument('--des_tpr', type=float, default=0.80)
    parser.add_argument('--des_fpr', type=float, default=0.15)
    parser.add_argument('--dataset_path', type=str, default='~/')
    parser.add_argument('--window_size', type=int, default=10)
    parser.add_argument('--config_path', type=str, default='~/.oci/config')
    args = parser.parse_args()

    # Setting up AnomalyDetectionClient
    config = oci.config.from_file("~/.oci/config")
    ad_client = AnomalyDetectionClient(config)

    # Read input dataset into DataFrame
    label_df = pd.read_csv(args.dataset_path)

    setup(args.des_tpr, args.des_fpr, label_df, ad_client, args.window_size)
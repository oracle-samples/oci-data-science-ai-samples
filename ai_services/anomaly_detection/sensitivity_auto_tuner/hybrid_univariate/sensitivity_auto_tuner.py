import oci
import pandas as pd
import argparse
import numpy as np

from oci.ai_anomaly_detection.models import DataItem, InlineDetectAnomaliesRequest
import time
from sklearn import metrics
from oci.ai_anomaly_detection import AnomalyDetectionClient


def remove_nan(val):
    if val != val:
        return "0"
    elif val == 1:
        return 1

def get_inference_results(label_df: pd.DataFrame,
                          sensitivity: float,
                          ad_client: AnomalyDetectionClient,
                          data: list,
                          model_id: str,
                          signal_names: list) -> dict:
    inline_req = InlineDetectAnomaliesRequest(
        model_id=model_id,
        request_type="INLINE",
        signal_names=signal_names,
        sensitivity=sensitivity,
        data=data)

    window_size = ad_client.get_model(model_id).data.model_training_results.window_size
    detect_response = ad_client.detect_anomalies(detect_anomalies_details=inline_req)
    anomaly_data = detect_response.data.detection_results
    ret = pd.DataFrame(
        columns=["date", "signalname", "anomaly_score", "actual_value", "estimated_value", "is_anomaly"])

    # Adding detected anomaly labels
    i = 0
    for a in anomaly_data:
        for anomaly in a.anomalies:
            row = [str(a.timestamp).replace(" ","T")[:-6],
                   anomaly.signal_name,
                   anomaly.anomaly_score,
                   anomaly.actual_value,
                   anomaly.estimated_value,
                   1]
            i += 1
            ret.loc[len(ret)] = row
    ret = pd.merge(label_df, ret, how="outer")
    ret['is_anomaly'] = ret.apply(lambda row : remove_nan(row['is_anomaly']), axis=1)

    # Create report
    y_true = label_df.anomaly.iloc[window_size - 1:].reset_index(drop=True).squeeze()
    y_pred = ret.is_anomaly.iloc[window_size - 1:].reset_index(drop=True).squeeze().astype(int).to_numpy()

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
                     des_fpr: float) -> float:
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
        return results['Sensitivity'].iloc[0]
    else:
        print("No values match desired metrics, Please use default sensitivity")
        return None


def find_best_sensitivity(des_tpr: float,
                          des_fpr: float,
                          label_df: pd.DataFrame,
                          ad_client: AnomalyDetectionClient,
                          model_id) -> float:
    # Generate sensitivity samples
    sensitivity_samples = np.arange(0.0, 1, 0.01)

    # Prepare inline request data
    signal_names = ['value']
    payloadData = []
    for index, row in label_df.iterrows():
        timestamp = row['date']
        values = list(row[signal_names])
        dItem = DataItem(timestamp=timestamp, values=values)
        payloadData.append(dItem)

    results = pd.DataFrame(columns=['TPR',
                                    'FPR',
                                    'Sensitivity'])

    # Perform inference for each sensitivity sample
    total_start_time = time.time()
    for sensitivity_sample in sensitivity_samples:
        res = get_inference_results(label_df=label_df,
                                    sensitivity=sensitivity_sample,
                                    ad_client=ad_client,
                                    data=payloadData,
                                    model_id=model_id,
                                    signal_names=signal_names)
        results = pd.concat([results, pd.DataFrame.from_records([res])], ignore_index=True)

    total_end_time = time.time()
    print(f"Total time taken: {total_end_time - total_start_time}")
    return tune_sensitivity(results, des_tpr, des_fpr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sensitivity Auto Tuner')
    parser.add_argument('--des_tpr', type=float, default=0.80)
    parser.add_argument('--des_fpr', type=float, default=0.25)
    parser.add_argument('--dataset_path', type=str, default='~/')
    parser.add_argument('--config_path', type=str, default='~/.oci/config')
    parser.add_argument('--model_id', type=str)
    args = parser.parse_args()

    # Setting up AnomalyDetectionClient
    config = oci.config.from_file("~/.oci/config")
    ad_client = AnomalyDetectionClient(config)

    # Read input dataset into DataFrame
    label_df = pd.read_csv(args.dataset_path)

    find_best_sensitivity(args.des_tpr, args.des_fpr, label_df, ad_client, args.model_id)

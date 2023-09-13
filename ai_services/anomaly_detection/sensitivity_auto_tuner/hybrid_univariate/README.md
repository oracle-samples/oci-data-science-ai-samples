## Sensitivity Auto Tuning based on Labeled Data

Anomaly Detection API provides a sensitivity parameter to move the decision boundary based on which we classify whether a timestamp is an anomaly. In other words, it is a parameter to tradeoff between False Positive Rate and True Positive Rate.
Other Anomaly Detection Service features also offer the sensitivity parameter and this solution can be extended to those features as well.


### Problem Statement:

Users of AD service can use the Sensitivity parameter to tune the model performance based on their desired False Positive Rate(FPR) and True Positive Rate(TPR). The default value for the sensitivity parameter is set to 0.5 which will give the user a balanced model. Increasing the sensitivity will make the model more sensitive and predict more anomalies. The Sensitivity parameter gives this control to the user on how they want the model to perform. In some use cases, a higher TPR would be absolutely necessary even if it comes at the cost of a higher FPR. Similarly, some use cases might demand the model to report as fewer False Positives as possible and would be tolerant towards missed alarms.

The complication with this approach is that the user would need to make several calls while varying the sensitivity manually. Users cannot realistically try a large number of values and may not be able to converge to the best possible model performance. To simplify this problem for the users, we have developed a tool that automates this process and calculates the optimal Sensitivity value for a given dataset with respect to the desired success metrics. The users do not need to use this tool if the default model performance is already within their desired success metrics.

Users can use this tool on a labeled dataset and obtain the optimal sensitivity value for that dataset. Then, while making inference calls in production, where the data pattern doesn't vary too much, they can provide this sensitivity value in the inference call request and expect the desired performance.

### Requirements:

The success metrics (TPR and FPR) are calculated by comparing predicted labels against actual labels. Hence, this tool has the following dataset format requirements:

*   **timestamp**: ISO-160 format with monotonically increasing and de-duplicated timestamp
*   **value**: Numerical column 
*   **anomaly**: Values labeled as 0(non-anomalous) / 1(anomalous)

Users can use the open-source [TagAnomaly](https://github.com/microsoft/TagAnomaly) tool to annotate the dataset. We have an instance of this tool hosted at [http://100.73.92.203:3838/](http://100.73.92.203:3838/). Following is an example of a compatible dataset. Users can also edit the script in case they need to use different column names for their specific use case.  Once anomalies are tagged using TagAnomaly tool, users will need to add the anomaly column to the dataset as mentioned above.


### Usage:

1.  Create a python virtual environment
2.  Install the requirements.txt by running ```python
pip install -r requirements.txt```
3.  Clone the notebook in your environment
4.  Run the script and provide the required parameters  
      
```python sensitivity_auto_tuner.py --dataset_path="~/inference.csv" --des_tpr=0.80 --des_fpr=0.15 --window_size=10 --config_path=~/.oci/config```    

The script supports following params:
  
|  Parameter   |  Description   | Default Value |
|-----|-----|---------------|
|  \--dataset\_path|  Path to the labeled dataset  | ~/input.csv            |
| \--des\_tpr    |  Desired True Positive Rate   |        0.80      |
|  \--des\_fpr   |   Desired False Positive Rate  |         0.15     |
| \--window\_size    |   Window size required for making the inference call |     None          |
|  \--config\_path   | Path to the user's OCI config    |          ~/.oci/config     |


### Approach:

* The tool will sample the sensitivity value at a rate of 0.01 within the 0,1 bounds.
    
* 100 inference calls are sent with each sample sensitivity value. Each call calculates the TPR and FPR by comparing the labeled data and the results produced from the inference calls.
    ```python
    for sensitivity_sample in sensitivity_samples:
      res = get_inference_results(label_df=label_df,
                                    sensitivity=sensitivity_sample,
                                    ad_client=ad_client,
                                    data=payloadData,
                                    model_id=model_id,
                                    signal_names=signal_names)
      results=results.append(res, ignore_index=True) ```
        
* This results in the construction of a dataframe that holds a column for TPR, FPR, and Sensitivity values.  
    
* The rows are then sorted based on TPR

    ```python
       results = results.sort_values('TPR', ascending=False)
    ```

* The desired metrics bounds are applied to the results
    ```python 
       results = results.loc[(results['TPR'] >= des_tpr)]
       best_FPR = results.loc[(results['FPR'] <= des_fpr)] 
    ```    
* We first check whether we are able to meet the FPR metric. If we are unable to meet the FPR metric, we will optimize to get the lowest possible FPR that corresponds to a TPR value that meets the TPR metric.  
    If we are able to meet the FPR metric then we find the sensitivity value with the best value for the function "TPR \* (1 - FPR)" . This will give us a TPR that is good enough while also not sacrificing the FPR too much.  
    If we are unable to meet the TPR metric as well, then we exit out.  
```python
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
```

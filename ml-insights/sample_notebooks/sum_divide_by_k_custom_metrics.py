from dataclasses import dataclass
from typing import Dict, Any, Optional, List

import pandas as pd

from mlm_insights.constants.definitions import ConfigParameter
from mlm_insights.constants.types import VariableType, DataType
from mlm_insights.core.metrics.interfaces.metric_base import MetricBase
from mlm_insights.core.metrics import logger
from mlm_insights.core.metrics.metric_result import StandardMetricResult

# Default k value
DEFAULT_K_VALUE: int = 10

# Configuration Keys
CONFIG_K_KEY: str = "k"



@dataclass
class SumDivideByK(MetricBase):
    
    k: int = DEFAULT_K_VALUE
    sum: float = 0.0
        
    @classmethod
    def create(cls, config: Optional[Dict[str, ConfigParameter]] = None) -> "SumDivideByK":
        if config is None:
            config = {}
        
        k = int(config.get(CONFIG_K_KEY, DEFAULT_K_VALUE))

        if k < 1 or k > 100:
            raise InvalidParameterException(parameter=CONFIG_K_KEY, component_name=cls.get_name(),
                message=f"`{CONFIG_K_KEY}` should be > 0 and less than 100")

        logger.debug("Creating SumDivideByK metric with k=" + str(k))
        return  SumDivideByK(k=k)



    @classmethod
    def get_supported_variable_types(cls) -> List[VariableType]:
        """
        Method to retrieve the list of Feature Variable type supported for the metric

        Returns
        -------
        List of Feature Variable type supported by the Sum metric
        """
        return [VariableType.CONTINUOUS, VariableType.DISCRETE]

    def compute(self, column: pd.Series, **kwargs: Any) -> None:
        """
        Computes the SumDivideByK for the passed in dataset. In case of a partitioned dataset, computes the SumDivideByK for the specific partition

        Parameters
        ----------
        column : pd.Series
            Input column.
        """
        logger.debug("Evaluating SumDivideByTwo for SumDivideByTwo metric")
        k = self.k
        self.sum = column.sum(skipna=True)/k

    def merge(self, other_metric: "SumDivideByK", **kwargs: Any) -> "SumDivideByK":  # type: ignore[override]
        """
        Merge two SumDivideByK metrics into one, without mutating the others.

        Parameters
        ----------
        other_metric : SumDivideByK
            Other SumDivideByK metric that need be merged.

        Returns
        -------
        SumDivideByK
            A new instance of SumDivideByK metric after merging.
        """
        logger.debug("Merging two SumDivideByK metrics into one.")
        k_after_merge = self.k
        new_state = self.sum + other_metric.sum
        return Sum(sum=new_state,k=k_after_merge)

    def get_result(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Returns SumDivideByK of input data.

        Returns
        -------
        float: SumDivideByK of the data.
        """
        logger.debug("Getting result for SumDivideByK metric")
        logger.info("Calculated SumDivideByK metric, value: " + str(self.sum))
        return {"value": self.sum}

    def get_standard_metric_result(self, **kwargs: Any) -> StandardMetricResult:
        """
        Returns Standard Metric for SumDivideByK.

        Returns
        -------
        StandardMetricResult: SumDivideByK Metric in standard format.
        """
        return StandardMetricResult(
            metric_name=self.get_name(),
            metric_description="",
            variable_count=1,
            variable_names=["sumdividebyK"],
            variable_types=[VariableType.CONTINUOUS],
            variable_dtypes=[DataType.FLOAT],
            variable_dimensions=[0],
            metric_data=[self.sum])

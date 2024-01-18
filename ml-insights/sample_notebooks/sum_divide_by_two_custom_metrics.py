from dataclasses import dataclass
from typing import Dict, Any, Optional, List

import pandas as pd

from mlm_insights.constants.definitions import ConfigParameter
from mlm_insights.constants.types import VariableType, DataType
from mlm_insights.core.metrics.interfaces.metric_base import MetricBase
from mlm_insights.core.metrics import logger
from mlm_insights.core.metrics.metric_result import StandardMetricResult


@dataclass
class SumDivideByTwo(MetricBase):
    @classmethod
    def create(cls, config: Optional[Dict[str, ConfigParameter]] = None) -> "SumDivideByTwo":
        logger.debug("Creating SumDivideByTwo metric")
        return  SumDivideByTwo()

    sum: float = 0.0

    @classmethod
    def get_supported_variable_types(cls) -> List[VariableType]:
        """
        Method to retrieve the list of Feature Variable type supported for the metric

        Returns
        -------
        List of Feature Variable type supported by the SumDivideByTwo metric
        """
        return [VariableType.CONTINUOUS, VariableType.DISCRETE]

    def compute(self, column: pd.Series, **kwargs: Any) -> None:
        """
        Computes the SumDivideByTwo for the passed in dataset. In case of a partitioned dataset, computes the sum for the specific partition

        Parameters
        ----------
        column : pd.Series
            Input column.
        """
        logger.debug("Evaluating SumDivideByTwo for SumDivideByTwo metric")
        self.sum = column.sum(skipna=True)/2

    def merge(self, other_metric: "SumDivideByTwo", **kwargs: Any) -> "SumDivideByTwo":  # type: ignore[override]
        """
        Merge two SumDivideByTwo metrics into one, without mutating the others.

        Parameters
        ----------
        other_metric : SumDivideByTwo
            Other SumDivideByTwo metric that need be merged.

        Returns
        -------
        SumDivideByTwo
            A new instance of SumDivideByTwo metric after merging.
        """
        logger.debug("Merging two SumDivideByTwo metrics into one.")
        new_state = self.sum + other_metric.sum
        return SumDivideByTwo(new_state)

    def get_result(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Returns SumDivideByTwo of input data.

        Returns
        -------
        float: SumDivideByTwo of the data.
        """
        logger.debug("Getting result for SumDivideByTwo metric")
        logger.info("Calculated SumDivideByTwo metric, value: " + str(self.sum))
        return {"value": self.sum}

    def get_standard_metric_result(self, **kwargs: Any) -> StandardMetricResult:
        """
        Returns Standard Metric for SumDivideByTwo.

        Returns
        -------
        StandardMetricResult: SumDivideByTwo Metric in standard format.
        """
        return StandardMetricResult(
            metric_name=self.get_name(),
            metric_description="",
            variable_count=1,
            variable_names=["sumdividebytwo"],
            variable_types=[VariableType.CONTINUOUS],
            variable_dtypes=[DataType.FLOAT],
            variable_dimensions=[0],
            metric_data=[self.sum])

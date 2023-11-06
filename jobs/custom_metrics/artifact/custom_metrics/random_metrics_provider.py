from custom_metrics_provider import Metric, CustomMetricsProvider
import random


class RandomMetricsProvider(CustomMetricsProvider):
    """
    Random metrics provider
    """

    def get_metrics(self) -> list:
        """
        Get a metric with a random value

        Returns
        -------
        list
            List of Metric objects.
        """
        metric = Metric("random", random.randint(0, 100))
        return [metric]

class Metric:
    """
    Class containing metric details
    """

    def __init__(self, name: str, value: float, dimensions: dict = None):
        """
        Initializes a Metrics object

        Parameters
        ----------
        name: str
            The metric name
        value: float
            The metric value
        dimensions: dict
            Dictionary of dimensions to include on the metric.
        """
        self.name = name
        self.value = value
        self.dimensions = dimensions if dimensions else {}


class CustomMetricsProvider:
    """
    Base class for a custom metric provider.
    """

    def get_metrics(self) -> list:
        """
        Get the custom metrics.

        Returns
        -------
        list
            List of Metric objects.
        """
        return []

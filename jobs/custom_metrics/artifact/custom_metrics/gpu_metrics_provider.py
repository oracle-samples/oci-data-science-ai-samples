from custom_metrics_provider import Metric, CustomMetricsProvider
import subprocess


class GpuMetricsProvider(CustomMetricsProvider):
    """
    Custom GPU utilization metrics provider
    """

    def get_metrics(self) -> list:
        """
        Get custom GPU metrics

        Returns
        -------
        list
            List of Metric objects.
        """
        gpu_metrics = []
        try:
            # Example output:
            # 00000000:00:04.0, 42.27, 40, 20, 16384, 15287
            # 00000000:00:05.0, 41.30, 42, 0, 16384, 479
            nvidia_smi_output = subprocess.check_output([
                "nvidia-smi",
                "--query-gpu=pci.bus_id,power.draw,temperature.gpu,utilization.gpu,memory.total,memory.used",
                "--format=csv,noheader,nounits"
            ]).decode("utf-8")

            for line in nvidia_smi_output.split("\n"):
                if len(line) > 0:
                    values = line.split(", ")
                    if len(values) >= 6:
                        dimensions = {"pci_bus": values[0]}
                        gpu_metrics.append(Metric("gpu.power_draw", float(values[1]), dimensions))
                        gpu_metrics.append(Metric("gpu.temperature", float(values[2]), dimensions))
                        gpu_metrics.append(Metric("gpu.gpu_utilization", float(values[3]), dimensions))
                        gpu_metrics.append(
                            Metric("gpu.memory_usage", round(float(values[5]) / float(values[4]) * 100, 2), dimensions)
                        )
                    else:
                        print(f"Unexpected nvidia-smi output format. Composing no metrics for output line: {line}")
        except Exception as e:
            print(f"Unexpected error encountered querying GPU: {e}")

        return gpu_metrics

# AQUA Deployment Metrics Mornitoring
This guide outlines how to set up an end-to-end monitoring solution for a model deployed on AQUA, using a custom stack (Authentication Proxy, Prometheus, Grafana) deployed on an OCI Container Instance.

The process involves four main steps:
- Instrumenting AQUA Model Deployment to expose metrics.
- Deploying the Authentication Proxy, Prometheus, and Grafana images in OCI Container Registry.
- Setting up the OCI Container Instance to host the monitoring stack.
- Visualizing Metrics in Grafana.

## Step 1: Instrument AQUA Model Deployment and Expose Metrics

AQUA model deployment inference container is using **vLLM** which publishes [Prometheus-compatible metrics](https://docs.vllm.ai/en/latest/design/metrics/) such as `Time to first token(TTFT)`, `Inter-token latency(ITL)`, tokens/sec, etc, to `/metrics` endpoint.

The [AQUA Model Deployment]((https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/model-deployment-tips.md)) is accessible via an HTTPS endpoint. Ensure proper [OCI IAM](https://docs.oracle.com/en-us/iaas/Content/data-science/using/model-dep-policies-auth.htm) policies are in place to control access. The workflow calls for an authentication proxy, so access (`resource_principal`) will be secured at that layer.

## Step 2: Deploying the Authentication Proxy, Prometheus, and Grafana images in OCI Container Registry.
You will use Docker images for the proxy, Prometheus, and Grafana. Download the repo `oci-data-science-ai-samples` and navigate to `oci-data-science-ai-samples/ai-quick-actions/aqua_metrics` folder.

```bash
git clone https://github.com/oracle-samples/oci-data-science-ai-samples.git
cd oci-data-science-ai-samples/ai-quick-actions/aqua_metrics
```

### 2.1. Authentication Proxy
You need an authentication proxy to control access to your model's metrics endpoint. 

Navigate to the `signing_proxy` folder, build and push the `signing_proxy` image to OCI Container Registry. The `signing_proxy` defaults to port `8080`. You will need to specify the target AQUA deployment `/metrics` endpoint via environment variables later in OCI Container Instance.

```bash
docker build --no-cache -t signing_proxy .
docker tag signing_proxy <registry-domain>/<tenancy-namespace>/signing_proxy
docker push <registry-domain>/<tenancy-namespace>/signing_proxy:latest
```

- **Note**
  - Replace the `<registry-domain>` and `<tenancy-namespace>` with your own values. For more information, see [Pushing Images Using the Docker CLI](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm)

### 2.2. Prometheus
Prometheus will scrape metrics from the proxy. In this example, we will have a configuration file `prometheus.yml` to define the scrape job and point to your authentication proxy's address `localhost:8080`.

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 30s

scrape_configs:
  - job_name: AQUA
    static_configs:
      - targets:
          - 'localhost:8080'
```

The configuration file will be added into the Prometheus container `Dockerfile`.

```
# Dockerfile
FROM prom/prometheus

ADD /prometheus.yml /etc/prometheus/prometheus.yml
```

Navigate to the `prometheus` folder, build and push the Prometheus image to OCI Container Registry. The `prometheus` defaults to port `9090`.

```bash
docker build --no-cache -t prometheus .
docker tag prometheus <registry-domain>/<tenancy-namespace>/prom/prometheus
docker push <registry-domain>/<tenancy-namespace>/prom/prometheus:latest
```

- **Note**
  - Replace the `<registry-domain>` and `<tenancy-namespace>` with your own values. For more information, see [Pushing Images Using the Docker CLI](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm)

## 2.3. Grafana
Grafana will visualize the metrics collected by Prometheus.

Navigate to the `grafana` folder, build and push the Grafana image to OCI Container Registry. The `grafana` service defaults to port `3000` (you will need to set this up via environment variables later in OCI Container Instance).

- **Note**: Instead of pushing it yourself, you can also pull `Grafana` image directly from `docker.io` on OCI Container Instance.

```bash
docker build --no-cache -t grafana .
docker tag grafana <registry-domain>/<tenancy-namespace>/grafana/grafana
docker push <registry-domain>/<tenancy-namespace>/grafana/grafana:latest
```

- **Note**
  - Replace the `<registry-domain>` and `<tenancy-namespace>` with your own values. For more information, see [Pushing Images Using the Docker CLI](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm)

## Step 3: Set Up the OCI Container Instance

You will host your monitoring images above on an OCI Container Instance.

- **Create a VCN and Subnet**: Ensure you have a Virtual Cloud Network (VCN) with a public or private regional subnet configured with appropriate security rules. The security rules must allow ingress traffic on the ports you plan to use for the proxy (8080), Prometheus (9090), and Grafana (3000), and allow egress traffic to the model deployment endpoint. For more information, see [Network](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/landing.htm).

- **Create the Container Instance**:
  - Navigate to **Developer Services** -> **Containers & Artifacts** -> **Container Instances** in the OCI Console.

  - Click **Create container instance**.
  - Select a **compartment**, **availability domain**, and an appropriate flexible **shape**.
  - Select your **VCN** and **subnet**. If you want a public IP, ensure the subnet is public and you check **Assign a public IPv4 address**.
  - In the **Configure containers**, you will define the individual containers (Proxy, Prometheus, Grafana) from OCI Container Registry that are built in the previous steps within the same instance.
    - **Note**: 
      - Set `TARGET` as the AQUA deployment `/metrics` endpoint that's monitored in `Environmental variables` for `signing_proxy` image. The endpoint format should be `<model-deployment-url>/predict/metrics`.
      - Set `PORT` as `3000` in `Environmental variables` for `grafana` image.
  - Click `Create`.

## Step 4: Visualize Metrics in Grafana

- **Access Grafana**: Once the container instance is active, access the Grafana UI using the public IP address of your Container Instance and the Grafana port: `http://<oci-container-instance-public-ip>:3000`.

- **Log In**: Log in with your credentials (default is `admin/admin` if not changed via environment variables).

- **Add Prometheus Data Source**:

  - Go to `Configuration` -> `Data Sources`.
  - Click `Add data source` and select `Prometheus`.
  - Set the URL to the internal Prometheus service address: `http://localhost:9090`.
  - Click `Save & Test`. You should see `"Data source is working"`.

- **Create Dashboards**: Use the Prometheus query language (PromQL) to build dashboards and panels that display your model's metrics. For more information, see [build grafana dashboard](https://grafana.com/docs/grafana/latest/getting-started/build-first-dashboard/).

By following these steps, you will have a self-contained, monitored system for your OCI Data Science model.

![grafana-dashboard-example](../web_assets/grafana-dashboard-example.png)
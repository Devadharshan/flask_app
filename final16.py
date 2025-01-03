import time
import psutil
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Set up OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Metrics Exporter and Provider
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter
meter = metrics.get_meter_provider().get_meter("sybase_app")

# CPU usage callback function (returns the metric value)
def get_cpu_usage():
    """Fetch CPU usage percentage of the current process."""
    return psutil.Process().cpu_percent(interval=None)

# Memory usage callback function (returns the metric value)
def get_memory_usage():
    """Fetch memory usage of the current process in bytes (RSS)."""
    return psutil.Process().memory_info().rss

# Create a Counter for CPU usage (used as gauge)
cpu_usage_metric = meter.create_up_down_counter(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="%",
)

# Create a Counter for Memory usage (used as gauge)
memory_usage_metric = meter.create_up_down_counter(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes",
    unit="bytes",
)

# Function to record metrics
def record_metrics():
    """Record metrics by fetching current CPU and Memory usage."""
    cpu_usage_metric.add(get_cpu_usage())  # Record CPU usage
    memory_usage_metric.add(get_memory_usage())  # Record memory usage

# Keep the application running
print("Metrics collection running. Sending to OTLP endpoint...")
while True:
    record_metrics()  # Record the metrics
    time.sleep(10)  # Wait for the next collection cycle
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

# Callback for CPU usage
def get_cpu_usage():
    """Fetch CPU usage percentage of the current process."""
    return [(psutil.Process().cpu_percent(interval=None), {})]

# Callback for Memory usage
def get_memory_usage():
    """Fetch memory usage of the current process in bytes (RSS)."""
    return [(psutil.Process().memory_info().rss, {})]

# ObservableGauges for process-level metrics
meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="%",
    callbacks=[get_cpu_usage],  # No arguments passed to this function
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes",
    unit="bytes",
    callbacks=[get_memory_usage],  # No arguments passed to this function
)

# Keep the application running
print("Metrics collection running. Sending to OTLP endpoint...")
while True:
    time.sleep(10)
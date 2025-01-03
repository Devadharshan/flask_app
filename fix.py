import time
import psutil
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup OpenTelemetry resources and metric provider
resource = Resource.create(attributes={"service.name": "sybase_app"})
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter
meter = metrics.get_meter_provider().get_meter("sybase_app")

# Define the callback functions
def get_cpu_usage(_):
    """Get CPU usage percentage."""
    return [
        (psutil.Process().cpu_percent(interval=None), {}),
    ]

def get_memory_usage(_):
    """Get memory usage in bytes."""
    return [
        (psutil.Process().memory_info().rss, {}),
    ]

# Create Observable Metrics
meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="percent",
    callbacks=[get_cpu_usage],
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS)",
    unit="bytes",
    callbacks=[get_memory_usage],
)

# Simulate workload
print("Metrics are being collected...")
while True:
    time.sleep(10)

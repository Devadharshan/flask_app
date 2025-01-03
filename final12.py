import time
import psutil
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# OpenTelemetry setup
resource = Resource.create(attributes={"service.name": "sybase_app"})
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Meter setup
meter = metrics.get_meter_provider().get_meter("sybase_app")

# Functions to fetch CPU and memory usage
def get_cpu_usage():
    """Fetch CPU usage percentage of the current process."""
    return psutil.Process().cpu_percent(interval=None)

def get_memory_usage():
    """Fetch memory usage of the current process in bytes (RSS)."""
    return psutil.Process().memory_info().rss

# Callback functions
def cpu_usage_callback(observer):
    """Callback for CPU usage."""
    observer.observe(get_cpu_usage(), {})

def memory_usage_callback(observer):
    """Callback for memory usage."""
    observer.observe(get_memory_usage(), {})

# Create ObservableGauges
meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[cpu_usage_callback],
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS)",
    callbacks=[memory_usage_callback],
)

# Keep the application running
print("Metrics collection running. Sending to OTLP endpoint...")
while True:
    time.sleep(10)  # Keep the script alive
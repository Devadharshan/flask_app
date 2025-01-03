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

# Meter for custom metrics
meter = metrics.get_meter_provider().get_meter("sybase_app")

# Helper function to wrap callbacks
def safe_callback(callback):
    """Wrap the callback to ensure it handles unexpected arguments."""
    def wrapper(*args, **kwargs):
        return callback()
    return wrapper

# Callback functions for metrics
def collect_cpu_usage():
    """Return CPU usage percentage of the current process."""
    value = psutil.Process().cpu_percent(interval=None)
    return [(value, {})]  # Return a list of tuples with value and attributes

def collect_memory_usage():
    """Return memory usage of the current process in bytes (RSS)."""
    value = psutil.Process().memory_info().rss
    return [(value, {})]  # Return a list of tuples with value and attributes

# Define ObservableGauges with wrapped callbacks
meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[safe_callback(collect_cpu_usage)],
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[safe_callback(collect_memory_usage)],
)

# Run application
print("Metrics collection running. Sending to OTLP endpoint...")
while True:
    pass  # Keep the script running to collect metrics
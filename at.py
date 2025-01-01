import time
import psutil
from prometheus_client import Gauge
from opentelemetry import trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter

# Initialize OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Initialize OpenTelemetry Metrics
meter_provider = MeterProvider()
meter = meter_provider.get_meter(__name__)

# Set up OTLP exporters for sending data to OpenTelemetry Collector
otlp_metric_exporter = OTLPMetricExporter(endpoint="localhost:4317", insecure=True)
otlp_span_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)

# Set up OpenTelemetry to export spans (traces) and metrics
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(otlp_span_exporter)
)

# Set up system-level metrics collection using psutil
cpu_usage_gauge = meter.create_gauge(
    "process_cpu_usage", description="Process CPU usage in percentage"
)
memory_usage_gauge = meter.create_gauge(
    "process_memory_usage", description="Process memory usage in bytes"
)

def track_process_metrics():
    """Track and export CPU and memory usage using psutil."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().used

    # Export metrics to OpenTelemetry Collector
    cpu_usage_gauge.add(cpu_usage)
    memory_usage_gauge.add(memory_usage)

    print(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage} bytes")

def main():
    """Main execution loop."""
    with tracer.start_as_current_span("main-operation"):
        for i in range(10):
            track_process_metrics()  # Track system metrics (CPU and memory)
            time.sleep(1)  # Simulate work by sleeping for 1 second

if __name__ == "__main__":
    main()

import time
from opentelemetry import trace, metrics
from opentelemetry.trace import TracerProvider
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import OTLPMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import sampling
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.exporter.otlp.proto.grpc._logs_exporter import OTLPLogExporter
import logging

# Configure Resource
resource = Resource.create(
    attributes={
        "service.name": "test_python_app",  # Service name
        "service.version": "1.0.0",
    }
)

# Configure Logger
log_exporter = OTLPLogExporter(endpoint="your-otel-collector-endpoint:4317", insecure=True)
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(logging.getLogger())
log_handler = LoggingHandler(logger_provider)
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
log = logging.getLogger("test_python_app")

# Configure Tracer
trace_provider = TracerProvider(
    resource=resource,
    sampler=sampling.ALWAYS_ON,  # Ensures every trace is sampled
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("test_python_app")

# Add Span Processor
span_exporter = OTLPSpanExporter(endpoint="your-otel-collector-endpoint:4317", insecure=True)
span_processor = BatchSpanProcessor(span_exporter)
trace_provider.add_span_processor(span_processor)

# Configure Metrics
metric_exporter = OTLPMetricExporter(endpoint="your-otel-collector-endpoint:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("test_python_app")

# Define Metrics
query_duration_histogram = meter.create_histogram(
    name="app_db_query_duration",
    unit="seconds",
    description="Duration of database queries",
)

# Example Traced Function
def example_function():
    with tracer.start_as_current_span(
        "example_function_execution",
        kind=SpanKind.INTERNAL,
        attributes={"example.attribute": "value"},
    ):
        log.info("Executing example function")
        time.sleep(2)  # Simulate work
        log.info("Example function completed")


# Main Application Logic
def main():
    while True:
        log.info("Application started")
        example_function()
        query_duration_histogram.record(1.5)  # Simulated query duration
        time.sleep(10)


if __name__ == "__main__":
    main()

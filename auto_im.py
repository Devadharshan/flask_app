from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from lib.tracer import tracer_init
from lib.logger import log
import sybpydb
import time
import psutil

# Configure the OTLP endpoint
OTLP_ENDPOINT = "http://<collector_address>:5608"

# Initialize Tracer Provider
resource = Resource.create({"service.name": "test_python_app"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP Trace Exporter
span_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)

# Initialize Meter Provider
meter_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
metric_reader = PeriodicExportingMetricReader(meter_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Initialize Tracer
tracer = tracer_init()

# Initialize Meter
meter = metrics.get_meter("test_python_app")

# Metrics
query_duration = meter.create_histogram(
    name="app_db_query_duration",
    description="Time taken to execute a database query",
    unit="seconds",
)
app_up_down = meter.create_observable_gauge(
    name="app_status",
    description="Whether the application is up (1) or down (0)",
    unit="",
    callbacks=[lambda options: 1],  # Always up for this example
)

# Example Sybase Query with Custom Span and Metrics
def query_sybase():
    with tracer.start_as_current_span("sybase-query", attributes={"db.system": "sybase"}):
        try:
            start_time = time.time()

            # Establish connection
            connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
            log.info("Connected to Sybase database.")

            # Execute a query
            query = "SELECT COUNT(*) FROM your_table_name"  # Replace with your actual query
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            log.info(f"Query result: {result[0]}")

            # Record query duration
            duration = time.time() - start_time
            query_duration.record(duration, {"db.system": "sybase"})
            log.info(f"Query executed in {duration:.2f} seconds")

            cursor.close()
            connection.close()

        except Exception as e:
            log.error(f"Failed to execute query: {e}")

# Main Application Logic
def main():
    while True:
        try:
            log.info("Starting Sybase query...")
            query_sybase()
            log.info("Completed Sybase query.")
        except Exception as e:
            log.error(f"An error occurred: {e}")
        time.sleep(10)

if __name__ == "__main__":
    log.info("Starting Python application with OpenTelemetry instrumentation")
    main()


________
from opentelemetry import trace
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import sybpydb
import time
import psutil
from lib.tracer import tracer_init
from lib.logger import log

# Initialize Tracer
resource = Resource.create({"service.name": "test_python_app"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP Exporter
span_exporter = OTLPSpanExporter(endpoint="http://<collector_address>:5608", insecure=True)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)

# Get the tracer
tracer = tracer_init()

# Example Sybase Query with Auto-Instrumentation
def query_sybase():
    with tracer.start_as_current_span("sybase-query", attributes={"db.system": "sybase"}):
        try:
            start_time = time.time()

            # Establish connection
            connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
            log.info("Connected to Sybase database.")

            # Execute a query
            query = "SELECT COUNT(*) FROM your_table_name"  # Replace with your actual query
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            log.info(f"Query result: {result[0]}")

            # Record duration (can be captured automatically if supported)
            duration = time.time() - start_time
            log.info(f"Query executed in {duration:.2f} seconds")

            cursor.close()
            connection.close()

        except Exception as e:
            log.error(f"Failed to execute query: {e}")

# Main Application Logic
def main():
    while True:
        try:
            log.info("Starting Sybase query...")
            query_sybase()
            log.info("Completed Sybase query.")
        except Exception as e:
            log.error(f"An error occurred: {e}")
        time.sleep(10)

if __name__ == "__main__":
    log.info("Starting Python application with OpenTelemetry auto-instrumentation")
    main()

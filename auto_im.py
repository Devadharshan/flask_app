
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
import psutil  # For system metrics like CPU and memory usage

# Define OTLP endpoint
OTLP_ENDPOINT = "http://<collector_address>:5608"

# Create resource for identifying the service
resource = Resource.create({"service.name": "test_python_app"})

# Initialize Metric Exporter and Provider
metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

# Set the MeterProvider globally
metrics.set_meter_provider(meter_provider)

# Create a meter for custom metrics
meter = metrics.get_meter("test_python_app", version="1.0.0")

# Metric: Database query duration
db_query_duration = meter.create_histogram(
    name="app_db_query_duration",
    description="Database query duration",
    unit="ms",
)

# Metric: CPU usage
cpu_usage_gauge = meter.create_observable_gauge(
    name="app_cpu_usage",
    description="Current CPU usage percentage",
    unit="%",
    callbacks=[lambda: [psutil.cpu_percent(interval=None)]],  # Correct callback
)

# Metric: Memory usage
memory_usage_gauge = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Current memory usage percentage",
    unit="%",
    callbacks=[lambda: [psutil.virtual_memory().percent]],  # Correct callback
)

# Metric: Application status (up/down)
def app_status_callback():
    # 1 for up, 0 for down
    return [1]

app_status_gauge = meter.create_observable_gauge(
    name="app_status",
    description="Application status (1 for up, 0 for down)",
    unit="",
    callbacks=[app_status_callback],
)

# Simulated function to measure query duration (example)
import time
def execute_query():
    start_time = time.time()
    time.sleep(0.2)  # Simulate a query delay
    duration = (time.time() - start_time) * 1000  # Duration in milliseconds
    db_query_duration.record(duration)

# Simulate queries
if __name__ == "__main__":
    while True:
        execute_query()
        time.sleep(5)  # Interval between metrics collection


----\\\\pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-exporter-otlp-proto-grpc opentelemetry-instrumentation


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

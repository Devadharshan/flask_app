import time
import os
import sybpydb
import psutil  # For CPU and memory metrics
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Set up OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer("sybase_app")

# Metrics Provider
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("sybase_app")

# Metrics Definitions
query_execution_time = meter.create_histogram(
    "sybase_query_execution_time",
    description="Time taken to execute queries in milliseconds",
)
query_count = meter.create_counter(
    "sybase_query_count", description="Total number of queries executed"
)

# Function for ObservableGauge Metrics
def get_cpu_usage(observer):
    observer.observe(psutil.cpu_percent(), {})

def get_memory_usage(observer):
    memory_in_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    observer.observe(memory_in_mb, {})

# Register Observable Gauges
meter.create_observable_gauge(
    "process_cpu_usage",
    callbacks=[get_cpu_usage],
    description="CPU usage percentage of the process",
)
meter.create_observable_gauge(
    "process_memory_usage",
    callbacks=[get_memory_usage],
    description="Memory usage of the process in MB",
)

def connect_to_sybase(server, user, password, database):
    """
    Connect to Sybase database.
    """
    with tracer.start_as_current_span("sybase_connect"):
        try:
            conn = sybpydb.connect(server=server, user=user, password=password, database=database)
            print("Successfully connected to Sybase.")
            return conn
        except Exception as e:
            print(f"Failed to connect to Sybase: {e}")
            raise


def execute_query(connection, query):
    """
    Execute a query on the Sybase database.
    """
    with tracer.start_as_current_span("sybase_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            query_count.add(1)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            query_execution_time.record(execution_time, {"query": query})
            span.set_attribute("execution_time_ms", execution_time)


def main():
    # Configuration
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    # Connect to Sybase
    try:
        connection = connect_to_sybase(server, user, password, database)
    except Exception as e:
        print(f"Error during connection: {e}")
        return

    # Queries to execute
    queries = [
        "SELECT COUNT(*) FROM your_table",  # Replace with your actual query
        "SELECT TOP 10 * FROM your_table",  # Replace with your actual query
    ]

    # Execute queries
    for query in queries:
        try:
            results = execute_query(connection, query)
            print(f"Results for query '{query}': {results}")
        except Exception as e:
            print(f"Error executing query '{query}': {e}")

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
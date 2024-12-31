import os
import time
import resource  # For memory usage
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter

# Import custom logger and tracer from your `lib` folder
from lib.logger import Logger
from lib.tracer import Tracer

# Configuration
SYBASE_SERVER = "your_server_name"
SYBASE_DATABASE = "your_database_name"
SYBASE_CONNECTION_STRING = f"server name={SYBASE_SERVER};database={SYBASE_DATABASE};chainxacts=0"
OTEL_COLLECTOR_ENDPOINT = "http://your-otel-collector-endpoint:4317"

# OpenTelemetry setup
def setup_otel():
    # Trace setup
    tracer_provider = TracerProvider()
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
    )
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Metrics setup
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
            )
        ]
    )
    metrics.set_meter_provider(meter_provider)

# Function to fetch CPU and memory usage
def collect_system_metrics():
    pid = os.getpid()  # Current process ID
    # CPU usage (user + system time)
    cpu_usage = os.times().user + os.times().system
    # Memory usage in MB
    memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    return cpu_usage, memory_usage

# Function to fetch data from the Sybase database
def fetch_data():
    try:
        Logger.log_info("Connecting to Sybase database...")
        connection = sybpydb.connect(SYBASE_CONNECTION_STRING)
        cursor = connection.cursor()
        query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your actual query

        start_time = time.time()
        cursor.execute(query)
        rows = cursor.fetchall()
        query_duration = time.time() - start_time

        Logger.log_info(f"Query executed successfully in {query_duration:.2f} seconds.")
        Logger.log_info(f"Fetched {len(rows)} rows from the database.")
        return rows, query_duration
    except Exception as e:
        Logger.log_error(f"Error during database query: {e}")
        raise

# Main function
def main():
    setup_otel()

    tracer = Tracer.get_tracer("custom_tracer")  # Use your custom tracer implementation
    meter = metrics.get_meter("custom_meter")

    # Define custom metrics
    db_query_duration_metric = meter.create_histogram(
        name="db_query_duration_seconds",
        description="Histogram of database query durations",
        unit="seconds"
    )
    cpu_usage_metric = meter.create_observable_gauge(
        name="app_cpu_usage_seconds",
        description="CPU usage of the application in seconds",
        unit="seconds",
        callback=lambda: [(cpu_usage_metric, collect_system_metrics()[0])]
    )
    memory_usage_metric = meter.create_observable_gauge(
        name="app_memory_usage_megabytes",
        description="Memory usage of the application in MB",
        unit="MB",
        callback=lambda: [(memory_usage_metric, collect_system_metrics()[1])]
    )

    # Tracing and fetching data
    with tracer.start_as_current_span("database_query"):
        rows, query_duration = fetch_data()

        # Record the query duration as a metric
        db_query_duration_metric.record(query_duration)

    Logger.log_info("Application execution completed successfully.")

if __name__ == "__main__":
    main()

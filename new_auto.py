\import time
import sybpydb
from lib.logger import get_logger
from lib.traces import tracer_init
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# OpenTelemetry Collector endpoint
OTEL_COLLECTOR_ENDPOINT = "http://<your-collector-endpoint>:5608"

# Initialize Logger
log = get_logger("SybaseAppLogger")

# Initialize Tracer
tracer = tracer_init("SybaseApp", OTEL_COLLECTOR_ENDPOINT)

# Configure MeterProvider for Metrics
resource = Resource.create({"service.name": "SybaseApp"})
metric_exporter = OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("SybaseAppMetrics")

# Define metrics
app_status_counter = meter.create_counter(
    "app_up_status",
    description="Counter to track app status (increments by 1 if app is running)",
)

query_duration_histogram = meter.create_histogram(
    "app_db_query_duration",
    description="Time taken to execute database query",
)

cpu_usage_counter = meter.create_counter(
    "app_cpu_usage_total",
    description="Tracks cumulative CPU usage over time",
)

memory_usage_counter = meter.create_counter(
    "app_memory_usage_total",
    description="Tracks cumulative memory usage in MB over time",
)

# Database configuration
DB_CONFIG = {
    "server": "your_sybase_server",
    "database": "your_database",
}

# Query to execute
QUERY = "SELECT COUNT(*) FROM your_table"


def connect_and_query():
    """
    Connects to the Sybase database, executes a query, and traces its execution.
    """
    log.info("Starting database connection and query execution.")

    try:
        # Use File System Native Authentication (no username/password)
        connection = sybpydb.connect(**DB_CONFIG)
        cursor = connection.cursor()

        with tracer.start_as_current_span(
            "db_query_execution",
            attributes={
                "db.system": "sybase",
                "db.name": DB_CONFIG["database"],
                "db.statement": QUERY,
            },
        ) as span:
            # Measure query duration
            start_time = time.time()
            cursor.execute(QUERY)
            result = cursor.fetchone()
            duration = time.time() - start_time

            # Log and record metrics
            log.info(f"Query executed successfully. Result: {result[0]}")
            span.set_attribute("db.query.result_count", result[0])
            query_duration_histogram.record(duration)

            log.info(f"Query duration: {duration:.2f} seconds")
            span.set_attribute("db.query.duration", duration)

        cursor.close()
        connection.close()
        log.info("Database connection closed.")

    except Exception as e:
        log.error(f"Database error: {e}")


def simulate_system_metrics():
    """
    Simulates CPU and memory usage metrics for the app.
    """
    try:
        # Simulated CPU and memory usage values (replace with actual collection logic)
        cpu_usage = 5.0  # Example CPU usage in %
        memory_usage = 256  # Example memory usage in MB

        # Log metrics
        log.info(f"CPU Usage: {cpu_usage}%")
        log.info(f"Memory Usage: {memory_usage}MB")

        # Record metrics
        cpu_usage_counter.add(cpu_usage)
        memory_usage_counter.add(memory_usage)

    except Exception as e:
        log.error(f"Error collecting system metrics: {e}")


if __name__ == "__main__":
    log.info("Starting the application.")
    try:
        while True:
            # Increment app status counter to show the app is up
            app_status_counter.add(1)

            # Simulate system metrics
            simulate_system_metrics()

            # Execute database query
            connect_and_query()

            # Wait for the next execution
            time.sleep(10)  # Adjust the interval as needed
    except KeyboardInterrupt:
        log.info("Application terminated.")

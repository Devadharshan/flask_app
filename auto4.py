import time
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
def app_up_status_callback():
    """
    Callback for app_up_status metric.
    Returns an iterable of observations (value + attributes).
    """
    return [(1, {})]  # App is running

def collect_memory_usage():
    """
    Callback for memory usage metric.
    Returns an iterable of observations.
    """
    try:
        # Replace with actual memory usage collection logic
        memory_usage = 512  # Example value in MB
        return [(memory_usage, {})]
    except Exception as e:
        log.error(f"Failed to collect memory usage: {e}")
        return [(0, {})]  # Default value if an error occurs

def collect_cpu_usage():
    """
    Callback for CPU usage metric.
    Returns an iterable of observations.
    """
    try:
        # Replace with actual CPU usage collection logic
        cpu_usage = 10.5  # Example percentage
        return [(cpu_usage, {})]
    except Exception as e:
        log.error(f"Failed to collect CPU usage: {e}")
        return [(0.0, {})]  # Default value if an error occurs


# Metrics definitions
app_up_metric = meter.create_observable_gauge(
    "app_up_status",
    callbacks=[app_up_status_callback],
    description="Shows if the app is running (1: up, 0: down)",
)

memory_usage_metric = meter.create_observable_gauge(
    "app_memory_usage",
    callbacks=[collect_memory_usage],
    description="Current memory usage of the application in MB",
)

cpu_usage_metric = meter.create_observable_gauge(
    "app_cpu_usage",
    callbacks=[collect_cpu_usage],
    description="Current CPU usage of the application in percentage",
)

query_duration_metric = meter.create_histogram(
    "app_db_query_duration",
    description="Time taken to execute database query",
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
            query_duration_metric.record(duration)

            log.info(f"Query duration: {duration:.2f} seconds")
            span.set_attribute("db.query.duration", duration)

        cursor.close()
        connection.close()
        log.info("Database connection closed.")

    except Exception as e:
        log.error(f"Database error: {e}")


if __name__ == "__main__":
    log.info("Starting the application.")
    try:
        while True:
            connect_and_query()
            log.info("Waiting before next execution...")
            time.sleep(10)  # Adjust the interval as needed
    except KeyboardInterrupt:
        log.info("Application terminated.")
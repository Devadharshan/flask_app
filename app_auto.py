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
app_up_metric = meter.create_observable_gauge(
    "app_up_status",
    callbacks=[lambda options: 1],
    description="Shows if the app is running (1: up, 0: down)",
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




opentelemetry-instrument \
    --traces_exporter otlp_proto_http \
    --metrics_exporter otlp_proto_http \
    --exporter_endpoint http://<your-collector-endpoint>:5608 \
    python app.py


import sybpydb
from lib.logger import get_logger
from lib.traces import tracer_init

# OpenTelemetry Collector endpoint
OTEL_COLLECTOR_ENDPOINT = "http://<your-collector-endpoint>:5608"

# Initialize Logger (assuming your logger is already set up in lib/logger.py)
log = get_logger("SybaseAppLogger")

# Initialize Tracer (assuming your tracer_init is already set up in lib/traces.py)
tracer = tracer_init("SybaseApp", OTEL_COLLECTOR_ENDPOINT)


def connect_and_query():
    """
    Connects to the Sybase database, executes a query, and traces its execution.
    """
    log.info("Starting database connection and query execution.")

    try:
        # Use File System Native Authentication (no username/password)
        connection = sybpydb.connect(
            server="your_sybase_server",
            database="your_database",
        )

        cursor = connection.cursor()

        with tracer.start_as_current_span(
            "db_query_execution",
            attributes={
                "db.system": "sybase",
                "db.name": "your_database",
                "db.statement": "SELECT COUNT(*) FROM your_table",
            },
        ) as span:
            # Execute a test query
            query = "SELECT COUNT(*) FROM your_table"
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            result = cursor.fetchone()

            log.info(f"Query result: {result[0]}")
            span.set_attribute("db.query.result_count", result[0])

        cursor.close()
        connection.close()
        log.info("Database connection closed.")

    except Exception as e:
        log.error(f"Database error: {e}")


if __name__ == "__main__":
    log.info("Starting the application.")
    connect_and_query()
    log.info("Application finished.")




import logging

def get_logger(name: str):
    """
    Returns a configured logger instance.
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not log.handlers:
        log.addHandler(console_handler)

    return log



from lib.logger import get_logger
from lib.traces import tracer_init
import sybpydb

# Collector endpoint
OTEL_COLLECTOR_ENDPOINT = "http://<your-collector-endpoint>:5608"

# Initialize Logger
log = get_logger("SybaseAppLogger")

# Initialize Tracer
tracer = tracer_init("SybaseApp", OTEL_COLLECTOR_ENDPOINT)

def connect_and_query():
    """
    Connects to the Sybase database and executes a sample query.
    """
    log.info("Starting the database connection and query execution.")

    try:
        # Use File System Native Authentication (no username/password)
        connection = sybpydb.connect(
            server="your_sybase_server",
            database="your_database",
        )

        cursor = connection.cursor()

        with tracer.start_as_current_span(
            "db_query_execution",
            attributes={"db.system": "sybase", "db.name": "your_database"}
        ) as span:
            # Execute a test query
            query = "SELECT COUNT(*) FROM your_table"
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            result = cursor.fetchone()

            log.info(f"Query Result: {result[0]}")
            span.set_attribute("db.query.result_count", result[0])

        cursor.close()
        connection.close()
        log.info("Database connection closed.")

    except Exception as e:
        log.error(f"Database error: {e}")

if __name__ == "__main__":
    log.info("Starting the application.")
    connect_and_query()
    log.info("Application finished.")
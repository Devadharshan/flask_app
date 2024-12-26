#pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp psutil sybpydb


import sybpydb
import logging
import psutil
import time
from lib.trace import init_tracer  # Assumes you have a trace.py file to configure OpenTelemetry
from opentelemetry import trace
from opentelemetry.metrics import get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Initialize tracing
init_tracer()

# Initialize logging
logger = logging.getLogger("sybase_otel_monitor")
logging.basicConfig(level=logging.INFO)

# Set up OpenTelemetry metrics
exporter = OTLPMetricExporter(endpoint="your_grafana_endpoint:4317", insecure=True)  # Replace with your endpoint
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
meter = provider.get_meter("sybase_otel_monitor")

# Register the meter provider
trace.set_meter_provider(provider)

# Define metrics
cpu_usage_metric = meter.create_observable_gauge(
    name="app_cpu_usage",
    description="CPU usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.cpu_percent(), {})],  # Callback for CPU usage
    ],
)

memory_usage_metric = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Memory usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.virtual_memory().percent, {})],  # Callback for memory usage
    ],
)

# Configure Sybase connection
DB_SERVER = "your_sybase_server"
DATABASE_NAME = "your_database_name"


def connect_to_sybase():
    """
    Establish a connection to the Sybase database using sybpydb.
    """
    try:
        conn = sybpydb.connect(dsn=f"server name={DB_SERVER}; database={DATABASE_NAME}; chainxacts=0")
        logger.info("Successfully connected to the Sybase database")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Sybase: {e}")
        raise


def execute_query(query: str):
    """
    Execute a query on the Sybase database and return the results.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("execute_query"):
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            logger.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            logger.info("Query executed successfully")
            return rows
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


def main():
    """
    Main function to execute a Sybase query and log results.
    """
    query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your query
    try:
        logger.info("Collecting system metrics")
        cpu_usage_metric.callback()
        memory_usage_metric.callback()

        logger.info("Executing database query")
        results = execute_query(query)
        logger.info(f"Query Results: {results}")

    except Exception as e:
        logger.error("Failed to execute main process", exc_info=True)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # Run every 5 minutes



-------------------------

import sybpydb
import logging
import psutil
import time
from lib.trace import init_tracer  # Assumes you have a trace.py file to configure OpenTelemetry
from opentelemetry import trace
from opentelemetry.metrics import get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Initialize logging
logger = logging.getLogger("sybase_otel_monitor")
logging.basicConfig(level=logging.INFO)

# Set up OpenTelemetry Tracing
init_tracer()

# Set up OpenTelemetry Metrics
try:
    exporter = OTLPMetricExporter(endpoint="your_grafana_endpoint:4317", insecure=True)  # Replace with your endpoint
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader])
    trace.set_meter_provider(provider)
    meter = provider.get_meter("sybase_otel_monitor")
    logger.info("OpenTelemetry metrics and tracing initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize OpenTelemetry: {e}")
    raise

# Define metrics with labels
cpu_usage_metric = meter.create_observable_gauge(
    name="app_cpu_usage",
    description="CPU usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.cpu_percent(), {"app_name": "test_python_app"})],  # Add label `test_python_app`
    ],
)

memory_usage_metric = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Memory usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.virtual_memory().percent, {"app_name": "test_python_app"})],  # Add label `test_python_app`
    ],
)

# Configure Sybase connection
DB_SERVER = "your_sybase_server"
DATABASE_NAME = "your_database_name"


def connect_to_sybase():
    """
    Establish a connection to the Sybase database using sybpydb.
    """
    try:
        conn = sybpydb.connect(dsn=f"server name={DB_SERVER}; database={DATABASE_NAME}; chainxacts=0")
        logger.info("Successfully connected to the Sybase database")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Sybase: {e}")
        raise


def execute_query(query: str):
    """
    Execute a query on the Sybase database and return the results.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("execute_query"):
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            logger.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            logger.info("Query executed successfully")
            return rows
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


def main():
    """
    Main function to execute a Sybase query and send metrics.
    """
    query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your query
    try:
        # Log CPU and memory metrics
        logger.info("Collecting system metrics")
        cpu_usage_metric.callback()
        memory_usage_metric.callback()

        # Execute database query
        logger.info("Executing database query")
        results = execute_query(query)
        logger.info(f"Query Results: {results}")

    except Exception as e:
        logger.error("Failed to execute main process", exc_info=True)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # Run every 5 minutes



-------------------


import sybpydb
import psutil
import time
from lib.trace import init_tracer  # Your custom tracing setup
from lib.logger import log  # Assuming `log` is your logging instance from lib.logger
from opentelemetry import trace
from opentelemetry.metrics import get_meter_provider

# Set up OpenTelemetry Tracing and Metrics
try:
    init_tracer()  # Initializes tracing and metric export with certs (configured in your `lib/trace.py`)
    meter = get_meter_provider().get_meter("sybase_otel_cert_monitor")
    log.info("OpenTelemetry metrics and tracing initialized successfully.")
except Exception as e:
    log.error(f"Failed to initialize OpenTelemetry: {e}")
    raise

# Define metrics with labels
cpu_usage_metric = meter.create_observable_gauge(
    name="app_cpu_usage",
    description="CPU usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.cpu_percent(), {"app_name": "test_python_app"})],  # Add label `test_python_app`
    ],
)

memory_usage_metric = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Memory usage of the application",
    unit="%",
    callbacks=[
        lambda: [(psutil.virtual_memory().percent, {"app_name": "test_python_app"})],  # Add label `test_python_app`
    ],
)

# Configure Sybase connection
DB_SERVER = "your_sybase_server"
DATABASE_NAME = "your_database_name"


def connect_to_sybase():
    """
    Establish a connection to the Sybase database using sybpydb.
    """
    try:
        conn = sybpydb.connect(dsn=f"server name={DB_SERVER}; database={DATABASE_NAME}; chainxacts=0")
        log.info("Successfully connected to the Sybase database")
        return conn
    except Exception as e:
        log.error(f"Error connecting to Sybase: {e}")
        raise


def execute_query(query: str):
    """
    Execute a query on the Sybase database and return the results.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("execute_query"):
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            log.info("Query executed successfully")
            return rows
        except Exception as e:
            log.error(f"Error executing query: {e}")
            raise


def main():
    """
    Main function to execute a Sybase query and send metrics.
    """
    query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your query
    try:
        # Log CPU and memory metrics
        log.info("Collecting system metrics")
        cpu_usage_metric.callback()
        memory_usage_metric.callback()

        # Execute database query
        log.info("Executing database query")
        results = execute_query(query)
        log.info(f"Query Results: {results}")

    except Exception as e:
        log.error("Failed to execute main process", exc_info=True)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # Run every 5 minutes



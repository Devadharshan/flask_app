pip install opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-api
pip uninstall opentelemetry-exporter-otlp -y
pip install opentelemetry-exporter-otlp


from opentelemetry.exporter.otlp.trace import OTLPTraceExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize TracerProvider
tracer_provider = TracerProvider()
trace_exporter = OTLPTraceExporter(endpoint="http://<collector_address>:5608")
span_processor = BatchSpanProcessor(trace_exporter)
tracer_provider.add_span_processor(span_processor)

import logging
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.metrics import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.trace import OTLPTraceExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

# Set up logging
log = logging.getLogger('otel-metrics-debug')
log.setLevel(logging.DEBUG)  # Adjust to INFO or ERROR in production if needed
ch = logging.StreamHandler()  # Log to console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# Initialize OpenTelemetry TracerProvider
log.info("Initializing TracerProvider...")
tracer_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "test_python_app"})
)
trace_exporter = OTLPTraceExporter(endpoint="http://<collector_address>:5608")
span_processor = BatchSpanProcessor(trace_exporter)
tracer_provider.add_span_processor(span_processor)

# Initialize OpenTelemetry MeterProvider and OTLP Metrics Exporter
log.info("Initializing MeterProvider...")
meter_provider = MeterProvider(resource=Resource.create({SERVICE_NAME: "test_python_app"}))

# Initialize OTLP Metric Exporter (this sends metrics to the collector)
log.info("Initializing OTLP Metric Exporter...")
otlp_metric_exporter = OTLPMetricExporter(endpoint="http://<collector_address>:5608", insecure=True)

# Use PeriodicExportingMetricReader to periodically export metrics to the OTLP exporter
reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)  # Exports every 5 seconds
meter_provider.add_metric_reader(reader)

# Set up the meter for creating metrics
meter = meter_provider.get_meter("test_python_app")

# Create some sample metrics (e.g., CPU and Memory usage)
cpu_usage = meter.create_gauge("app_cpu_usage", description="CPU usage of the application")
memory_usage = meter.create_gauge("app_memory_usage", description="Memory usage of the application")

# Simulate updating metrics every 5 seconds
log.info("Starting to simulate metric updates...")
try:
    while True:
        cpu_val = random.uniform(0, 100)  # Random CPU usage between 0 and 100
        memory_val = random.uniform(0, 16)  # Random memory usage between 0 and 16 GB
        cpu_usage.add(cpu_val, labels={"app_name": "test_python_app"})
        memory_usage.add(memory_val, labels={"app_name": "test_python_app"})
        
        log.debug(f"Updated metrics - CPU Usage: {cpu_val}, Memory Usage: {memory_val}")
        
        time.sleep(5)  # Wait for 5 seconds before updating again

except KeyboardInterrupt:
    log.info("Metric simulation stopped by user.")


----===
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp
pip install opentelemetry-exporter-prometheus  # If using Prometheus
pip install opentelemetry-instrumentation       # If using automatic instrumentation
pip install opentelemetry-api
pip install sybpydb  # If you're connecting to a Sybase database




import logging
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.metrics import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.trace import OTLPTraceExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

# Set up logging
log = logging.getLogger('otel-metrics-debug')
log.setLevel(logging.DEBUG)  # Adjust to INFO or ERROR in production if needed
ch = logging.StreamHandler()  # Log to console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# Initialize OpenTelemetry Meter Provider
log.info("Initializing MeterProvider...")
meter_provider = MeterProvider()
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter("test_python_app")

# Set up OpenTelemetry Tracer
log.info("Initializing TracerProvider...")
tracer_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "test_python_app"})
)
trace_exporter = OTLPTraceExporter(endpoint="http://<collector_address>:5608")
span_processor = BatchSpanProcessor(trace_exporter)
tracer_provider.add_span_processor(span_processor)

# Initialize OTLP Metrics Exporter for sending metrics to the collector
log.info("Initializing OTLP Metrics Exporter...")
otlp_metric_exporter = OTLPMetricExporter(endpoint="http://<collector_address>:5608", insecure=True)
meter_provider.start_pipeline(meter, otlp_metric_exporter)

# Simulate starting Prometheus HTTP server (optional, for local development only)
# If your collector exposes an endpoint, you may not need this.
log.info("Starting Prometheus HTTP server (for local use)...")
# start_http_server(8000)  # Exposing metrics at http://localhost:8000/metrics

# Create some sample metrics (e.g., CPU and Memory usage)
cpu_usage = meter.create_gauge("app_cpu_usage", description="CPU usage of the application")
memory_usage = meter.create_gauge("app_memory_usage", description="Memory usage of the application")

# Simulate updating metrics every 5 seconds
log.info("Starting to simulate metric updates...")
try:
    while True:
        cpu_val = random.uniform(0, 100)  # Random CPU usage between 0 and 100
        memory_val = random.uniform(0, 16)  # Random memory usage between 0 and 16 GB
        cpu_usage.add(cpu_val, labels={"app_name": "test_python_app"})
        memory_usage.add(memory_val, labels={"app_name": "test_python_app"})
        
        log.debug(f"Updated metrics - CPU Usage: {cpu_val}, Memory Usage: {memory_val}")
        
        time.sleep(5)  # Wait for 5 seconds before updating again

except KeyboardInterrupt:
    log.info("Metric simulation stopped by user.")



#pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp psutil sybpydb
import sybpydb
import psutil
import time
from lib.trace import tracer_init  # Your custom tracing setup
from lib.logger import log  # Assuming `log` is your logging instance from lib.logger
from opentelemetry import trace
from opentelemetry.metrics import get_meter_provider

# Initialize OpenTelemetry Tracing and Metrics
try:
    tracer_init()  # Custom tracing setup (configured in your `lib/trace.py`)
    meter = get_meter_provider().get_meter("sybase_otel_cert_monitor")
    log.info("OpenTelemetry metrics and tracing initialized successfully.")
except Exception as e:
    log.error(f"Failed to initialize OpenTelemetry: {e}")
    raise

# Define metrics with labels
cpu_usage_metric = meter.create_up_down_counter(
    name="app_cpu_usage",
    description="CPU usage of the application",
    unit="%",
)

memory_usage_metric = meter.create_up_down_counter(
    name="app_memory_usage",
    description="Memory usage of the application",
    unit="%",
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
    with tracer.start_as_current_span(
        "execute_query", attributes={"query": query}
    ) as span:
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            span.set_attribute("query_result_count", len(rows))
            log.info("Query executed successfully")
            return rows
        except Exception as e:
            log.error(f"Error executing query: {e}")
            raise


def report_metrics():
    """
    Report system-level metrics (CPU and memory usage).
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("report_metrics"):
        try:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            # Record metrics with labels
            cpu_usage_metric.add(cpu_usage, {"app_name": "test_python_app"})
            memory_usage_metric.add(memory_usage, {"app_name": "test_python_app"})

            log.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        except Exception as e:
            log.error(f"Error reporting metrics: {e}")


def main():
    """
    Main function to execute a Sybase query and send metrics.
    """
    query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your query
    try:
        # Collect and report metrics
        report_metrics()

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

--------
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




0--------


import sybpydb
import psutil
import time
from lib.trace import tracer_init  # Your custom tracing setup
from lib.logger import log  # Assuming `log` is your logging instance from lib.logger
from opentelemetry import trace
from opentelemetry.metrics import get_meter_provider, Observation

# Initialize OpenTelemetry Tracing and Metrics
try:
    tracer_init()  # Custom tracing setup (configured in your `lib/trace.py`)
    meter = get_meter_provider().get_meter("sybase_otel_cert_monitor")
    log.info("OpenTelemetry metrics and tracing initialized successfully.")
except Exception as e:
    log.error(f"Failed to initialize OpenTelemetry: {e}")
    raise

# Define metrics with labels
cpu_usage_metric = meter.create_up_down_counter(
    name="app_cpu_usage",
    description="CPU usage of the application",
    unit="%",
)

memory_usage_metric = meter.create_up_down_counter(
    name="app_memory_usage",
    description="Memory usage of the application",
    unit="%",
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
    with tracer.start_as_current_span(
        "execute_query", attributes={"query": query}
    ) as span:
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            span.set_attribute("query_result_count", len(rows))
            log.info("Query executed successfully")
            return rows
        except Exception as e:
            log.error(f"Error executing query: {e}")
            raise


def report_metrics():
    """
    Report system-level metrics (CPU and memory usage).
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("report_metrics"):
        try:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            # Add metrics with labels
            cpu_usage_metric.add(cpu_usage, {"app_name": "test_python_app"})
            memory_usage_metric.add(memory_usage, {"app_name": "test_python_app"})

            log.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        except Exception as e:
            log.error(f"Error reporting metrics: {e}")


def main():
    """
    Main function to execute a Sybase query and send metrics.
    """
    query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your query
    try:
        # Collect and report metrics
        report_metrics()

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



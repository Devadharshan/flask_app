from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.metrics import get_meter
from lib.tracer import tracer_init
from lib.logger import log
import sybpydb
import psutil
import time

# Initialize Tracer
tracer = tracer_init()

# Configure Metrics Exporter
resource = Resource.create({"service.name": "test_python_app"})
metric_exporter = OTLPMetricExporter(
    endpoint="http://<collector_address>:5608",  # Replace with your OTLP collector endpoint
    insecure=True,
)
metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
meter = get_meter("test_python_app", meter_provider=meter_provider)

# Callback Functions for Metrics
def collect_cpu_usage(observer):
    try:
        usage = psutil.cpu_percent(interval=1)
        observer.observe(usage, {"metric": "cpu_usage"})
    except Exception as e:
        log.error(f"Failed to collect CPU usage: {e}")

def collect_memory_usage(observer):
    try:
        memory = psutil.virtual_memory()
        observer.observe(memory.percent, {"metric": "memory_usage"})
    except Exception as e:
        log.error(f"Failed to collect memory usage: {e}")

def collect_disk_usage(observer):
    try:
        disk = psutil.disk_usage("/")
        observer.observe(disk.percent, {"metric": "disk_usage"})
    except Exception as e:
        log.error(f"Failed to collect disk usage: {e}")

def collect_db_connection_status(observer):
    try:
        connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
        connection.close()
        observer.observe(1.0, {"metric": "db_connection_status"})  # Database is up
    except Exception:
        observer.observe(0.0, {"metric": "db_connection_status"})  # Database is down

# Define Metrics with Proper Callbacks
meter.create_observable_gauge(
    "app.cpu.usage",
    description="CPU usage of the application",
    callbacks=[collect_cpu_usage],
)

meter.create_observable_gauge(
    "app.memory.usage",
    description="Memory usage of the application",
    callbacks=[collect_memory_usage],
)

meter.create_observable_gauge(
    "app.disk.usage",
    description="Disk usage of the application",
    callbacks=[collect_disk_usage],
)

meter.create_observable_gauge(
    "app.db.connection.status",
    description="Database connection status (1 for up, 0 for down)",
    callbacks=[collect_db_connection_status],
)

db_query_duration = meter.create_histogram(
    "app.db.query.duration",
    description="Time taken to execute a database query",
)

user_logged_in = meter.create_counter(
    "app.db.user.logged_in",
    description="Number of times a user connects to the database",
)

# Function to Query Sybase and Log Metrics
def query_sybase():
    with tracer.start_as_current_span("sybase-query", attributes={"db.system": "sybase"}):
        try:
            start_time = time.time()
            
            # Establish connection
            connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
            user_id = connection.getuser()  # Get the user ID
            log.info(f"Connected to Sybase database as user: {user_id}")
            user_logged_in.add(1, {"user_id": user_id})

            # Execute a query
            query = "SELECT COUNT(*) FROM your_table_name"  # Replace with your actual query
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            log.info(f"Query result: {result[0]}")

            # Record query duration
            duration = time.time() - start_time
            db_query_duration.record(duration, {"query": "SELECT COUNT(*)"})
            log.info(f"Query executed in {duration:.2f} seconds")

            cursor.close()
            connection.close()

        except Exception as e:
            log.error(f"Failed to execute query: {e}")

# Main Application Logic
def main():
    with tracer.start_as_current_span("main-operation", attributes={"operation": "demo"}):
        log.info("Starting the main operation")
        query_sybase()  # Call the function to run the Sybase query
        log.info("Main operation completed successfully")

# Run Application Loop
if __name__ == "__main__":
    log.info("Starting Python application with OpenTelemetry metrics and tracing")
    while True:
        try:
            main()
        except Exception as e:
            log.error(f"An error occurred in the main loop: {e}")
        time.sleep(10)



from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.metrics import get_meter
from lib.tracer import tracer_init
from lib.logger import log
import sybpydb
import psutil
import time

# Initialize Tracer
tracer = tracer_init()

# Configure Metrics Exporter
resource = Resource.create({"service.name": "test_python_app"})
metric_exporter = OTLPMetricExporter(
    endpoint="http://<collector_address>:5608",  # Replace with your OTLP collector endpoint
    insecure=True,
)
metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
meter = get_meter("test_python_app", meter_provider=meter_provider)

# Callback Functions for Metrics
def collect_cpu_usage():
    try:
        usage = psutil.cpu_percent(interval=1)
        return [("cpu", usage)]
    except Exception as e:
        log.error(f"Failed to collect CPU usage: {e}")
        return []

def collect_memory_usage():
    try:
        memory = psutil.virtual_memory()
        return [("memory", memory.percent)]
    except Exception as e:
        log.error(f"Failed to collect memory usage: {e}")
        return []

def collect_disk_usage():
    try:
        disk = psutil.disk_usage("/")
        return [("disk", disk.percent)]
    except Exception as e:
        log.error(f"Failed to collect disk usage: {e}")
        return []

def collect_db_connection_status():
    try:
        connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
        connection.close()
        return [("status", 1.0)]  # Database is up
    except Exception:
        return [("status", 0.0)]  # Database is down

# Define Metrics with Callbacks
cpu_usage = meter.create_observable_gauge(
    "app.cpu.usage",
    description="CPU usage of the application",
    callbacks=[lambda: collect_cpu_usage()],
)

memory_usage = meter.create_observable_gauge(
    "app.memory.usage",
    description="Memory usage of the application",
    callbacks=[lambda: collect_memory_usage()],
)

disk_usage = meter.create_observable_gauge(
    "app.disk.usage",
    description="Disk usage of the application",
    callbacks=[lambda: collect_disk_usage()],
)

db_connection_status = meter.create_observable_gauge(
    "app.db.connection.status",
    description="Database connection status (1 for up, 0 for down)",
    callbacks=[lambda: collect_db_connection_status()],
)

db_query_duration = meter.create_histogram(
    "app.db.query.duration",
    description="Time taken to execute a database query",
)

user_logged_in = meter.create_counter(
    "app.db.user.logged_in",
    description="Number of times a user connects to the database",
)

# Function to Query Sybase and Log Metrics
def query_sybase():
    with tracer.start_as_current_span("sybase-query", attributes={"db.system": "sybase"}):
        try:
            start_time = time.time()
            
            # Establish connection
            connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
            user_id = connection.getuser()  # Get the user ID
            log.info(f"Connected to Sybase database as user: {user_id}")
            user_logged_in.add(1, {"user_id": user_id})

            # Execute a query
            query = "SELECT COUNT(*) FROM your_table_name"  # Replace with your actual query
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            log.info(f"Query result: {result[0]}")

            # Record query duration
            duration = time.time() - start_time
            db_query_duration.record(duration, {"query": "SELECT COUNT(*)"})
            log.info(f"Query executed in {duration:.2f} seconds")

            cursor.close()
            connection.close()

        except Exception as e:
            log.error(f"Failed to execute query: {e}")

# Main Application Logic
def main():
    with tracer.start_as_current_span("main-operation", attributes={"operation": "demo"}):
        log.info("Starting the main operation")
        query_sybase()  # Call the function to run the Sybase query
        log.info("Main operation completed successfully")

# Run Application Loop
if __name__ == "__main__":
    log.info("Starting Python application with OpenTelemetry metrics and tracing")
    while True:
        try:
            main()
        except Exception as e:
            log.error(f"An error occurred in the main loop: {e}")
        time.sleep(10)
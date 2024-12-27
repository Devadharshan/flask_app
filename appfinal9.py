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
    endpoint="http://<collector_address>:5608",  # Replace with your collector endpoint
    insecure=True,
)
metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
meter = get_meter("test_python_app", meter_provider=meter_provider)

# Callback Functions
def collect_cpu_usage(callback_options=None):
    """Collect CPU usage."""
    try:
        usage = psutil.cpu_percent()
        log.info(f"CPU Usage: {usage}%")
        return [(usage, {"metric": "cpu_usage"})]
    except Exception as e:
        log.error(f"Error in CPU Usage Callback: {e}")
        return [(0.0, {"metric": "cpu_usage"})]  # Return a default value on failure

def collect_memory_usage(callback_options=None):
    """Collect Memory usage."""
    try:
        memory = psutil.virtual_memory()
        log.info(f"Memory Usage: {memory.percent}%")
        return [(memory.percent, {"metric": "memory_usage"})]
    except Exception as e:
        log.error(f"Error in Memory Usage Callback: {e}")
        return [(0.0, {"metric": "memory_usage"})]

def collect_disk_usage(callback_options=None):
    """Collect Disk usage."""
    try:
        disk = psutil.disk_usage("/")
        log.info(f"Disk Usage: {disk.percent}%")
        return [(disk.percent, {"metric": "disk_usage"})]
    except Exception as e:
        log.error(f"Error in Disk Usage Callback: {e}")
        return [(0.0, {"metric": "disk_usage"})]

def collect_db_connection_status(callback_options=None):
    """Check database connection status."""
    try:
        connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
        connection.close()
        log.info("Database is reachable")
        return [(1.0, {"metric": "db_connection_status"})]  # Database is up
    except Exception as e:
        log.error(f"Database Connection Error: {e}")
        return [(0.0, {"metric": "db_connection_status"})]  # Database is down

# Observable Metrics
meter.create_observable_gauge(
    "app.cpu.usage",
    callbacks=[collect_cpu_usage],
    description="CPU usage percentage",
)

meter.create_observable_gauge(
    "app.memory.usage",
    callbacks=[collect_memory_usage],
    description="Memory usage percentage",
)

meter.create_observable_gauge(
    "app.disk.usage",
    callbacks=[collect_disk_usage],
    description="Disk usage percentage",
)

meter.create_observable_gauge(
    "app.db.connection.status",
    callbacks=[collect_db_connection_status],
    description="Database connection status (1 for up, 0 for down)",
)

# Histogram and Counter
db_query_duration = meter.create_histogram(
    "app.db.query.duration",
    description="Duration of database queries in seconds",
)

user_logged_in = meter.create_counter(
    "app.db.user.logged_in",
    description="Count of users connecting to the database",
)

# Database Query Function
def query_sybase():
    with tracer.start_as_current_span("sybase-query", attributes={"db.system": "sybase"}):
        try:
            start_time = time.time()
            
            # Connect to Sybase
            connection = sybpydb.connect(servername="your_server_name", database="your_database_name")
            user_id = connection.getuser()
            log.info(f"Connected to database as user: {user_id}")
            user_logged_in.add(1, {"user_id": user_id})

            # Execute query
            query = "SELECT COUNT(*) FROM your_table_name"
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            log.info(f"Query result: {result[0]}")

            # Record duration
            duration = time.time() - start_time
            db_query_duration.record(duration, {"query": "SELECT COUNT(*)"})
            log.info(f"Query executed in {duration:.2f} seconds")

            cursor.close()
            connection.close()

        except Exception as e:
            log.error(f"Database query failed: {e}")

# Main Loop
def main():
    log.info("Starting main loop")
    while True:
        query_sybase()
        time.sleep(10)

if __name__ == "__main__":
    log.info("Starting the Python application")
    main()
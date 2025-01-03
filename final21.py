import time
import psutil
import sybpydb
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Set up OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Metrics Exporter and Provider
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter
meter = metrics.get_meter_provider().get_meter("sybase_app")

# CPU usage callback function (returns the metric value)
def get_cpu_usage():
    """Fetch CPU usage percentage of the current process."""
    return psutil.Process().cpu_percent(interval=None)

# Memory usage callback function (returns the metric value)
def get_memory_usage():
    """Fetch memory usage of the current process in bytes (RSS)."""
    return psutil.Process().memory_info().rss

# Create UpDown Counters for CPU usage and memory usage
cpu_usage_metric = meter.create_up_down_counter(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="%",
    callback=lambda: [(get_cpu_usage(), {})],
)

memory_usage_metric = meter.create_up_down_counter(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes",
    unit="bytes",
    callback=lambda: [(get_memory_usage(), {})],
)

# Create custom metrics
query_execution_time_metric = meter.create_up_down_counter(
    name="sybase_query_execution_time_ms",
    description="Execution time of Sybase queries in milliseconds",
    unit="ms",
)

rows_returned_metric = meter.create_up_down_counter(
    name="sybase_query_rows_returned",
    description="Number of rows returned by Sybase queries",
    unit="1",
)

query_failure_metric = meter.create_up_down_counter(
    name="sybase_query_failures",
    description="Count of failed Sybase queries",
    unit="1",
)

active_connections_metric = meter.create_up_down_counter(
    name="sybase_active_connections",
    description="Number of active connections to the Sybase database",
    unit="1",
)

transaction_rate_metric = meter.create_up_down_counter(
    name="sybase_transaction_rate",
    description="Rate of transactions in the Sybase database (transactions per second)",
    unit="1",
)

# Sybase database connection parameters
def connect_to_sybase():
    """Create a connection to the Sybase database."""
    try:
        conn = sybpydb.connect(
            servername="SYBASE_SERVER_NAME",
            database="DATABASE_NAME",
            user="USERNAME",
            password="PASSWORD"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Sybase: {e}")
        query_failure_metric.add(1)  # Increment failure count
        return None

# Fetch active connections and transaction rate
def fetch_sybase_metrics(conn):
    """Fetch active connections and transaction rate from Sybase."""
    try:
        cursor = conn.cursor()

        # Query for active connections (replace with appropriate Sybase query)
        cursor.execute("SELECT COUNT(*) FROM master.dbo.sysprocesses WHERE status = 'active'")
        active_connections = cursor.fetchone()[0]
        active_connections_metric.add(active_connections)
        print(f"Active Connections: {active_connections}")

        # Query for transaction rate (replace with appropriate Sybase query)
        cursor.execute("SELECT SUM(tran_begin) - SUM(tran_commit) AS transaction_rate FROM master.dbo.sysmon")
        transaction_rate = cursor.fetchone()[0]
        transaction_rate_metric.add(transaction_rate)
        print(f"Transaction Rate: {transaction_rate}")
    except Exception as e:
        print(f"Failed to fetch Sybase metrics: {e}")
        query_failure_metric.add(1)  # Increment failure count

# Execute a sample query
def execute_query(conn):
    """Execute a sample query on the Sybase database."""
    try:
        start_time = time.time()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM some_table")  # Replace with your query
        rows = cursor.fetchone()
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Record custom metrics
        query_execution_time_metric.add(execution_time)
        rows_returned_metric.add(rows[0] if rows else 0)
        print(f"Query executed in {execution_time} ms, returned {rows[0]} rows")
    except Exception as e:
        print(f"Query execution failed: {e}")
        query_failure_metric.add(1)  # Increment failure count

# Main function to record metrics
def record_metrics():
    """Record metrics for the process and database."""
    conn = connect_to_sybase()
    if conn:
        execute_query(conn)
        fetch_sybase_metrics(conn)
        conn.close()

# Keep the application running
print("Metrics collection running. Sending to OTLP endpoint...")
while True:
    record_metrics()  # Record the metrics
    time.sleep(10)  # Wait for the next collection cycle

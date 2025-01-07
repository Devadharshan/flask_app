import time
import logging
import psutil
from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.logs import LoggingHandler, LogEmitterProvider
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentation
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry._logs import set_log_emitter_provider
from opentelemetry.trace.status import Status, StatusCode
from sybpydb import connect

# Define the OTLP endpoint
OTLP_ENDPOINT = "http://localhost:4317"

# Set up OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider
trace_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("sybase_app")

# Metrics Provider
metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter_provider().get_meter("sybase_app")

# System Metrics (Host-level metrics instrumentation)
SystemMetricsInstrumentation(
    meter=meter,
    resource=resource,
    exporter=metric_exporter,
    export_interval_millis=10000,
).start()

# Logging setup
log_exporter = OTLPLogExporter(endpoint=OTLP_ENDPOINT, insecure=True)
log_emitter_provider = LogEmitterProvider(resource=resource)
set_log_emitter_provider(log_emitter_provider)
log_handler = LoggingHandler(level=logging.INFO, log_exporter=log_exporter)
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
logger = logging.getLogger(__name__)

# Application-specific custom metrics
active_connections_metric = meter.create_up_down_counter(
    name="sybase_active_connections",
    description="Number of active connections in the Sybase database",
    unit="1",
)
transaction_rate_metric = meter.create_up_down_counter(
    name="sybase_transaction_rate",
    description="Transaction rate in the Sybase database",
    unit="transactions/s",
)

# Process-level custom metrics (CPU and memory usage of the application)
cpu_usage_metric = meter.create_up_down_counter(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="%",
)
memory_usage_metric = meter.create_up_down_counter(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes",
    unit="bytes",
)

# Helper functions
def get_cpu_usage():
    """Fetch CPU usage percentage of the current process."""
    return psutil.Process().cpu_percent(interval=None)

def get_memory_usage():
    """Fetch memory usage of the current process in bytes (RSS)."""
    return psutil.Process().memory_info().rss

def fetch_active_connections():
    """Fetch the number of active connections in Sybase."""
    query = "SELECT COUNT(*) FROM master..sysprocesses WHERE status='active'"
    result = trace_sybase_query(query, "Fetch Active Connections")
    return result[0][0] if result else 0

def fetch_transaction_rate():
    """Fetch the transaction rate in Sybase."""
    query = """
        SELECT COUNT(*) AS transaction_count 
        FROM master..syslogins 
        WHERE logindatetime > GETDATE() - 1
    """
    result = trace_sybase_query(query, "Calculate Transaction Rate")
    return result[0][0] if result else 0

# Tracing for Sybase operations
def trace_sybase_query(query, operation_context):
    """
    Trace a Sybase query with a dynamic operation name.
    
    :param query: The SQL query to execute.
    :param operation_context: A dynamic description of the operation.
    """
    operation_name = f"Sybase Operation: {operation_context}"
    with tracer.start_as_current_span(operation_name) as span:
        logger.info(f"Executing query: {query}")
        try:
            with connect(dsn="server=your_server;database=your_db;chainxacts=0") as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                logger.info(f"Query executed successfully: {query}")
                
                # Set span attributes for additional metadata
                span.set_attribute("db.query", query)
                span.set_attribute("db.operation_context", operation_context)
                span.set_attribute("db.row_count", len(result))
                return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

# Function to record custom metrics
def record_metrics():
    """Record metrics by fetching current system and custom metrics."""
    # Process-level metrics
    cpu_usage_metric.add(get_cpu_usage())
    memory_usage_metric.add(get_memory_usage())
    
    # Application-specific custom metrics
    active_connections = fetch_active_connections()
    active_connections_metric.add(active_connections)
    
    transaction_rate = fetch_transaction_rate()
    transaction_rate_metric.add(transaction_rate)

# Application loop
print("Metrics collection, system instrumentation, tracing, and logging running. Sending data to OTLP endpoint...")
while True:
    try:
        record_metrics()  # Record custom metrics
    except Exception as e:
        logger.error(f"Error during metrics collection: {e}")
    time.sleep(10)  # Wait for the next collection cycle

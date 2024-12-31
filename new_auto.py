import sybpydb
import time
from opentelemetry import trace, metrics, logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.logs.export import BatchLogProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.logs_exporter import OTLPLogExporter
import logging

# Configuration
DATABASE_DSN = "server name=YOUR_SERVER_NAME;database=YOUR_DATABASE_NAME;chainxacts=0"
OTEL_COLLECTOR_ENDPOINT = "http://your-otel-collector-endpoint:4317"

# Logger setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("custom_logger")

# OpenTelemetry setup
def setup_otel():
    # Trace setup
    tracer_provider = TracerProvider()
    span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_COLLECTOR_ENDPOINT))
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Metrics setup
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT)
            )
        ]
    )
    metrics.set_meter_provider(meter_provider)

    # Logs setup
    logger_provider = LoggerProvider()
    log_processor = BatchLogProcessor(OTLPLogExporter(endpoint=OTEL_COLLECTOR_ENDPOINT))
    logger_provider.add_log_processor(log_processor)
    logs.set_logger_provider(logger_provider)

# Database query function
def fetch_data():
    try:
        connection = sybpydb.connect(dsn=DATABASE_DSN)
        cursor = connection.cursor()
        query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your actual query
        start_time = time.time()

        cursor.execute(query)
        rows = cursor.fetchall()

        query_duration = time.time() - start_time
        logger.info(f"Query executed in {query_duration:.2f} seconds")
        logger.info(f"Fetched {len(rows)} rows")

        return rows, query_duration
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

# Main application logic
def main():
    setup_otel()

    tracer = trace.get_tracer("app_tracer")
    meter = metrics.get_meter("app_meter")

    # Define a custom metric
    db_query_duration_metric = meter.create_histogram(
        name="db_query_duration_seconds",
        description="Histogram of database query durations",
        unit="seconds"
    )

    with tracer.start_as_current_span("database_query"):
        rows, query_duration = fetch_data()

        # Record the query duration as a metric
        db_query_duration_metric.record(query_duration)

    logger.info("Application execution completed")

if __name__ == "__main__":
    main()

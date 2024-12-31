import sybpydb
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
from lib.logger import Logger
from lib.tracer import Tracer
from config import DATABASE_CONFIG, OTEL_CONFIG
import time

# Auto-instrumentation setup
def setup_otel():
    # Trace setup
    tracer_provider = TracerProvider()
    span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_CONFIG["otel_collector_endpoint"]))
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Metrics setup
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=OTEL_CONFIG["otel_collector_endpoint"])
            )
        ]
    )
    metrics.set_meter_provider(meter_provider)

    # Logs setup
    logger_provider = LoggerProvider()
    log_processor = BatchLogProcessor(OTLPLogExporter(endpoint=OTEL_CONFIG["otel_collector_endpoint"]))
    logger_provider.add_log_processor(log_processor)
    logs.set_logger_provider(logger_provider)


# Function to fetch data from Sybase
def fetch_data():
    try:
        connection = sybpydb.connect(dsn=DATABASE_CONFIG["dsn"])
        cursor = connection.cursor()
        query = "SELECT TOP 10 * FROM your_table_name"  # Replace with your actual query
        start_time = time.time()

        cursor.execute(query)
        rows = cursor.fetchall()

        # Custom logging
        Logger.log_info(f"Query executed in {time.time() - start_time:.2f} seconds")
        Logger.log_info(f"Fetched {len(rows)} rows")

        return rows
    except Exception as e:
        Logger.log_error(f"Error fetching data: {e}")
        raise


def main():
    setup_otel()

    tracer = Tracer.get_tracer("app_tracer")  # Your custom tracer implementation
    meter = metrics.get_meter("app_meter")

    # Define custom metric
    db_query_duration = meter.create_histogram(
        name="db_query_duration",
        description="Histogram of database query durations",
        unit="seconds"
    )

    with tracer.start_as_current_span("database_query"):
        rows = fetch_data()
        db_query_duration.record(len(rows))

    Logger.log_info("Application execution completed")


if __name__ == "__main__":
    main()

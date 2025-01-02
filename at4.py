import time
import sybpydb
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Set up tracing
resource = Resource.create(attributes={"service.name": "sybase_app"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Set up metrics
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True))],
)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("sybase_app")

# Metrics
query_execution_time_metric = meter.create_histogram(
    "sybase_query_execution_time",
    unit="ms",
    description="Execution time of Sybase queries",
)
query_count_metric = meter.create_counter(
    "sybase_query_count",
    unit="1",
    description="Count of queries executed against Sybase",
)

# Tracer
tracer = trace.get_tracer("sybase_app")

def connect_to_sybase(server, user, password, database):
    """
    Connects to the Sybase database.
    """
    return sybpydb.connect(server=server, user=user, password=password, database=database)

def execute_query(connection, query):
    """
    Executes a query on the Sybase database.
    """
    with tracer.start_as_current_span("execute_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            query_count_metric.add(1)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            query_execution_time_metric.record(execution_time, {"query": query})
            span.set_attribute("execution_time_ms", execution_time)

def main():
    # Connect to Sybase
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    try:
        connection = connect_to_sybase(server, user, password, database)
        print("Connected to Sybase database.")
    except Exception as e:
        print(f"Failed to connect to Sybase: {e}")
        return

    # Execute queries
    queries = [
        "SELECT COUNT(*) FROM your_table",
        "SELECT TOP 10 * FROM your_table",
    ]

    for query in queries:
        try:
            results = execute_query(connection, query)
            print(f"Query executed successfully: {query}")
            print("Results:", results)
        except Exception as e:
            print(f"Failed to execute query '{query}': {e}")

    connection.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
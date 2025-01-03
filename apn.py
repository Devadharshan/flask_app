import http.server
import http.client
import threading
import time
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.logs_exporter import OTLPLogExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Set up OpenTelemetry exporters
otel_collector_endpoint = "http://localhost:4317"  # Replace with your Otel Collector endpoint

# Resource to identify the application
resource = Resource.create({"service.name": "non-flask-app"})

# Configure Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_collector_endpoint, insecure=True))
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure Metrics
metrics.set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=otel_collector_endpoint, insecure=True))]
    )
)
meter = metrics.get_meter(__name__)

# Configure Logs
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=otel_collector_endpoint, insecure=True))
)

# Instrument external libraries
RequestsInstrumentor().instrument()


# Process-level metrics
cpu_metric = meter.create_observable_gauge(
    name="process.cpu.usage",
    description="CPU usage of the process",
    callbacks=[lambda: [(os.getloadavg()[0], {})]],
)
memory_metric = meter.create_observable_gauge(
    name="process.memory.usage",
    description="Memory usage of the process",
    callbacks=[lambda: [(os.getpid().memory_info().rss / 1024 ** 2, {})]],
)


# Server implementation
class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        with tracer.start_as_current_span("server-handler"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello from the server!")


def start_server():
    server = http.server.HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
    print("Server started on http://localhost:8000")
    server.serve_forever()


# Client implementation
def client_request():
    conn = http.client.HTTPConnection("localhost", 8000)
    with tracer.start_as_current_span("client-request"):
        conn.request("GET", "/")
        response = conn.getresponse()
        print(f"Client received: {response.status} {response.reason}")
        conn.close()


if __name__ == "__main__":
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Simulate client requests
    while True:
        client_request()
        time.sleep(5)

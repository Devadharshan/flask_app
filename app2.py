from flask import Flask, jsonify
import sybpydb
import time

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.trace import set_span_in_context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenTelemetry
resource = Resource.create(attributes={"service.name": "sybase-flask-app"})

# Trace provider and exporter setup
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Metrics provider setup
metrics.set_meter_provider(MeterProvider(resource=resource))
meter = metrics.get_meter(__name__)
db_query_counter = meter.create_counter(
    name="db_query_count",
    description="Number of DB queries executed",
    unit="1",
)

# Flask instrumentation
FlaskInstrumentor().instrument_app(app)
LoggingInstrumentor().instrument()
RequestsInstrumentor().instrument()

# Sybase database connection details
DB_CONFIG = {
    "server": "your_server_name",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
}


def connect_to_sybase():
    """Connect to Sybase database."""
    conn = sybpydb.connect(
        servername=DB_CONFIG["server"],
        user=DB_CONFIG["username"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )
    return conn


@app.route("/query1", methods=["GET"])
def query1():
    """Run a simple query and return the result."""
    start_time = time.time()
    with tracer.start_as_current_span("query1"):
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            query = "SELECT TOP 10 * FROM your_table"
            
            # Execute query
            cursor.execute(query)
            result = cursor.fetchall()

            # Update metrics
            db_query_counter.add(1, {"query_name": "query1"})

            # Return result
            return jsonify(result)
        except Exception as e:
            trace.get_current_span().record_exception(e)
            return jsonify({"error": str(e)}), 500
        finally:
            duration = time.time() - start_time
            print(f"Query executed in {duration:.2f} seconds")


@app.route("/query2", methods=["GET"])
def query2():
    """Run another query."""
    with tracer.start_as_current_span("query2"):
        try:
            conn = connect_to_sybase()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM another_table"
            
            # Execute query
            cursor.execute(query)
            result = cursor.fetchone()

            # Update metrics
            db_query_counter.add(1, {"query_name": "query2"})

            return jsonify({"count": result[0]})
        except Exception as e:
            trace.get_current_span().record_exception(e)
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
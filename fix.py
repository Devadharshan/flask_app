pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp psutil grpcio google-api-core


import time
import psutil
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider, ObservableGauge
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.measurement import Measurement

# Setup OpenTelemetry resources and metric provider
resource = Resource.create(attributes={"service.name": "sybase_app"})
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter
meter = metrics.get_meter_provider().get_meter("sybase_app")

# Define the callback functions
def get_cpu_usage(observer):
    """Get CPU usage percentage."""
    cpu_usage = psutil.Process().cpu_percent(interval=None)
    observer.observe(cpu_usage)

def get_memory_usage(observer):
    """Get memory usage in bytes."""
    memory_usage = psutil.Process().memory_info().rss
    observer.observe(memory_usage)

# Create Observable Metrics
meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    unit="percent",
    callbacks=[get_cpu_usage],
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS)",
    unit="bytes",
    callbacks=[get_memory_usage],
)

# Simulate workload
print("Metrics are being collected...")
while True:
    time.sleep(10)



----


import time
import psutil
import sybpydb
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider Setup
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer("sybase_app")

# Metrics Exporter Setup
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter for process-level metrics
meter = meter_provider.get_meter("sybase_app")

# Custom process-level metrics using ObservableGauges
def get_cpu_usage():
    return psutil.Process().cpu_percent(interval=None)

def get_memory_usage():
    return psutil.Process().memory_info().rss

# Registering Observable Gauges
process_cpu_usage = meter.create_observable_gauge(
    "process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[lambda result: result.observe(get_cpu_usage(), {})],
)

process_memory_usage = meter.create_observable_gauge(
    "process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[lambda result: result.observe(get_memory_usage(), {})],
)

# Sybase database functions
def connect_to_sybase(server, user, password, database):
    """
    Connect to Sybase database.
    """
    with tracer.start_as_current_span("sybase_connect"):
        try:
            conn = sybpydb.connect(server=server, user=user, password=password, database=database)
            print("Successfully connected to Sybase.")
            return conn
        except Exception as e:
            print(f"Failed to connect to Sybase: {e}")
            raise


def execute_query(connection, query):
    """
    Execute a query on the Sybase database.
    """
    with tracer.start_as_current_span("sybase_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            span.set_attribute("execution_time_ms", execution_time)


def run_application():
    # Configuration
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    # Connect to Sybase
    try:
        connection = connect_to_sybase(server, user, password, database)
    except Exception as e:
        print(f"Error during connection: {e}")
        return

    # Queries to execute
    queries = [
        "SELECT COUNT(*) FROM your_table",  # Replace with your actual query
        "SELECT TOP 10 * FROM your_table",  # Replace with your actual query
    ]

    # Run continuously
    while True:
        for query in queries:
            try:
                results = execute_query(connection, query)
                print(f"Results for query '{query}': {results}")
            except Exception as e:
                print(f"Error executing query '{query}': {e}")

        # Sleep for 10 seconds before the next iteration
        time.sleep(10)

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    run_application()




-----

import time
import psutil
import sybpydb
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider Setup
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer("sybase_app")

# Metrics Exporter Setup
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter for process-level metrics
meter = meter_provider.get_meter("sybase_app")

# Custom process-level metrics using ObservableGauges
def get_cpu_usage_callback(result):
    result.observe(psutil.Process().cpu_percent(interval=None), {})

def get_memory_usage_callback(result):
    result.observe(psutil.Process().memory_info().rss, {})

# Registering Observable Gauges with the proper callback
process_cpu_usage = meter.create_observable_gauge(
    "process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[get_cpu_usage_callback],
)

process_memory_usage = meter.create_observable_gauge(
    "process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[get_memory_usage_callback],
)

# Sybase database functions
def connect_to_sybase(server, user, password, database):
    """
    Connect to Sybase database.
    """
    with tracer.start_as_current_span("sybase_connect"):
        try:
            conn = sybpydb.connect(server=server, user=user, password=password, database=database)
            print("Successfully connected to Sybase.")
            return conn
        except Exception as e:
            print(f"Failed to connect to Sybase: {e}")
            raise


def execute_query(connection, query):
    """
    Execute a query on the Sybase database.
    """
    with tracer.start_as_current_span("sybase_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            span.set_attribute("execution_time_ms", execution_time)


def run_application():
    # Configuration
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    # Connect to Sybase
    try:
        connection = connect_to_sybase(server, user, password, database)
    except Exception as e:
        print(f"Error during connection: {e}")
        return

    # Queries to execute
    queries = [
        "SELECT COUNT(*) FROM your_table",  # Replace with your actual query
        "SELECT TOP 10 * FROM your_table",  # Replace with your actual query
    ]

    # Run continuously
    while True:
        for query in queries:
            try:
                results = execute_query(connection, query)
                print(f"Results for query '{query}': {results}")
            except Exception as e:
                print(f"Error executing query '{query}': {e}")

        # Sleep for 10 seconds before the next iteration
        time.sleep(10)

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    run_application()



------

import time
import psutil
import sybpydb
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider Setup
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer("sybase_app")

# Metrics Exporter Setup
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter for process-level metrics
meter = meter_provider.get_meter("sybase_app")

# Custom process-level metrics using ObservableGauges
def get_cpu_usage_callback():
    cpu_usage = psutil.Process().cpu_percent(interval=None)
    return [metrics.Measurement(cpu_usage, {})]

def get_memory_usage_callback():
    memory_usage = psutil.Process().memory_info().rss
    return [metrics.Measurement(memory_usage, {})]

# Registering Observable Gauges with the proper callback
process_cpu_usage = meter.create_observable_gauge(
    "process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[get_cpu_usage_callback],
)

process_memory_usage = meter.create_observable_gauge(
    "process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[get_memory_usage_callback],
)

# Sybase database functions
def connect_to_sybase(server, user, password, database):
    """
    Connect to Sybase database.
    """
    with tracer.start_as_current_span("sybase_connect"):
        try:
            conn = sybpydb.connect(server=server, user=user, password=password, database=database)
            print("Successfully connected to Sybase.")
            return conn
        except Exception as e:
            print(f"Failed to connect to Sybase: {e}")
            raise


def execute_query(connection, query):
    """
    Execute a query on the Sybase database.
    """
    with tracer.start_as_current_span("sybase_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            span.set_attribute("execution_time_ms", execution_time)


def run_application():
    # Configuration
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    # Connect to Sybase
    try:
        connection = connect_to_sybase(server, user, password, database)
    except Exception as e:
        print(f"Error during connection: {e}")
        return

    # Queries to execute
    queries = [
        "SELECT COUNT(*) FROM your_table",  # Replace with your actual query
        "SELECT TOP 10 * FROM your_table",  # Replace with your actual query
    ]

    # Run continuously
    while True:
        for query in queries:
            try:
                results = execute_query(connection, query)
                print(f"Results for query '{query}': {results}")
            except Exception as e:
                print(f"Error executing query '{query}': {e}")

        # Sleep for 10 seconds before the next iteration
        time.sleep(10)

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    run_application()




------


import time
import psutil
import sybpydb
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup OpenTelemetry resources
resource = Resource.create(attributes={"service.name": "sybase_app"})

# Tracer Provider Setup
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer("sybase_app")

# Metrics Exporter Setup
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Create a meter for process-level metrics
meter = meter_provider.get_meter("sybase_app")

# Custom process-level metrics using ObservableGauges
def get_cpu_usage_callback(meter):
    cpu_usage = psutil.Process().cpu_percent(interval=None)
    # Return a list of measurements with the CPU usage value
    return [metrics.Measurement(cpu_usage, {})]

def get_memory_usage_callback(meter):
    memory_usage = psutil.Process().memory_info().rss
    # Return a list of measurements with the memory usage value
    return [metrics.Measurement(memory_usage, {})]

# Registering Observable Gauges with the proper callback
process_cpu_usage = meter.create_observable_gauge(
    "process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[get_cpu_usage_callback],
)

process_memory_usage = meter.create_observable_gauge(
    "process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[get_memory_usage_callback],
)

# Sybase database functions
def connect_to_sybase(server, user, password, database):
    """
    Connect to Sybase database.
    """
    with tracer.start_as_current_span("sybase_connect"):
        try:
            conn = sybpydb.connect(server=server, user=user, password=password, database=database)
            print("Successfully connected to Sybase.")
            return conn
        except Exception as e:
            print(f"Failed to connect to Sybase: {e}")
            raise


def execute_query(connection, query):
    """
    Execute a query on the Sybase database.
    """
    with tracer.start_as_current_span("sybase_query") as span:
        start_time = time.time()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            span.set_attribute("query", query)
            span.set_attribute("query.success", True)
            return results
        except Exception as e:
            span.set_attribute("query.success", False)
            span.record_exception(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            span.set_attribute("execution_time_ms", execution_time)


def run_application():
    # Configuration
    server = "YOUR_SERVER"
    user = "YOUR_USER"
    password = "YOUR_PASSWORD"
    database = "YOUR_DATABASE"

    # Connect to Sybase
    try:
        connection = connect_to_sybase(server, user, password, database)
    except Exception as e:
        print(f"Error during connection: {e}")
        return

    # Queries to execute
    queries = [
        "SELECT COUNT(*) FROM your_table",  # Replace with your actual query
        "SELECT TOP 10 * FROM your_table",  # Replace with your actual query
    ]

    # Run continuously
    while True:
        for query in queries:
            try:
                results = execute_query(connection, query)
                print(f"Results for query '{query}': {results}")
            except Exception as e:
                print(f"Error executing query '{query}': {e}")

        # Sleep for 10 seconds before the next iteration
        time.sleep(10)

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    run_application()



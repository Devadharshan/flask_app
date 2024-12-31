import time
import os
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import OTLPMetricExporter, PeriodicExportingMetricReader

# Import logger and tracer from the lib folder
from lib.logger import log
from lib.tracer import tracer

# Configure Metrics
metric_exporter = OTLPMetricExporter(endpoint="your-otel-collector-endpoint:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("test_python_app")

# Fixed Observable Gauges
def collect_cpu_usage():
    try:
        # Simulate CPU usage percentage
        cpu_usage = os.getloadavg()[0] * 10  # Example logic; replace with actual CPU metrics
        return [(cpu_usage, {})]
    except Exception as e:
        log.error(f"Failed to collect CPU usage: {e}")
        return []

def collect_memory_usage():
    try:
        # Simulate memory usage in MB
        memory_usage = 512  # Replace with actual memory usage logic
        return [(memory_usage, {})]
    except Exception as e:
        log.error(f"Failed to collect Memory usage: {e}")
        return []

cpu_usage_gauge = meter.create_observable_gauge(
    name="app_cpu_usage",
    description="CPU usage of the application",
    callback=collect_cpu_usage,
)

memory_usage_gauge = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Memory usage of the application",
    callback=collect_memory_usage,
)

# Example Histogram for DB Query Duration
query_duration_histogram = meter.create_histogram(
    name="app_db_query_duration",
    unit="seconds",
    description="Duration of database queries",
)

# Main Application Logic
def execute_database_query():
    with tracer.start_as_current_span("execute_database_query"):
        log.info("Executing database query...")
        start_time = time.time()
        time.sleep(1.5)  # Simulating a query taking 1.5 seconds
        duration = time.time() - start_time
        query_duration_histogram.record(duration)
        log.info(f"Database query completed in {duration:.2f} seconds")

def main():
    while True:
        log.info("Application is running...")
        execute_database_query()
        time.sleep(10)

if __name__ == "__main__":
    main()

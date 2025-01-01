import os
import subprocess
import time
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider, Observation
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.metrics import CallbackOptions

# Global configuration
OTEL_EXPORTER_ENDPOINT = "http://localhost:4317"  # Update if your Collector is on another host
COLLECT_METRICS_INTERVAL = 5  # Collect metrics every 5 seconds

# Resource definition
resource = Resource.create({"service.name": "job-monitoring-app"})

# Metric and tracing providers
metric_exporter = OTLPMetricExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=COLLECT_METRICS_INTERVAL * 1000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

tracer_provider = TracerProvider(resource=resource)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True))
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

# Create meter and tracer
meter = metrics.get_meter("job-monitoring-metrics", version="1.0.0")
tracer = trace.get_tracer("job-monitoring-tracer", version="1.0.0")


# Helper functions to collect CPU and memory usage
def get_cpu_usage():
    try:
        if os.name == "posix":  # Linux/Mac
            load = os.getloadavg()
            cpu_usage = (load[0] / os.cpu_count()) * 100
            return cpu_usage
        else:  # Windows
            result = subprocess.run(["wmic", "cpu", "get", "loadpercentage"], capture_output=True, text=True)
            return float(result.stdout.split("\n")[1].strip())
    except Exception as e:
        print(f"Error fetching CPU usage: {e}")
        return 0.0


def get_memory_usage():
    try:
        if os.name == "posix":  # Linux/Mac
            meminfo = dict((i.split()[0].rstrip(":"), int(i.split()[1])) for i in open("/proc/meminfo").readlines())
            total_memory = meminfo["MemTotal"]
            available_memory = meminfo["MemAvailable"]
            used_memory = total_memory - available_memory
            return (used_memory / total_memory) * 100
        else:  # Windows
            result = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory"], capture_output=True, text=True)
            free_memory = int(result.stdout.split("\n")[1].strip()) * 1024
            total_memory = int(subprocess.run(["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"], capture_output=True, text=True).stdout.split("\n")[1].strip())
            used_memory = total_memory - free_memory
            return (used_memory / total_memory) * 100
    except Exception as e:
        print(f"Error fetching memory usage: {e}")
        return 0.0


# Metric registration
def register_metrics():
    def cpu_usage_callback(options: CallbackOptions):
        return [Observation(value=get_cpu_usage(), attributes={})]

    def memory_usage_callback(options: CallbackOptions):
        return [Observation(value=get_memory_usage(), attributes={})]

    meter.create_observable_gauge(
        name="system.cpu.usage_percent",
        description="Current CPU usage percentage",
        unit="%",
        callbacks=[cpu_usage_callback],
    )

    meter.create_observable_gauge(
        name="system.memory.usage_percent",
        description="Current Memory usage percentage",
        unit="%",
        callbacks=[memory_usage_callback],
    )


# Simulate job monitoring
def monitor_jobs(job_patterns):
    with tracer.start_as_current_span("monitor_jobs") as span:
        for pattern in job_patterns:
            # Simulate checking job status
            span.add_event(f"Monitoring pattern: {pattern}")
            job_name = f"job_{pattern}"
            status = "success" if int(time.time()) % 2 == 0 else "failure"
            duration = round((time.time() % 10) * 100, 2)  # Random duration

            # Log the status and duration
            print(f"Job: {job_name}, Status: {status}, Duration: {duration}ms")

            # Add custom attributes to span
            span.set_attribute("job.name", job_name)
            span.set_attribute("job.status", status)
            span.set_attribute("job.duration_ms", duration)


if __name__ == "__main__":
    # Register CPU and memory metrics
    register_metrics()

    # Define job patterns to monitor
    job_patterns = ["pattern1", "pattern2", "pattern3"]

    # Monitor jobs and export metrics/traces
    while True:
        monitor_jobs(job_patterns)
        time.sleep(COLLECT_METRICS_INTERVAL)
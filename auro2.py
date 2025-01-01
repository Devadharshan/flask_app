from time import sleep, time
from random import choice, randint
import os
import subprocess
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Set up OpenTelemetry resources
resource = Resource.create({"service.name": "autosys-job-monitor"})

# Initialize Tracer
tracer_provider = TracerProvider(resource=resource)
span_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

# Initialize Meter
metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

# Create Tracer and Meter
tracer = tracer_provider.get_tracer("autosys-job-monitor")
meter = meter_provider.get_meter("autosys-job-monitor")

# Create metrics
job_status_counter = meter.create_counter(
    "autosys_job_status",
    description="Counts the status of Autosys jobs",
    unit="1",
)

job_duration_histogram = meter.create_histogram(
    "autosys_job_duration",
    description="Tracks the duration of Autosys jobs",
    unit="ms",
)

cpu_usage_gauge = meter.create_observable_gauge(
    "system_cpu_usage",
    callbacks=[
        lambda: [{"value": get_cpu_usage(), "attributes": {}}],
    ],
    description="Tracks system CPU usage percentage",
    unit="%",
)

memory_usage_gauge = meter.create_observable_gauge(
    "system_memory_usage",
    callbacks=[
        lambda: [{"value": get_memory_usage(), "attributes": {}}],
    ],
    description="Tracks system memory usage percentage",
    unit="%",
)

# Helper to get CPU usage (using system commands)
def get_cpu_usage():
    try:
        if os.name == "posix":  # Linux/Mac
            load = os.getloadavg()
            return (load[0] / os.cpu_count()) * 100
        else:  # Windows
            result = subprocess.run(["wmic", "cpu", "get", "loadpercentage"], capture_output=True, text=True)
            return float(result.stdout.split("\n")[1].strip())
    except Exception as e:
        print(f"Error fetching CPU usage: {e}")
        return 0.0

# Helper to get Memory usage (using system commands)
def get_memory_usage():
    try:
        if os.name == "posix":  # Linux/Mac
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            total = int(lines[0].split()[1])
            free = int(lines[1].split()[1])
            return ((total - free) / total) * 100
        else:  # Windows
            result = subprocess.run(["wmic", "os", "get", "freephysicalmemory"], capture_output=True, text=True)
            free_mem = int(result.stdout.split("\n")[1].strip())
            total_mem = int(subprocess.run(["wmic", "computersystem", "get", "totalphysicalmemory"], capture_output=True, text=True).stdout.split("\n")[1].strip())
            return ((total_mem - free_mem) / total_mem) * 100
    except Exception as e:
        print(f"Error fetching memory usage: {e}")
        return 0.0

# Simulate checking Autosys job status (replace with real logic)
def check_job_status(job_name):
    statuses = ["SUCCESS", "FAILURE", "RUNNING", "PENDING"]
    status = choice(statuses)
    duration = randint(1000, 10000)  # Simulate job duration in ms
    return status, duration

# Monitor multiple job patterns
def monitor_jobs(job_patterns):
    for job_pattern in job_patterns:
        with tracer.start_as_current_span(f"monitor_{job_pattern}"):
            print(f"Checking jobs for pattern: {job_pattern}")

            for i in range(1, 4):  # Simulate 3 jobs per pattern
                job_name = f"{job_pattern}_job_{i}"
                status, duration = check_job_status(job_name)

                # Record metrics
                job_status_counter.add(1, {"job_name": job_name, "status": status})
                job_duration_histogram.record(duration, {"job_name": job_name, "status": status})

                print(f"Job {job_name}: Status={status}, Duration={duration}ms")

def main():
    job_patterns = ["Job_A_*", "Job_B_*", "Job_C_*"]
    while True:
        print("Monitoring Autosys jobs and system metrics...")
        monitor_jobs(job_patterns)
        sleep(10)

if __name__ == "__main__":
    main()
from time import sleep
from random import choice, randint
import os
import subprocess
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

# Set up OpenTelemetry resources
resource = Resource.create({"service.name": "autosys-job-monitor"})

# Initialize Tracer
tracer_provider = TracerProvider(resource=resource)
span_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
tracer = tracer_provider.get_tracer("autosys-job-monitor")

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
        for i in range(1, 4):  # Simulate 3 jobs per pattern
            job_name = f"{job_pattern}_job_{i}"
            status, duration = check_job_status(job_name)

            # Start a span for each job
            with tracer.start_as_current_span(
                f"job_{job_name}",
                kind=SpanKind.INTERNAL,
                attributes={
                    "job.name": job_name,
                    "job.pattern": job_pattern,
                    "job.status": status,
                    "job.duration_ms": duration,
                    "system.cpu.usage_percent": get_cpu_usage(),
                    "system.memory.usage_percent": get_memory_usage(),
                },
            ) as span:
                print(f"Monitoring {job_name}: Status={status}, Duration={duration}ms")
                sleep(duration / 1000.0)  # Simulate job duration

def main():
    job_patterns = ["Job_A_*", "Job_B_*", "Job_C_*"]
    while True:
        print("Monitoring Autosys jobs...")
        monitor_jobs(job_patterns)
        sleep(10)  # Wait before the next monitoring cycle

if __name__ == "__main__":
    main()
import subprocess
import time
import psutil  # For process and system-level metrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider, Counter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.metrics import ObservableGauge

# Initialize OpenTelemetry Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export trace data to OTEL collector using OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="your-otel-collector-endpoint:4317")
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Initialize OpenTelemetry Meter for metrics
meter_provider = MeterProvider()
reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10000)
meter_provider.add_metric_reader(reader)
meter = meter_provider.get_meter(__name__)

# Create custom metrics for system-level data
cpu_usage_gauge = meter.create_observable_gauge(
    "system.cpu.usage", description="CPU usage as percentage", callback=lambda: [psutil.cpu_percent()]
)

memory_usage_gauge = meter.create_observable_gauge(
    "system.memory.usage", description="Memory usage as percentage", callback=lambda: [psutil.virtual_memory().percent]
)

disk_usage_gauge = meter.create_observable_gauge(
    "system.disk.usage", description="Disk usage as percentage", callback=lambda: [psutil.disk_usage('/').percent]
)

network_usage_gauge = meter.create_observable_gauge(
    "system.network.bytes_sent", description="Bytes sent by the system", callback=lambda: [psutil.net_io_counters().bytes_sent]
)

# Function to check Autosys job status
def check_autosys_job_status(job_name):
    """Check the status of an Autosys job."""
    command = f"autorep -j {job_name}"  # Change the command according to your environment
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error checking job {job_name}: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

# Monitor Autosys jobs and print status
def monitor_jobs():
    job_names = ['job1', 'job2', 'job3']  # Add your job names here
    while True:
        for job_name in job_names:
            with tracer.start_as_current_span(f"Checking {job_name}"):
                status = check_autosys_job_status(job_name)
                print(f"Job {job_name} status:\n{status}")
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    print("Starting Autosys job status monitor...")
    monitor_jobs()

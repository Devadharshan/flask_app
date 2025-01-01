import subprocess
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.instrumentation.auto_instrumentation import AutoInstrumentation

# Initialize OpenTelemetry Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export trace data to OTEL collector using OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="your-otel-collector-endpoint:4317")
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Initialize OpenTelemetry Metrics
meter_provider = MeterProvider()
reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10000)
meter_provider.add_metric_reader(reader)

# Auto-instrumentation (sets up process-level metrics collection automatically)
AutoInstrumentation()

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

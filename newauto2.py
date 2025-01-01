import logging
import os
import time
import resource  # For memory usage stats
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.auto_instrumentation import AutoInstrumented
from lib.logger import logger  # Assuming your logger.py is already set up
from lib.tracer import tracer  # Assuming your tracer.py is already set up with the OTLP endpoint

# Auto-instrumentation for libraries (if needed)
AutoInstrumented()

# Initialize logger
logger = logging.getLogger(__name__)

# Custom tracer provider setup (if you don't want to use AutoInstrumented for traces)
resource = Resource.create(attributes={"service.name": "process-stats-app"})
trace.set_tracer_provider(TracerProvider(resource=resource))
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Get a tracer
tracer = trace.get_tracer(__name__)

# Function to collect process stats
def collect_process_stats():
    # Get the current process ID
    pid = os.getpid()

    # Get memory usage (in bytes)
    memory_usage_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024  # Convert from KB to bytes

    # Get CPU usage time (user + system time in seconds)
    cpu_time_user = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    cpu_time_system = resource.getrusage(resource.RUSAGE_SELF).ru_stime
    cpu_time_total = cpu_time_user + cpu_time_system

    stats = {
        "pid": pid,
        "memory_usage_rss": memory_usage_rss,
        "cpu_time_total": cpu_time_total,
    }
    return stats

# Main logic
def main():
    logger.info("Starting process stats collection app")

    while True:
        try:
            stats = collect_process_stats()

            # Log stats
            logger.info(f"Process stats: {stats}")

            # Create a span for tracing
            with tracer.start_as_current_span("process-stats") as span:
                span.set_attribute("process.pid", stats["pid"])
                span.set_attribute("memory.usage.rss", stats["memory_usage_rss"])
                span.set_attribute("cpu.time.total", stats["cpu_time_total"])

            # Add a sleep to simulate periodic data collection
            time.sleep(5)

        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    main()

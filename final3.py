# Custom process-level metrics for older versions
def get_cpu_usage_callback():
    """Callback to report CPU usage."""
    cpu_usage = psutil.Process().cpu_percent(interval=None)
    return [(cpu_usage, {})]

def get_memory_usage_callback():
    """Callback to report memory usage."""
    memory_usage = psutil.Process().memory_info().rss
    return [(memory_usage, {})]

meter.create_observable_gauge(
    name="process_cpu_usage_percent",
    description="CPU usage percentage of the process",
    callbacks=[get_cpu_usage_callback],
)

meter.create_observable_gauge(
    name="process_memory_usage_bytes",
    description="Memory usage of the process in bytes (RSS - Resident Set Size)",
    callbacks=[get_memory_usage_callback],
)
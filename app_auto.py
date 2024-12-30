import logging

def get_logger(name: str):
    """
    Returns a configured logger instance.
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not log.handlers:
        log.addHandler(console_handler)

    return log



from lib.logger import get_logger
from lib.traces import tracer_init
import sybpydb

# Collector endpoint
OTEL_COLLECTOR_ENDPOINT = "http://<your-collector-endpoint>:5608"

# Initialize Logger
log = get_logger("SybaseAppLogger")

# Initialize Tracer
tracer = tracer_init("SybaseApp", OTEL_COLLECTOR_ENDPOINT)

def connect_and_query():
    """
    Connects to the Sybase database and executes a sample query.
    """
    log.info("Starting the database connection and query execution.")

    try:
        # Use File System Native Authentication (no username/password)
        connection = sybpydb.connect(
            server="your_sybase_server",
            database="your_database",
        )

        cursor = connection.cursor()

        with tracer.start_as_current_span(
            "db_query_execution",
            attributes={"db.system": "sybase", "db.name": "your_database"}
        ) as span:
            # Execute a test query
            query = "SELECT COUNT(*) FROM your_table"
            log.info(f"Executing query: {query}")
            cursor.execute(query)
            result = cursor.fetchone()

            log.info(f"Query Result: {result[0]}")
            span.set_attribute("db.query.result_count", result[0])

        cursor.close()
        connection.close()
        log.info("Database connection closed.")

    except Exception as e:
        log.error(f"Database error: {e}")

if __name__ == "__main__":
    log.info("Starting the application.")
    connect_and_query()
    log.info("Application finished.")
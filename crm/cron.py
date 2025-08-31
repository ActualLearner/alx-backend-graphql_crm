from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"


def log_crm_heartbeat():
    """
    A cron job function to log a heartbeat message.
    It appends a timestamped message to a log file and optionally
    queries the GraphQL endpoint to ensure it is responsive.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    graphql_status = ""
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("query { hello }")
        result = client.execute(query)

        if result and result.get("hello"):
            graphql_status = "and GraphQL endpoint is responsive"
        else:
            graphql_status = "but GraphQL query returned no data"

    except Exception as e:
        graphql_status = f"but GraphQL endpoint FAILED to respond. Error: {e}"

    with open(LOG_FILE, "a") as f:
        log_message = f"{timestamp} CRM is alive {graphql_status}\n"
        f.write(log_message)

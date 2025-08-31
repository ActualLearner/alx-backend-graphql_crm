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


LOG_FILE_LOW_STOCK = "/tmp/low_stock_updates_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"


def update_low_stock():
    """
    Executes the UpdateLowStockProducts GraphQL mutation to restock
    products with low inventory and logs the result.
    """
    # Define the GraphQL mutation string that we will send.
    # We ask for the updated product's name and new stock level.
    mutation_string = gql("""
        mutation RestockProducts {
          updateLowStockProducts {
            message
            updatedProducts {
              name
              stock
            }
          }
        }
    """)

    try:
        # Set up a synchronous GraphQL client
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Execute the mutation
        result = client.execute(mutation_string)

        # Log the results to the file
        with open(LOG_FILE_LOW_STOCK, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Safely access the nested data from the result
            mutation_result = result.get("updateLowStockProducts", {})
            message = mutation_result.get("message", "No message returned.")
            updated_products = mutation_result.get("updatedProducts", [])

            f.write(f"[{timestamp}] Executing low stock update job.\n")
            f.write(f"  - API Response: {message}\n")

            if updated_products:
                f.write("  - Updated Products:\n")
                for product in updated_products:
                    name = product.get("name", "N/A")
                    stock = product.get("stock", "N/A")
                    f.write(f"    - {name}: New stock is {stock}\n")

    except Exception as e:
        # Log any errors that occur during the process
        with open(LOG_FILE_LOW_STOCK, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"[{timestamp}] ERROR: Failed to update low stock products. Error: {e}\n"
            )

from celery import shared_task
from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"


@shared_task
def generate_crm_report():
    """
    A Celery task that queries GraphQL for CRM stats and logs a report.
    """
    # This query uses the new aggregation fields we added to the schema
    query = gql("""
        query CrmReportQuery {
          totalCustomers
          totalOrders
          totalRevenue
        }
    """)

    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(query)

        # Safely get results from the query
        customers = result.get("totalCustomers", "N/A")
        orders = result.get("totalOrders", "N/A")
        revenue = result.get("totalRevenue", "N/A")

        # Format the log message as specified
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue.\n"

        # Append the report to the log file
        with open(LOG_FILE, "a") as f:
            f.write(log_message)

    except Exception as e:
        # Log any errors encountered during the task
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{timestamp} - ERROR generating CRM report: {e}\n"
        with open(LOG_FILE, "a") as f:
            f.write(error_message)

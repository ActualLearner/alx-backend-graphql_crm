#!/bin/python3

import asyncio
from datetime import datetime, timedelta, timezone
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

# CONFIGURATION
LOG_FILE = "p/tmp/order_reminders_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"


# MAIN LOGIC
async def main():
    """
    Connects to the GraphQL endpoint, fetches pending orders from the last 7 days,
    and logs the details to a file.
    """

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    date_filter_string = seven_days_ago.isoformat()

    query = gql("""
        query getRecentPendingOrders($since: DateTime!) {
            orders(orderDate_Gte: $since, status: "PENDING") {
            id
            customer {
                email
            }
        }
        }
    """)

    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
    async with Client(transport=transport, fetch_schema_from_transport=True) as client:
        try:
            result = await client.execute(
                query, variable_values={"since": date_filter_string}
            )

            # Log to file
            with open(LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if result and result["orders"]:
                    num_orders = len(result["orders"])
                    f.write(
                        f"[{timestamp}] Found {num_orders} pending orders to process.\n"
                    )

                    # write each order
                    for order in result["orders"]:
                        order_id = order["id"]
                        customer_email = order["customer"]["email"]
                        log_line = f" - Order Id: {order_id}, Customer email: {customer_email}\n"
                        f.write(log_line)
                else:
                    f.write(
                        f"[{timestamp}] No pending orders found in the last 7 days.\n"
                    )

            print("Order reminders processed!")

        except Exception as e:
            with open(LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] ERROR: An error occurred - {e}\n")

            print(f"An error occurred. Check the log at {LOG_FILE} for details.")


if __name__ == "__main__":
    asyncio.run(main())

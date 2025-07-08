import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up GraphQL client
transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=False)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range for the last 7 days
now = datetime.datetime.now()
seven_days_ago = now - datetime.timedelta(days=7)

# GraphQL query for orders in the last 7 days
query = gql('''
query getRecentOrders($dateFrom: DateTime!) {
  allOrders(orderBy: ["order_date"]) {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
''')

params = {"dateFrom": seven_days_ago.isoformat()}

# Execute query
result = client.execute(query, variable_values=params)

# Filter orders by order_date >= seven_days_ago
orders = [edge['node'] for edge in result['allOrders']['edges'] if edge['node']['orderDate'] >= seven_days_ago.isoformat()]

with open('/tmp/order_reminders_log.txt', 'a') as log_file:
    for order in orders:
        log_file.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n")

print("Order reminders processed!") 
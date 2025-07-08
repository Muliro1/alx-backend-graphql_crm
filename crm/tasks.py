from celery import shared_task
import requests
import datetime

@shared_task
def generate_crm_report():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = '''
    query {
      allCustomers {
        totalCount
      }
      allOrders {
        totalCount
        edges {
          node {
            totalAmount
          }
        }
      }
    }
    '''
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            timeout=10
        )
        data = response.json().get('data', {})
        total_customers = data.get('allCustomers', {}).get('totalCount', 0)
        all_orders = data.get('allOrders', {})
        total_orders = all_orders.get('totalCount', 0)
        total_revenue = 0
        for edge in all_orders.get('edges', []):
            node = edge.get('node', {})
            try:
                total_revenue += float(node.get('totalAmount', 0))
            except Exception:
                pass
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(f"{now} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n")
    except Exception as e:
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(f"{now} - ERROR: {e}\n") 
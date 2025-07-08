import datetime
import requests

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{now} CRM is alive"
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(message + '\n')
    # Optionally, check GraphQL hello field
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'},
            timeout=5
        )
        if response.ok and response.json().get('data', {}).get('hello') == 'Hello, GraphQL!':
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{now} GraphQL hello OK\n")
        else:
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{now} GraphQL hello FAILED\n")
    except Exception as e:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(f"{now} GraphQL hello ERROR: {e}\n") 

def update_low_stock():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mutation = '''
    mutation {
      updateLowStockProducts {
        updatedProducts {
          name
          stock
        }
        message
      }
    }
    '''
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            timeout=10
        )
        data = response.json()
        updates = data.get('data', {}).get('updateLowStockProducts', {})
        products = updates.get('updatedProducts', [])
        message = updates.get('message', 'No message')
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"{now} - {message}\n")
            for product in products:
                f.write(f"{now} - {product['name']} restocked to {product['stock']}\n")
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"{now} - ERROR: {e}\n") 
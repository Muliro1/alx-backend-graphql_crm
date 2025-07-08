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
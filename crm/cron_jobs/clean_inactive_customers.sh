#!/bin/bash

# Run Django shell command to delete inactive customers and log the result
deleted_count=$(python3 manage.py shell -c "import datetime; from django.utils import timezone; from models import Customer; from django.db.models import Count; one_year_ago = timezone.now() - datetime.timedelta(days=365); qs = Customer.objects.annotate(order_count=Count('orders')).filter(order_count=0, created_at__lt=one_year_ago); count = qs.count(); qs.delete(); print(count)")

echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt 
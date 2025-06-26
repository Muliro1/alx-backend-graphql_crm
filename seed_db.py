import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
    django.setup()

setup_django()

from crm.models import Customer, Product, Order
from django.utils import timezone

# Clear existing data
Order.objects.all().delete()
Product.objects.all().delete()
Customer.objects.all().delete()

# Create customers
alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
bob = Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")
carol = Customer.objects.create(name="Carol", email="carol@example.com")

# Create products
laptop = Product.objects.create(name="Laptop", price=999.99, stock=10)
phone = Product.objects.create(name="Phone", price=499.99, stock=25)
tablet = Product.objects.create(name="Tablet", price=299.99, stock=5)

# Create orders
order1 = Order.objects.create(customer=alice, order_date=timezone.now(), total_amount=laptop.price + phone.price)
order1.products.set([laptop, phone])

order2 = Order.objects.create(customer=bob, order_date=timezone.now(), total_amount=tablet.price)
order2.products.set([tablet])

print("Seed data created!")

import graphene
from .models import Customer, Product, Order
from graphene_django import DjangoObjectType
import re
from django.core.exceptions import ValidationError
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def validate_phone(self, phone):
        if not phone:
            return True
        pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
        return re.match(pattern, phone)

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="Email already exists.")
        if phone and not self.validate_phone(phone):
            return CreateCustomer(success=False, message="Invalid phone format.")
        customer = Customer(name=name, email=email, phone=phone)
        try:
            customer.full_clean()
            customer.save()
        except ValidationError as e:
            return CreateCustomer(success=False, message=str(e))
        return CreateCustomer(customer=customer, success=True, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    created_customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True
        pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
        return re.match(pattern, phone)

    @staticmethod
    def mutate(root, info, customers):
        created = []
        errors = []
        for idx, data in enumerate(customers):
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            if Customer.objects.filter(email=email).exists():
                errors.append(f"[{idx}] Email already exists: {email}")
                continue
            if phone and not BulkCreateCustomers.validate_phone(phone):
                errors.append(f"[{idx}] Invalid phone format: {phone}")
                continue
            customer = Customer(name=name, email=email, phone=phone)
            try:
                customer.full_clean()
                customer.save()
                created.append(customer)
            except ValidationError as e:
                errors.append(f"[{idx}] {str(e)}")
        return BulkCreateCustomers(created_customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(success=False, message="Price must be positive.")
        if stock is not None and stock < 0:
            return CreateProduct(success=False, message="Stock cannot be negative.")
        product = Product(name=name, price=price, stock=stock if stock is not None else 0)
        try:
            product.full_clean()
            product.save()
        except ValidationError as e:
            return CreateProduct(success=False, message=str(e))
        return CreateProduct(product=product, success=True, message="Product created successfully.")

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, customer_id, product_ids, order_date=None):
        # Validate customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(success=False, message="Invalid customer ID.")
        # Validate products
        if not product_ids or len(product_ids) == 0:
            return CreateOrder(success=False, message="At least one product must be selected.")
        products = []
        total = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total += float(product.price)
            except Product.DoesNotExist:
                return CreateOrder(success=False, message=f"Invalid product ID: {pid}")
        # Create order
        order = Order(customer=customer, order_date=order_date or None, total_amount=total)
        order.save()
        order.products.set(products)
        return CreateOrder(order=order, success=True, message="Order created successfully.")

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)
        msg = f"{len(updated)} products restocked."
        return UpdateLowStockProducts(updated_products=updated, message=msg)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerNode, order_by=graphene.List(graphene.String))
    all_products = DjangoFilterConnectionField(ProductNode, order_by=graphene.List(graphene.String))
    all_orders = DjangoFilterConnectionField(OrderNode, order_by=graphene.List(graphene.String))

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

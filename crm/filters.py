import django_filters
from .models import Customer, Product, Order
from django.db.models import Q

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')

    def filter_phone_pattern(self, queryset, name, value):
        # Example: value = '+1' to match numbers starting with +1
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at', 'phone']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price = django_filters.RangeFilter(field_name='price')
    stock = django_filters.RangeFilter(field_name='stock')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

class OrderFilter(django_filters.FilterSet):
    total_amount = django_filters.RangeFilter(field_name='total_amount')
    order_date = django_filters.DateFromToRangeFilter(field_name='order_date')
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = django_filters.NumberFilter(field_name='products__id')

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date', 'customer_name', 'product_name', 'product_id']

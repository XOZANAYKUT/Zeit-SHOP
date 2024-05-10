from django.shortcuts import render
from .models import Product

def all_products(request):
    """A view to show all products, including sorting and search queries"""
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'sort': sort,
        'direction': direction,
    }
    return render(request, 'products/products.html', context)
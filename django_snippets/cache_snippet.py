from django.core.cache import cache
from django.shortcuts import render
from .models import Order

def recent_orders_view(request, user_id):
    cache_key = f'recent_orders_user_{user_id}'
    orders = cache.get(cache_key)
    if orders is None:
        orders = list(Order.objects.filter(user_id=user_id).order_by('-created_at')[:50].values('id','created_at','total'))
        cache.set(cache_key, orders, timeout=90)
    return render(request, 'orders/list.html', {'orders': orders})

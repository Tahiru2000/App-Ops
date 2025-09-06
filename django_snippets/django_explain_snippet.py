# django_explain_snippet.py
from myapp.models import Order

user_id = 42
qs = Order.objects.filter(user_id=user_id).order_by('-created_at')[:50]

print("SQL:\n", qs.query)
print("\nQuery plan (EXPLAIN):")
print(qs.explain(analyze=False))

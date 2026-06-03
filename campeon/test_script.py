import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campeon.settings")
django.setup()

from products.models import Coupon
from django.utils import timezone
now = timezone.now().date()

coupons = Coupon.objects.all()
for c in coupons:
    print(f"Coupon: {c.code}, is_active: {c.is_active}, start: {c.start_date}, end: {c.end_date}, now: {now}, is_valid: {c.is_valid()}")

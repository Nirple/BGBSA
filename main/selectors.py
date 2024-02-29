from django.contrib.auth.models import User
from django.db.models import QuerySet

from main.models import Listing


def list_user_active_selling(user: User) -> QuerySet:
    return user.listings.filter(is_sold=False)


def for_sale() -> int:
    return Listing.objects.filter(is_sold=False)

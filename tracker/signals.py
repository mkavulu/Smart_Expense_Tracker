from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category

DEFAULT_EXPENSE_CATEGORIES = [
    "Utilities",
    "Rent",
    "Insurance",
    "Housing",
    "Debt",
    "Clothing",
    "Savings",
    "Gifting",
    "Medical",
    "Miscellaneous",
]

DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Investments",
    "Bonus",
    "Business",
    "Other Income",
]

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        # Seed expense categories
        for name in DEFAULT_EXPENSE_CATEGORIES:
            Category.objects.get_or_create(
                user=instance,
                name=name,
                type="expense"
            )
        # Seed income categories
        for name in DEFAULT_INCOME_CATEGORIES:
            Category.objects.get_or_create(
                user=instance,
                name=name,
                type="income"
            )

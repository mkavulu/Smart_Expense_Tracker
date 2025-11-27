from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import Category

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

class Command(BaseCommand):
    help = "Seed default categories for all existing users"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            for name in DEFAULT_EXPENSE_CATEGORIES:
                Category.objects.get_or_create(user=user, name=name, type="expense")
            for name in DEFAULT_INCOME_CATEGORIES:
                Category.objects.get_or_create(user=user, name=name, type="income")
        self.stdout.write(self.style.SUCCESS("Default categories seeded for all users"))

from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Category model — user-specific, can be 'income' or 'expense'.
    """
    TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ("user", "name", "type")
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    """
    Transaction model with receipt upload.
    """
    TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    # Receipt image
    receipt = models.ImageField(upload_to="receipts/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user} {self.type} {self.amount} {self.date}"


class Budget(models.Model):
    """
    Monthly budget per category.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # store first day of each month

    class Meta:
        unique_together = ("user", "category", "month")

    def __str__(self):
        return f"{self.user} - {self.category} - {self.month}: {self.amount}"

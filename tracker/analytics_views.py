from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from .models import Transaction, Category
from datetime import date


class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        # Filter current month
        qs = Transaction.objects.filter(
            user=user,
            date__year=today.year,
            date__month=today.month
        )

        income_total = qs.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
        expense_total = qs.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0
        transaction_count = qs.count()

        return Response({
            "income_total": income_total,
            "expense_total": expense_total,
            "net": income_total - expense_total,
            "transaction_count": transaction_count,
        })


class MonthlyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        # For consistency, return the same fields (your React merges them)
        qs = Transaction.objects.filter(
            user=user,
            date__year=today.year,
            date__month=today.month
        )

        income_total = qs.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
        expense_total = qs.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "income_total": income_total,
            "expense_total": expense_total,
            "net": income_total - expense_total
        })

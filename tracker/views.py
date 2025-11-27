from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from .models import Transaction, Category, Budget
from .serializers import (
    TransactionSerializer,
    RegisterSerializer,
    CategorySerializer,
    BudgetSerializer,
)
from .permissions import IsOwnerOrReadOnly


# ---------------------------
# User Registration
# ---------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# ---------------------------
# Transactions CRUD
# ---------------------------
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)

        # Optional filters
        ttype = self.request.query_params.get("type")
        category_name = self.request.query_params.get("category")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if ttype:
            qs = qs.filter(type=ttype)
        if category_name:
            qs = qs.filter(category__name__iexact=category_name)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------
# Category CRUD
# ---------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------
# Budget CRUD
# ---------------------------
class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------
# Analytics: Monthly Summary
# ---------------------------
class MonthlySummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        qs = Transaction.objects.filter(user=request.user)

        # Filter by specific month
        if year and month:
            try:
                start = datetime(year=int(year), month=int(month), day=1).date()
                end = (start + relativedelta(months=1))
                qs = qs.filter(date__gte=start, date__lt=end)
            except ValueError:
                return Response({"detail": "Invalid year/month"}, status=400)

        totals = qs.values("type").annotate(total=Sum("amount"))
        income_total = sum(i["total"] for i in totals if i["type"] == "income") or 0
        expense_total = sum(i["total"] for i in totals if i["type"] == "expense") or 0

        expense_by_category = (
            qs.filter(type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        # Monthly series only when not filtering by a specific month
        monthly_series = {}
        if not (year and month):
            monthly = (
                qs.annotate(month=TruncMonth("date"))
                .values("month", "type")
                .annotate(total=Sum("amount"))
                .order_by("month")
            )

            for row in monthly:
                mon = row["month"].strftime("%Y-%m")
                typ = row["type"]
                monthly_series.setdefault(mon, {"income": 0, "expense": 0})
                monthly_series[mon][typ] = float(row["total"] or 0)

        return Response({
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "net": float(income_total - expense_total),
            "expense_by_category": [
                {"category": r["category__name"], "total": float(r["total"])}
                for r in expense_by_category
            ],
            "monthly_series": monthly_series,
        })


# ---------------------------
# Analytics: Category Totals
# ---------------------------
class CategoryAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)

        ttype = request.query_params.get("type")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if ttype:
            qs = qs.filter(type=ttype)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        data = (
            qs.values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        formatted = [
            {
                "category": row["category__name"] or "Uncategorized",
                "total": float(row["total"] or 0),
            }
            for row in data
        ]

        return Response({"results": formatted})


# ---------------------------
# Analytics: Monthly by Category
# ---------------------------
class MonthlyCategoryAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)

        ttype = request.query_params.get("type")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if ttype:
            qs = qs.filter(type=ttype)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        data = (
            qs.annotate(month=TruncMonth("date"))
            .values("month", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        grouped = defaultdict(lambda: defaultdict(float))
        categories = set()

        for row in data:
            month = row["month"].strftime("%Y-%m")
            category = row["category__name"] or "Uncategorized"
            grouped[month][category] += float(row["total"] or 0)
            categories.add(category)

        results = []
        for month in sorted(grouped.keys()):
            entry = {"month": month}
            for cat in sorted(categories):
                entry[cat] = grouped[month].get(cat, 0.0)
            results.append(entry)

        return Response({
            "categories": sorted(categories),
            "results": results,
        })


# ---------------------------
# Budget vs Expense Analytics
# ---------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def budget_vs_expense(request, year, month):
    user = request.user
    month_start = date(int(year), int(month), 1)
    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

    categories = Category.objects.filter(user=user)
    response = []

    for cat in categories:
        budget = Budget.objects.filter(
            user=user, category=cat, month=month_start
        ).first()

        spent = Transaction.objects.filter(
            user=user,
            category=cat,
            type="expense",
            date__range=[month_start, month_end],
        ).aggregate(total=Sum("amount"))["total"] or 0

        response.append({
            "category": cat.name,
            "budget": budget.amount if budget else 0,
            "spent": spent,
        })

    return Response(response)


# ---------------------------
# Analytics: Monthly Totals (Simple)
# ---------------------------
class MonthlyTotalsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()

        qs = Transaction.objects.filter(
            user=request.user,
            date__year=today.year,
            date__month=today.month
        )

        income_total = qs.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
        expense_total = qs.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "net": float(income_total - expense_total)
        })

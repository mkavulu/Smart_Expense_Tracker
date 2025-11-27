from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Views
from .views import (
    TransactionViewSet,
    RegisterView,
    MonthlySummaryView,
    CategoryViewSet,
    CategoryAnalyticsView,
    MonthlyCategoryAnalyticsView,
)

# If your second file (analytics_views.py) contains MonthlySummaryView or MonthlyAnalyticsView,
# import it like this:
# from .analytics_views import MonthlySummaryView, MonthlyAnalyticsView

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    # ---------------------------
    # Authentication
    # ---------------------------
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---------------------------
    # Analytics (merged)
    # ---------------------------
    path("analytics/monthly-summary/", MonthlySummaryView.as_view(), name="monthly_summary"),
    path("analytics/monthly/", MonthlySummaryView.as_view(), name="monthly"),
    path("analytics/by-category/", CategoryAnalyticsView.as_view(), name="category_analytics"),
    path(
        "analytics/monthly-by-category/",
        MonthlyCategoryAnalyticsView.as_view(),
        name="monthly_category_analytics"
    ),

    # ---------------------------
    # CRUD Routes
    # ---------------------------
    path("", include(router.urls)),
]


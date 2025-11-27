from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from tracker.views import (
    TransactionViewSet,
    CategoryViewSet,
    BudgetViewSet,
    RegisterView,
    MonthlySummaryView,
    MonthlyTotalsView,
    CategoryAnalyticsView,
    MonthlyCategoryAnalyticsView,
)

# Router for ViewSets
router = DefaultRouter()
router.register("transactions", TransactionViewSet, basename="transaction")
router.register("categories", CategoryViewSet, basename="category")
router.register("budgets", BudgetViewSet, basename="budget")

urlpatterns = [
    path("admin/", admin.site.urls),

    # ---------------------------
    # Authentication
    # ---------------------------
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---------------------------
    # Analytics Endpoints (MERGED)
    # ---------------------------

    # Newly added from your snippet
    path("api/analytics/monthly/", MonthlyTotalsView.as_view(), name="monthly"),

    # Already existing analytics
    path("api/analytics/monthly-summary/", MonthlySummaryView.as_view(), name="monthly-summary"),
    path("api/analytics/category-totals/", CategoryAnalyticsView.as_view(), name="category-totals"),
    path("api/analytics/monthly-category/", MonthlyCategoryAnalyticsView.as_view(), name="monthly-category"),

    # ---------------------------
    # CRUD Routes (ViewSets)
    # ---------------------------
    path("api/", include(router.urls)),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

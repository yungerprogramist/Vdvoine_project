from django.urls import path

from .views import OrderListView, OrderDetailView, OrderCancelView

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/cancel/", OrderCancelView.as_view(), name="cancel"),
]
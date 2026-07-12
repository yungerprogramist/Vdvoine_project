from django.urls import path

from .views import (
    CollectionListView,
    CollectionDetailView,
    ProductCardListView,
    ProductCardDetailView,
)

app_name = "products"

urlpatterns = [
    path("", ProductCardListView.as_view(), name="list"),
    path("<int:pk>/", ProductCardDetailView.as_view(), name="detail"),
    path("collections/", CollectionListView.as_view(), name="collection-list"),
    path("collections/<int:pk>/", CollectionDetailView.as_view(), name="collection-detail"),
]
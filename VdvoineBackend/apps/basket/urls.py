from django.urls import path

from .views import BasketListView, BasketItemView, BasketClearView

app_name = "basket"

urlpatterns = [
    path("", BasketListView.as_view(), name="list"),
    path("clear/", BasketClearView.as_view(), name="clear"),
    path("<int:pk>/", BasketItemView.as_view(), name="item"),
]
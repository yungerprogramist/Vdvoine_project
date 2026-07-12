from django.urls import path

from .views import PromoCodeValidateView

app_name = "promotions"

urlpatterns = [
    path("validate/", PromoCodeValidateView.as_view(), name="validate"),
]
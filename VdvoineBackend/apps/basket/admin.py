from django.contrib import admin

from apps.basket.models import Basket, UserSession

# Register your models here.


admin.site.register(Basket)
admin.site.register(UserSession)

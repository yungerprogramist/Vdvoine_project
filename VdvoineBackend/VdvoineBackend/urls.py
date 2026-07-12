from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/basket/",     include("apps.basket.urls",     namespace="basket")),
    path("api/products/",   include("apps.products.urls",   namespace="products")),
    path("api/orders/",     include("apps.orders.urls",     namespace="orders")),
    path("api/promotions/", include("apps.promotions.urls", namespace="promotions")),
    # path("api/payments/",   include("apps.payments.urls",   namespace="payments")),
    # path("api/delivery/",   include("apps.delivery.urls",   namespace="delivery")),
] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

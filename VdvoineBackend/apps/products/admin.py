from django.contrib import admin

from apps.products.models import Collection, ProductCard, ProductVariant, Size

# Register your models here.


admin.site.register(Collection)
admin.site.register(ProductCard)
admin.site.register(Size)
admin.site.register(ProductVariant)
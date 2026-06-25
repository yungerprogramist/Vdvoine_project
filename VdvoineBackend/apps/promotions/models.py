from django.db import models


class PromoCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    discount_value = models.PositiveIntegerField()

    class Meta:
        db_table = "promo_code"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    @property
    def is_available(self):
        """Можно ли ещё применить промокод"""
        if not self.is_active:
            return False
        if self.usage_limit is None:
            return True
        return self.orders.count() < self.usage_limit
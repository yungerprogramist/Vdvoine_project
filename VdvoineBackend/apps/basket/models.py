from django.db import models

from apps.products.models import ProductVariant


class UserSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "users_django"
        verbose_name = "Сессия пользователя"
        verbose_name_plural = "Сессии пользователей"

    def __str__(self):
        return self.session_id


class Basket(models.Model):
    product = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="basket_items",
    )
    user_session = models.ForeignKey(
        UserSession,
        on_delete=models.CASCADE,
        related_name="basket_items",
    )
    count = models.PositiveIntegerField(default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "basket"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        # Один вариант товара — одна запись на сессию
        unique_together = ("product", "user_session")

    def __str__(self):
        return f"{self.user_session.session_id} — {self.product}"
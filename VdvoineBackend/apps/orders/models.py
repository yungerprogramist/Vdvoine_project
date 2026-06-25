from django.db import models

from apps.basket.models import UserSession
from apps.products.models import ProductVariant
from apps.promotions.models import PromoCode


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        CONFIRMED = "confirmed", "Подтверждён"
        PAID = "paid", "Оплачен"
        SHIPPED = "shipped", "Отправлен"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменён"

    class PaymentStatus(models.TextChoices):
        WAITING = "waiting", "Ожидает оплаты"
        PAID = "paid", "Оплачен"
        FAILED = "failed", "Ошибка оплаты"
        REFUNDED = "refunded", "Возврат"

    id_session = models.ForeignKey(
        UserSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    pickup_point = models.CharField(max_length=255, blank=True, null=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_status = models.CharField(
        max_length=50,
        choices=PaymentStatus.choices,
        default=PaymentStatus.WAITING,
        null=True,
        blank=True,
    )
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_timestamp"]

    def __str__(self):
        return f"Заказ #{self.pk} — {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    count = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.order} — {self.product}"

    @property
    def total(self):
        return self.price * self.count
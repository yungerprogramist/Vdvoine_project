from django.db import transaction
from rest_framework import serializers

from apps.basket.models import Basket
from apps.products.serializers import ProductVariantSerializer as ProductVariantDetailSerializer
from apps.products.models import ProductVariant
from apps.promotions.models import PromoCode
from apps.orders.models import Order, OrderItem


# --- OrderItem ---

class OrderItemSerializer(serializers.ModelSerializer):
    """Чтение: позиция заказа с информацией о товаре"""
    product = ProductVariantDetailSerializer(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "count", "price", "total")


# --- Order ---

class OrderListSerializer(serializers.ModelSerializer):
    """Для списка заказов — без вложенных позиций"""

    class Meta:
        model = Order
        fields = (
            "id", "full_name", "status", "payment_status",
            "total_price", "created_timestamp",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    """Для страницы конкретного заказа — с позициями"""
    items = OrderItemSerializer(many=True, read_only=True)
    promo_code = serializers.SlugRelatedField(slug_field="code", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "full_name", "email", "phone", "city", "pickup_point",
            "promo_code", "total_price", "status", "payment_status",
            "created_timestamp", "items",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Создание заказа из корзины пользователя.
    Ожидает user_session в context, промокод — опционально по коду.
    """
    promo_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = (
            "id", "full_name", "email", "phone", "city",
            "pickup_point", "promo_code",
        )

    def validate_promo_code(self, value):
        if not value:
            return None
        try:
            promo = PromoCode.objects.get(code=value)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Промокод не найден")
        if not promo.is_available:
            raise serializers.ValidationError("Промокод недействителен или лимит исчерпан")
        return promo

    def validate(self, attrs):
        user_session = self.context["user_session"]
        basket_items = Basket.objects.filter(user_session=user_session).select_related(
            "product", "product__product_card"
        )
        if not basket_items.exists():
            raise serializers.ValidationError("Корзина пуста")

        for item in basket_items:
            if item.product.quantity < item.count:
                raise serializers.ValidationError(
                    f"Недостаточно товара «{item.product.product_card.name}» на складе"
                )

        attrs["_basket_items"] = list(basket_items)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        basket_items = validated_data.pop("_basket_items")
        promo = validated_data.pop("promo_code", None)
        user_session = self.context["user_session"]

        total_price = sum(
            item.product.product_card.price * item.count for item in basket_items
        )
        if promo:
            discount = total_price * promo.discount_value / 100
            total_price -= discount

        order = Order.objects.create(
            id_session=user_session,
            promo_code=promo,
            total_price=total_price,
            **validated_data,
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                count=item.count,
                price=item.product.product_card.price,
            )
            for item in basket_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Списываем остатки и чистим корзину
        for item in basket_items:
            ProductVariant.objects.filter(pk=item.product_id).update(
                quantity=item.product.quantity - item.count
            )
        Basket.objects.filter(user_session=user_session).delete()

        return order
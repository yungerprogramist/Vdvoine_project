from rest_framework import serializers

from apps.products.models import ProductVariant
from apps.products.serializers import ProductCardListSerializer, SizeSerializer
from apps.basket.models import Basket


class ProductVariantSerializer(serializers.ModelSerializer):
    """Вариант товара с карточкой и размером — для отображения в корзине"""
    product_card = ProductCardListSerializer(read_only=True)
    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ("id", "product_card", "size", "quantity")


# --- Basket ---

class BasketSerializer(serializers.ModelSerializer):
    """Чтение: полная информация о позиции в корзине"""
    product = ProductVariantSerializer(read_only=True)

    class Meta:
        model = Basket
        fields = ("id", "product", "count", "created_timestamp")


class BasketWriteSerializer(serializers.ModelSerializer):
    """Запись: добавление / обновление позиции в корзине"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source="product",
    )

    class Meta:
        model = Basket
        fields = ("product_id", "count")

    def validate(self, attrs):
        product: ProductVariant = attrs["product"]
        count: int = attrs["count"]

        if product.quantity < count:
            raise serializers.ValidationError(
                {"count": f"Недостаточно товара на складе. Доступно: {product.quantity}"}
            )
        return attrs

    def create(self, validated_data):
        user_session = self.context["user_session"]
        basket_item, created = Basket.objects.get_or_create(
            product=validated_data["product"],
            user_session=user_session,
            defaults={"count": validated_data["count"]},
        )
        if not created:
            basket_item.count = validated_data["count"]
            basket_item.save()
        return basket_item
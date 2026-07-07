from rest_framework import serializers

from apps.products.models import Collection, ProductCard, Size, ProductVariant


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("id", "name", "date", "is_active")


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("id", "name")


class ProductVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ("id", "size", "quantity")


# --- ProductCard ---

class ProductCardListSerializer(serializers.ModelSerializer):
    """Для списка товаров — минимум полей, быстрая загрузка"""
    collection = CollectionSerializer(read_only=True)

    class Meta:
        model = ProductCard
        fields = ("id", "name", "image", "price", "collection")


class ProductCardDetailSerializer(serializers.ModelSerializer):
    """Для страницы товара — полная информация с вариантами"""
    collection = CollectionSerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCard
        fields = ("id", "name", "description", "image", "price", "collection", "variants")


class ProductCardWriteSerializer(serializers.ModelSerializer):
    """Для создания / редактирования товара (админ)"""
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source="collection",
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ProductCard
        fields = ("id", "name", "description", "image", "price", "collection_id")
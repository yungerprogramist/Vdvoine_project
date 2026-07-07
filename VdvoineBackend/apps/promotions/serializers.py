from rest_framework import serializers

from .models import PromoCode


class PromoCodeSerializer(serializers.ModelSerializer):
    """Чтение промокода — для отображения применённого промокода в заказе"""
    class Meta:
        model = PromoCode
        fields = ("id", "code", "discount_value", "is_active")


class PromoCodeValidateSerializer(serializers.Serializer):
    """Проверка промокода по коду — вызывается с фронта перед оформлением заказа"""
    code = serializers.CharField(max_length=255)

    def validate_code(self, code):
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Промокод не найден.")

        if not promo.is_available:
            raise serializers.ValidationError("Промокод недействителен или исчерпан.")

        return code

    def get_promo(self):
        """Возвращает объект промокода после валидации"""
        return PromoCode.objects.get(code=self.validated_data["code"])


class PromoCodeAdminSerializer(serializers.ModelSerializer):
    """Создание и редактирование промокодов — только для админа"""
    usage_count = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = ("id", "code", "discount_value", "is_active", "usage_limit", "usage_count")

    def get_usage_count(self, obj):
        """Сколько раз промокод уже был использован"""
        return obj.orders.count()
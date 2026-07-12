from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PromoCode
from .serializers import PromoCodeValidateSerializer, PromoCodeSerializer


class PromoCodeValidateView(APIView):
    """
    POST /api/promotions/validate/ — проверить промокод перед оформлением заказа
    """

    def post(self, request):
        serializer = PromoCodeValidateSerializer(data=request.data)
        if serializer.is_valid():
            promo = serializer.get_promo()
            return Response({
                "valid": True,
                "promo": PromoCodeSerializer(promo).data,
            })
        return Response(
            {"valid": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
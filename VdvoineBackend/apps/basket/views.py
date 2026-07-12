from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Basket, UserSession
from .serializers import BasketSerializer, BasketWriteSerializer


def get_or_create_session(request) -> UserSession:
    """Получает или создаёт сессию пользователя по session_id из куки"""
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    session, _ = UserSession.objects.get_or_create(session_id=session_id)
    return session


class BasketListView(APIView):
    """
    GET  /api/basket/       — получить корзину текущей сессии
    POST /api/basket/       — добавить товар в корзину
    """

    def get(self, request):
        session = get_or_create_session(request)
        items = Basket.objects.filter(user_session=session).select_related(
            "product__product_card",
            "product__size",
        )
        serializer = BasketSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        session = get_or_create_session(request)
        serializer = BasketWriteSerializer(
            data=request.data,
            context={"user_session": session},
        )
        if serializer.is_valid():
            item = serializer.save()
            return Response(BasketSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketItemView(APIView):
    """
    PATCH  /api/basket/<id>/  — обновить количество позиции
    DELETE /api/basket/<id>/  — удалить позицию из корзины
    """

    def get_object(self, pk, session):
        try:
            return Basket.objects.get(pk=pk, user_session=session)
        except Basket.DoesNotExist:
            return None

    def patch(self, request, pk):
        session = get_or_create_session(request)
        item = self.get_object(pk, session)
        if not item:
            return Response({"detail": "Позиция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasketWriteSerializer(
            item,
            data=request.data,
            partial=True,
            context={"user_session": session},
        )
        if serializer.is_valid():
            updated = serializer.save()
            return Response(BasketSerializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        session = get_or_create_session(request)
        item = self.get_object(pk, session)
        if not item:
            return Response({"detail": "Позиция не найдена."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BasketClearView(APIView):
    """
    DELETE /api/basket/clear/ — очистить всю корзину
    """

    def delete(self, request):
        session = get_or_create_session(request)
        Basket.objects.filter(user_session=session).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
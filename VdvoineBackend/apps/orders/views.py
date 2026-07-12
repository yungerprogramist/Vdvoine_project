from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.basket.models import UserSession
from .models import Order
from .serializers import OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer


def get_session(request):
    """Получает сессию пользователя или None если не существует"""
    session_key = request.session.session_key
    if not session_key:
        return None
    return UserSession.objects.filter(session_id=session_key).first()


class OrderListView(APIView):
    """
    GET  /api/orders/  — список заказов текущей сессии
    POST /api/orders/  — создать заказ из корзины
    """

    def get(self, request):
        session = get_session(request)
        if not session:
            return Response([])

        orders = Order.objects.filter(id_session=session)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        session = get_session(request)
        if not session:
            return Response(
                {"detail": "Сессия не найдена. Добавьте товар в корзину."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderCreateSerializer(
            data=request.data,
            context={"user_session": session},
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderDetailSerializer(order).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    """
    GET /api/orders/<id>/ — детальная страница заказа
    """

    def get_object(self, pk, session):
        try:
            return Order.objects.prefetch_related(
                "items__product__product_card",
                "items__product__size",
            ).get(pk=pk, id_session=session)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        session = get_session(request)
        if not session:
            return Response(
                {"detail": "Сессия не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order = self.get_object(pk, session)
        if not order:
            return Response(
                {"detail": "Заказ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class OrderCancelView(APIView):
    """
    PATCH /api/orders/<id>/cancel/ — отменить заказ
    """

    def patch(self, request, pk):
        session = get_session(request)
        if not session:
            return Response(
                {"detail": "Сессия не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            order = Order.objects.get(pk=pk, id_session=session)
        except Order.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        cancellable = {Order.Status.PENDING, Order.Status.CONFIRMED}
        if order.status not in cancellable:
            return Response(
                {"detail": f"Нельзя отменить заказ со статусом «{order.get_status_display()}»."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        return Response(OrderDetailSerializer(order).data)
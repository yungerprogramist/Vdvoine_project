from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Collection, ProductCard
from .serializers import (
    CollectionSerializer,
    ProductCardListSerializer,
    ProductCardDetailSerializer,
    ProductCardWriteSerializer,
)


# --- Collections ---

class CollectionListView(APIView):
    """
    GET /api/products/collections/ — список всех активных коллекций
    """

    def get(self, request):
        collections = Collection.objects.filter(is_active=True)
        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data)


class CollectionDetailView(APIView):
    """
    GET /api/products/collections/<id>/ — товары внутри коллекции
    """

    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk, is_active=True)
        except Collection.DoesNotExist:
            return None

    def get(self, request, pk):
        collection = self.get_object(pk)
        if not collection:
            return Response({"detail": "Коллекция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        products = ProductCard.objects.filter(collection=collection).prefetch_related(
            "variants__size"
        )
        serializer = ProductCardListSerializer(products, many=True)
        return Response({
            "collection": CollectionSerializer(collection).data,
            "products": serializer.data,
        })


# --- Products ---

class ProductCardListView(APIView):
    """
    GET /api/products/ — список всех товаров с фильтрацией
    """

    def get(self, request):
        queryset = ProductCard.objects.select_related("collection").prefetch_related(
            "variants__size"
        )

        # Фильтр по коллекции: /api/products/?collection=1
        collection_id = request.query_params.get("collection")
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)

        # Фильтр по размеру: /api/products/?size=2
        size_id = request.query_params.get("size")
        if size_id:
            queryset = queryset.filter(variants__size_id=size_id, variants__quantity__gt=0)

        # Сортировка: /api/products/?ordering=price или ?ordering=-price
        ordering = request.query_params.get("ordering")
        allowed_orderings = {"price", "-price", "name", "-name"}
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)

        serializer = ProductCardListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductCardDetailView(APIView):
    """
    GET /api/products/<id>/ — страница товара с вариантами
    """

    def get_object(self, pk):
        try:
            return ProductCard.objects.prefetch_related(
                "variants__size",
            ).select_related("collection").get(pk=pk)
        except ProductCard.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"detail": "Товар не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductCardDetailSerializer(product)
        return Response(serializer.data)
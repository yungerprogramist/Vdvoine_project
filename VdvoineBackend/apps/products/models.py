from django.db import models


class Collection(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "collections"
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self):
        return self.name


class ProductCard(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    class Meta:
        db_table = "product_card"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "sizes"
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product_card = models.ForeignKey(
        ProductCard,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,
        related_name="variants",
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "product_variants"
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"
        # Один размер — один раз на карточку товара
        unique_together = ("product_card", "size")

    def __str__(self):
        return f"{self.product_card.name} — {self.size.name}"
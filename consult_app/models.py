from django.db import models
from django.utils import timezone
from boran_app.models import Catalogo

# ——————————————————————————————————————————————————————————————
# PRODUCTOS MAS RENTABLES
# ——————————————————————————————————————————————————————————————

class ProductoRentable(models.Model):
    codigo_producto = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    producto = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    venta_total = models.DecimalField(max_digits=20, decimal_places=2)
    costo_total = models.DecimalField(max_digits=20, decimal_places=2)
    utilidad_bruta_total = models.DecimalField(max_digits=20, decimal_places=2)
    margen_bruto = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        db_table = "productos_rentables"

    def __str__(self):
        return f"{self.codigo_producto} - {self.producto}"

# ——————————————————————————————————————————————————————————————
# TIENDAS
# ——————————————————————————————————————————————————————————————

class BodegaTienda(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Tienda/Bodega")

    class Meta:
        verbose_name = "Tienda/Bodega"
        verbose_name_plural = "Tiendas/Bodegas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# ——————————————————————————————————————————————————————————————
# ENVIO A TIENDAS
# ——————————————————————————————————————————————————————————————

# Modelo principal de envíos
class EnviosATiendas(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(
        default=timezone.now,
        verbose_name="Fecha"
    )
    sku = models.ForeignKey(
        Catalogo,                # Asegúrate que Catalogo esté importado
        to_field='sku',
        on_delete=models.PROTECT,
        db_column='sku',
        verbose_name="SKU"
    )
    cantidad = models.IntegerField(
        verbose_name="Cantidad",
        default=0
    )
    tienda_bodega = models.ForeignKey(
        BodegaTienda,
        on_delete=models.PROTECT,
        verbose_name="Tienda/Bodega"
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentario"
    )

    class Meta:
        db_table = 'envios_a_tiendas'
        verbose_name = 'Envío a Tienda'
        verbose_name_plural = 'Envíos a Tiendas'
        ordering = ['-fecha', 'tienda_bodega']

    def __str__(self):
        return f"{self.fecha} | SKU: {self.sku.sku} | {self.cantidad} a {self.tienda_bodega}"

#_______________________________________________________________
#INVENTARIO INICIAL TIENDAS
#_______________________________________________________________

class InventarioInicialTiendas(models.Model):
    fecha = models.DateField(
        default=timezone.now,
        verbose_name="Fecha"
    )
    sku = models.ForeignKey(
        Catalogo,
        to_field='sku',
        on_delete=models.PROTECT,
        db_column='sku',
        verbose_name="SKU"
    )
    tienda = models.ForeignKey(
        BodegaTienda,
        on_delete=models.PROTECT,
        verbose_name="Tienda"
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
        default=0
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentario"
    )

    class Meta:
        db_table = 'inventario_inicial_tiendas'
        verbose_name = 'Inventario Inicial Tienda'
        verbose_name_plural = 'Inventarios Iniciales Tiendas'
        ordering = ['-fecha', 'tienda']

    def __str__(self):
        return f"{self.fecha} | {self.sku.sku} | {self.tienda} | {self.cantidad}"

#_______________________________________________________________
# AJUSTE INVENTARIO TIENDAS
#_______________________________________________________________

class AjusteInventarioTienda(models.Model):
    fecha = models.DateField(
        default=timezone.now,
        verbose_name="Fecha"
    )
    sku = models.ForeignKey(
        Catalogo,
        to_field='sku',            # requiere que Catalogo.sku sea unique=True
        on_delete=models.PROTECT,
        db_column='sku',
        verbose_name="SKU",
        related_name="ajustes_tienda"
    )
    tienda = models.ForeignKey(
        BodegaTienda,
        on_delete=models.PROTECT,
        verbose_name="Tienda",
        related_name="ajustes"
    )
    # Puede ser positivo (ingreso) o negativo (merma/salida)
    cantidad = models.IntegerField(
        verbose_name="Cantidad (±)"
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentario"
    )

    class Meta:
        db_table = "ajustes_inventario_tiendas"
        verbose_name = "Ajuste Inventario Tienda"
        verbose_name_plural = "Ajustes Inventario Tienda"
        ordering = ['-fecha', 'tienda', 'sku']
        indexes = [
            models.Index(fields=['tienda', 'sku', 'fecha'], name='idx_ajustes_tsf'),
        ]

    def __str__(self):
        return f"{self.fecha} | {self.sku.sku} | {self.tienda} | {self.cantidad:+d}"

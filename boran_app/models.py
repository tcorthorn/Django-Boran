from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# ——————————————————————————————————————————————————————————————
# 1) Modelo: AsientosContables
# ——————————————————————————————————————————————————————————————


class AsientosContables(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto"
    )
    debito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Débito",
        editable=False  # <--- Inmodificable en admin y forms
    )
    cuenta_debito = models.CharField(
        max_length=7,
        verbose_name="Cuenta Débito",
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message='La cuenta débito debe tener exactamente 7 dígitos.'
            )
        ]
    )
    credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Crédito",
        editable=False  # <--- Inmodificable en admin y forms
    )
    cuenta_credito = models.CharField(
        max_length=7,
        verbose_name="Cuenta Crédito",
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message='La cuenta crédito debe tener exactamente 7 dígitos.'
            )
        ]
    )
    comentario = models.CharField(
        verbose_name="Comentario",
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'asientos_contables'
        verbose_name = 'Asiento contable'
        verbose_name_plural = 'Asientos contables'

    def save(self, *args, **kwargs):
        # Asignación automática antes de guardar
        self.debito = self.monto
        self.credito = self.monto
        super().save(*args, **kwargs)

# ——————————————————————————————————————————————————————————————
# 2) Modelo: Catalogo
# ——————————————————————————————————————————————————————————————
from decimal import Decimal, ROUND_HALF_UP

class Catalogo(models.Model):
    """
    Catálogo de SKUs válidos.
    """
    fecha_ingreso = models.DateField(
        verbose_name="Fecha Ingreso"
    )
    sku = models.CharField(
        verbose_name="SKU",
        max_length=7,
        unique=True,
        validators=[
            # El SKU debe comenzar con 'B' y tener exactamente 6 caracteres en total.
            RegexValidator(
                regex=r'^B.{6}$',
                message="El SKU debe comenzar con 'B' y tener exactamente 6 caracteres en total (B + 5 más)."
            )
        ]
    )

    clase_producto = models.CharField(
        verbose_name="Clase de Producto",
        max_length=50,
        default =""
    )

    categoria = models.CharField(
        verbose_name="Categoría",
        max_length=50
    )

    producto = models.CharField(
        verbose_name="Producto",
        max_length=100
    )

    cod_proveedor = models.TextField(
        max_length=20,
        blank=True,
        null=True, 
    )   

    descripcion = models.TextField(
        verbose_name="Descripción",
        blank=True,
        null=True
    )

    costo_base= models.DecimalField(
        verbose_name="Costo Base Producto",
        max_digits=12,
        decimal_places=2,
        default=0
    )

    costo_adicional = models.DecimalField(
        verbose_name="Costo adicional",
        max_digits=12,
        decimal_places=2,
        default = 1.0
    )

    costo_directo_producto = models.DecimalField(
        verbose_name="Costo directo producto",
        max_digits=12,
        decimal_places=2,
        default=0
    )

    comentario = models.CharField(
        verbose_name="Comentario",
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogo'

    def __str__(self):
        return self.sku

    def save(self, *args, **kwargs):
        self.sku = self.sku.upper()  # Fuerza a mayúsculas antes de guardar
        base = Decimal(str(self.costo_base or 0))
        try:
            self.costo_directo_producto = (
                (base + (self.costo_adicional or Decimal('0.00'))) / Decimal("1.19")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception:
            self.costo_directo_producto = Decimal('0.00')
        super().save(*args, **kwargs)

# ——————————————————————————————————————————————————————————————
# 3) Modelo: Envios
# ——————————————————————————————————————————————————————————————

class Envios(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(
        default=timezone.now,
        verbose_name="Fecha"
    )
    tienda_bodega = models.CharField(
        max_length=255,
        verbose_name="Tienda/Bodega",
        default="",
        blank=True
    )

    # Ahora sku es ForeignKey a Catalogo.sku
    sku = models.ForeignKey(
        Catalogo,
        to_field='sku',
        on_delete=models.PROTECT,
        db_column='sku',
        verbose_name="SKU"
    )

    cantidad = models.IntegerField(
        verbose_name="Cantidad",
        default=0
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentario"
    )
    proveedor = models.IntegerField(       # recién agregado
        verbose_name="Proveedor",
        default=0,
        blank=True
    )

    class Meta:
        db_table = 'envios'
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'

    def __str__(self):
        return f"Envío {self.pk} – {self.sku.sku} – Cantidad: {self.cantidad}"

# ——————————————————————————————————————————————————————————————
# 4) Modelo: EntradaProductos
# ——————————————————————————————————————————————————————————————

class EntradaProductos(models.Model):
   

    id = models.AutoField(primary_key=True)

    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )

    proveedor = models.IntegerField(
        verbose_name="Proveedor",
        default=0     # <--- Ponemos default=0 para no romper migraciones
    )

    # ForeignKey a Catalogo.sku
    sku = models.ForeignKey(
        'boran_app.Catalogo',
        to_field='sku',
        on_delete=models.PROTECT,
        db_column='sku',
        verbose_name="SKU",
    )


    DOCUMENTO_CHOICES = [
        ('Factura', 'Factura'),
        ('Boleta', 'Boleta'),
        ('Anticipo', 'Anticipo'),
        ('Cuenta por pagar', 'Cuenta por pagar'),
        ('Otro', 'Otro'),
    ]
    documento_anticipo = models.CharField(
        max_length=20,
        verbose_name="Documento Anticipo",
        choices=DOCUMENTO_CHOICES,
        default='Otro'
    )

    numero_factura_boleta = models.IntegerField(null=True, blank=True)

    # ‣ Cantidad ingresada (ahora con default=0)
    cantidad_ingresada = models.IntegerField(
        verbose_name="Cantidad Ingresada",
        validators=[MinValueValidator(0, message="La cantidad debe ser cero o positiva.")],
        default=0
    )

    # ‣ Lote (default=0)
    #lote = models.IntegerField(
        #verbose_name="Lote",
        #default=0
    #)

    # ‣ Costo con IVA (default=0.00)
    costo_con_iva = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        verbose_name="Costo con IVA",
        default=Decimal('0.00')
    )

    # ‣ Costo adicional (default=0.00)
    costo_adicional = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Costo Adicional",
        default=Decimal('0.00')
    )

    # ‣ Costo unitario total producto (calculado)
    costo_unitario_total_producto = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        verbose_name="Costo Unitario Total Producto",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Costo Total (calculado)
    costo_total = models.DecimalField(
        max_digits=14,
        decimal_places=1,
        verbose_name="Costo Total",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ IVA Compra (calculado)
    iva_compra = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        verbose_name="IVA Compra",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Costo neto (calculado)
    costo_neto = models.DecimalField(
        max_digits=14,
        decimal_places=1,
        verbose_name="Costo Neto",
        editable=False,
        default=Decimal('0.00')
    )

    fecha_pago_factura_plazo = models.DateField(null=True, blank=True)

    # ‣ Cuenta Débito (7 dígitos, default=1010900)
    cuenta_debito = models.IntegerField(
        verbose_name="Cuenta Débito",
        default=1010900,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    # ‣ Débito (calculado = costo_neto)
    debito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Cuenta Débito IVA (7 dígitos, default=1011001)
    cuenta_debito_iva = models.IntegerField(
        verbose_name="Cuenta Débito IVA",
        default=1011001,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    # ‣ Débito IVA (calculado = iva_compra)
    debito_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Débito IVA",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Inventario inicio (texto corto, default "")
    inventario_inicio = models.CharField(
        max_length=50,
        verbose_name="Inventario Inicio",
        default="",  
        blank=True
    )

    # ‣ Cuenta Crédito (calculado)
    cuenta_credito = models.IntegerField(
        verbose_name="Cuenta Crédito",
        editable=False,
        default=1010100,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    # ‣ Crédito (calculado)
    credito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Cuenta Crédito genero (default= 1010901)
    cuenta_credito_genero = models.IntegerField(
        verbose_name="Cuenta Crédito género",
        editable=False,
        default=1010901,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    # ‣ Crédito género producto (calculado)
    credito_genero = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito género",
        editable=False,
        default=Decimal('0.00')
    )

    # ‣ Comentario (texto corto, default "")
    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        default="",
        blank=True
    )


    class Meta:
        db_table = 'entrada_productos'
        verbose_name = 'Entrada de Producto'
        verbose_name_plural = 'Entradas de Productos'

    def save(self, *args, **kwargs):
        total_c_iva = Decimal(self.costo_con_iva or Decimal('0.00'))
        adicional   = Decimal(self.costo_adicional or Decimal('0.00'))
        cantidad    = Decimal(self.cantidad_ingresada or 0)

        # 1) costo_unitario_total_producto
        self.costo_unitario_total_producto = (total_c_iva + adicional).quantize(Decimal('0.01'))

        # 2) costo_total
        self.costo_total = (cantidad * self.costo_unitario_total_producto).quantize(Decimal('0.01'))

        # 3) iva_compra
        if self.documento_anticipo == 'Factura':
            self.iva_compra = (self.costo_total * (Decimal('0.19') / Decimal('1.19'))).quantize(Decimal('0.01'))
        else:
            self.iva_compra = Decimal('0.00')

        # 4) costo_neto
        self.costo_neto = (self.costo_total - self.iva_compra).quantize(Decimal('0.01'))

        # 5) debito = costo_neto
        self.debito = self.costo_neto

        # 6) debito_iva = iva_compra
        self.debito_iva = self.iva_compra

        # 7) cuenta_credito según condiciones  (✅ corrige el nombre del campo)
        if (self.fecha_pago_factura_plazo is not None) or (self.documento_anticipo == 'Cuenta por pagar'):
            self.cuenta_credito = 2010800
        elif self.documento_anticipo == 'Anticipo':
            self.cuenta_credito = 1011100
        else:
            self.cuenta_credito = 1010100

        # 8) crédito (flujo general)
        if self.inventario_inicio == 'Inventario inicial':
            self.credito = Decimal('0.00')
        else:
            self.credito = (cantidad * total_c_iva).quantize(Decimal('0.01'))

        # 9) crédito género  (✅ asigna al campo correcto)
        if self.inventario_inicio == 'Inventario inicial':
            self.credito_genero = Decimal('0.00')
        else:
            self.credito_genero = (cantidad * adicional).quantize(Decimal('0.01'))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} – SKU {self.sku.sku} – Cantidad: {self.cantidad_ingresada}"

# ——————————————————————————————————————————————————————————————
# 5) Modelo: OtrosGastos
# ——————————————————————————————————————————————————————————————

class OtrosGastos(models.Model):
    """
    Modelo: OtrosGastos
    -------------------
    Campos:
      - id                  : AutoField (autonumeración implícita)
      - fecha               : DateField
      - otros_gastos        : ChoiceField ("Factura", "Boleta", "Otros")
      - total               : DecimalField
      - iva                 : DecimalField (calculado: si es Factura ⇒ total * (0.19/1.19); si no ⇒ 0)
      - monto_neto          : DecimalField (calculado = total - iva)
      - cuenta_debito       : CharField (7 dígitos, default="1011001")
      - debito              : DecimalField (calculado = iva)
      - cuenta_credito      : CharField (7 dígitos)
      - credito             : DecimalField (calculado = total)
      - comentario          : CharField (texto corto)
      - cuenta_debito_eerr  : CharField (7 dígitos)
      - debito_eerr         : DecimalField (calculado según regla)
    """

    FACTURA = 'Factura'
    BOLETA = 'Boleta'
    OTROS = 'Otros'
    OTROS_GASTOS_CHOICES = [
        (FACTURA, 'Factura'),
        (BOLETA, 'Boleta'),
        (OTROS, 'Otros'),
    ]

    id = models.AutoField(primary_key=True)

    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )

    otros_gastos = models.CharField(
        max_length=20,
        verbose_name="Otros Gastos",
        choices=OTROS_GASTOS_CHOICES,
        default=OTROS
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Total"
    )

    iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="IVA",
        editable=False,
        default=Decimal('0.00')
    )

    monto_neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto neto",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_debito = models.CharField(
        max_length=7,
        verbose_name="Cuenta Débito",
        default=1011001,
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message='La cuenta débito debe tener exactamente 7 dígitos.'
            )
        ]
    )

    # Ahora debito se calcula = iva
    debito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Débito",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_credito = models.CharField(
        max_length=7,
        verbose_name="Cuenta Crédito",
        default=1010100,
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message='La cuenta crédito debe tener exactamente 7 dígitos.'
            )
        ]
    )

    # Ahora credito se calcula = total
    credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Crédito",
        editable=False,
        default=Decimal('0.00')
    )

    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        blank=True,
        null=True
    )

    cuenta_debito_eerr = models.CharField(
        max_length=7,
        verbose_name="Cuenta Débito EERR",
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message='La cuenta débito EERR debe tener exactamente 7 dígitos.'
            )
        ]
    )

    debito_eerr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Débito EERR",
        editable=False,
        default=Decimal('0.00')
    )

    class Meta:
        db_table = 'otros_gastos'
        verbose_name = 'Otro Gasto'
        verbose_name_plural = 'Otros Gastos'

    def save(self, *args, **kwargs):
        """
        Antes de guardar, calcular:
         - iva: si 'otros_gastos' == 'Factura' ⇒ total * (0.19 / 1.19); de lo contrario 0
         - monto_neto: total - iva
         - debito: siempre igual a iva
         - credito: siempre igual a total
         - debito_eerr: si 'otros_gastos' == 'Factura' ⇒ monto_neto; de lo contrario ⇒ total
        """
        total = Decimal(self.total or Decimal('0.00'))

        if self.otros_gastos == self.FACTURA:
            # Calcular IVA = total * (0.19/1.19)
            self.iva = (total * (Decimal('0.19') / Decimal('1.19'))).quantize(Decimal('0.01'))
        else:
            self.iva = Decimal('0.00')

        # Monto neto = total - iva
        self.monto_neto = (total - self.iva).quantize(Decimal('0.01'))

        # Debito = iva
        self.debito = self.iva

        # Credito = total
        self.credito = total

        # Debito EERR según regla
        if self.otros_gastos == self.FACTURA:
            self.debito_eerr = self.monto_neto
        else:
            self.debito_eerr = total

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} – {self.otros_gastos} – Total: {self.total}"

# ——————————————————————————————————————————————————————————————
# 6) Modelo: SueldosHonorarios
# ——————————————————————————————————————————————————————————————

class SueldosHonorarios(models.Model):
    """
    Modelo: SueldosHonorarios
    -------------------------
    Campos:
      - id                   : AutoField (autonumeración implícita)
      - fecha                : DateField
      - tipo_remuneracion    : CharField con opciones ("Sueldo", "Honorarios", "Otro")
      - monto_total_pagado   : DecimalField
      - retenciones          : DecimalField (calculado: si es Honorarios ⇒ monto_total_pagado * 0.115; si no ⇒ 0)
      - nombre               : CharField (texto corto)
      - cuenta_debito        : IntegerField (7 dígitos, default=3010300, validación 7 dígitos)
      - debito               : DecimalField
      - cuenta_credito       : IntegerField (7 dígitos, default=1010100, validación 7 dígitos)
      - credito              : DecimalField
      - cuenta_credito2      : IntegerField (7 dígitos, default=2011200, validación 7 dígitos)
      - credito2             : DecimalField
      - comentario           : CharField (texto corto)
    """

    # 1) ID: se crea automáticamente con AutoField, no es necesario declararlo.

    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )

    SUELDO = 'Sueldo'
    HONORARIOS = 'Honorarios'
    OTRO = 'Otro'
    TIPO_REMU_CHOICES = [
        (SUELDO, 'Sueldo'),
        (HONORARIOS, 'Honorarios'),
        (OTRO, 'Otro'),
    ]
    tipo_remuneracion = models.CharField(
        max_length=20,
        verbose_name="Tipo remuneración",
        choices=TIPO_REMU_CHOICES,
        default=SUELDO
    )

    monto_total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto total pagado"
    )

    retenciones = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Retenciones",
        editable=False,
        default=Decimal('0.00')
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    cuenta_debito = models.IntegerField(
        verbose_name="Cuenta Débito",     
        default=3010300,
        editable=False,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    debito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Débito",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_credito = models.IntegerField(
        verbose_name="Cuenta Crédito",
        default=1010100,
        editable=False,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Crédito",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_credito2 = models.IntegerField(
        verbose_name="Cuenta Crédito 2",
        default=2011200,
        editable=False,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    credito2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Crédito 2",
        editable=False,
        default=Decimal('0.00')
    )

    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'sueldos'
        verbose_name = 'Sueldo u Honorario'
        verbose_name_plural = 'Sueldos u Honorarios'

    def save(self, *args, **kwargs):
        # Calculo de retenciones solo si es HONORARIOS
        total = Decimal(self.monto_total_pagado or Decimal('0.00'))
        if self.tipo_remuneracion == self.HONORARIOS:
            self.retenciones = (total * Decimal('0.115')).quantize(Decimal('0.01'))
        else:
            self.retenciones = Decimal('0.00')

        # Asignaciones automáticas (siempre)
        self.cuenta_debito = 3010300
        self.cuenta_credito = 1010100
        self.cuenta_credito2 = 2011200
        self.debito = total
        self.credito = (total - self.retenciones).quantize(Decimal('0.01'))
        self.credito2 = self.retenciones

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} – {self.tipo_remuneracion} – {self.nombre}"

# ——————————————————————————————————————————————————————————————
# 7) Modelo: BalanceInicial
# ——————————————————————————————————————————————————————————————
class BalanceInicial(models.Model):
    """
    Modelo: BalanceInicial
    ----------------------
      - id            : AutoField (autonumeración implícita)
      - fecha         : DateField (default = hoy)
      - cuenta_debito : IntegerField, 7 dígitos, default=1000000
      - debito        : DecimalField (monto), default=0.00
      - cuenta_credito: IntegerField, 7 dígitos, default=1000000
      - credito       : DecimalField (monto), default=0.00
      - comentario    : CharField (texto corto), default=""
    """

    id = models.AutoField(primary_key=True)

    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )

    cuenta_debito = models.IntegerField(
        verbose_name="Cuenta Débito",
        #default=1000000,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    debito = models.DecimalField(
        verbose_name="Débito",
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    cuenta_credito = models.IntegerField(
        verbose_name="Cuenta Crédito",
        #default=1000000,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    credito = models.DecimalField(
        verbose_name="Crédito",
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        default="",
        blank=True
    )

    class Meta:
        db_table = 'balance_inicial'
        verbose_name = 'Balance Inicial'
        verbose_name_plural = 'Balance Inicial'

    def __str__(self):
        return f"{self.fecha} — Débito: {self.debito} / Crédito: {self.credito}"


# ——————————————————————————————————————————————————————————————
# 8) Modelo: InventarioInicial
# ——————————————————————————————————————————————————————————————
class InventarioInicial(models.Model):
    """
    Modelo: InventarioInicial
    -------------------------
      - id          : AutoField (autonumeración implícita)
      - sku         : CharField, patrón “B?????”, default="B00000"
      - categoria   : CharField (texto corto), default=""
      - producto    : CharField (texto corto), default=""
      - stock       : IntegerField (entero), default=0
      - bodega      : CharField (entero), default=""
      - comentario  : CharField (texto corto), default=""
    """

    id = models.AutoField(primary_key=True)

    sku = models.CharField(
        verbose_name="SKU",
        max_length=6,
        default="B00000",
        validators=[
            RegexValidator(
                regex=r'^B.{5}$',
                message="El SKU debe comenzar con 'B' y tener exactamente 6 caracteres."
            )
        ]
    )

    categoria = models.CharField(
        max_length=50,
        verbose_name="Categoría",
        default="",
        blank=True
    )

    producto = models.CharField(
        max_length=50,
        verbose_name="Producto",
        default="",
        blank=True 
    )

    stock = models.IntegerField(
        verbose_name="Stock",
        default=0,
        validators=[MinValueValidator(0, message="El stock no puede ser negativo.")]
    )

    bodega =  models.IntegerField(
        verbose_name="Bodega",
        default=0,
        blank=True
    )

    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        default="",
        blank=True
    )

    class Meta:
        db_table = 'inventario_inicial'
        verbose_name = 'Inventario Inicial'
        verbose_name_plural = 'Inventario Inicial'

    def __str__(self):
        return f"{self.sku} — {self.producto} (Stock: {self.stock})"

# ——————————————————————————————————————————————————————————————
# 8) Modelo: Ventas
# ——————————————————————————————————————————————————————————————

class Ventas(models.Model):
    class Meta:
            ordering = ['fecha']  # más reciente primero
    """
    Modelo: Ventas
    ----------------
      - id                           : AutoField (autonumeración implícita)
      - fecha                        : DateField (default = hoy)
      - numero_pedido                : IntegerField (default = 0)
      - comprador                    : CharField (texto corto, default = "")
      - sku                          : CharField (patrón "B?????", default = "B00000")
      - cantidad                     : IntegerField (default = 0)
      - valor_unitario_venta         : DecimalField (default = 0.00)
      - valor_envio_cobrado          : DecimalField (default = 0.00)
      - costo_unitario_venta         : DecimalField (default = 0.00)
      - total_venta                  : DecimalField (calculado = cantidad * valor_unitario_venta)
      - costo_venta                  : DecimalField (default = 0.00)
      - documento                    : CharField con opciones ("Boleta", "Otro"), default = "Otro"
      - forma_pago                   : CharField con opciones ("Contado", "A plazo"), default = "Contado"
      - numero_factura               : IntegerField (default = 0)
      - comprador_con_factura        : CharField (texto corto, default = "")
      - fecha_pago_factura           : DateField (null=True, blank=True)
      - iva_calculo                  : DecimalField (calculado = cantidad * valor_unitario_venta * 0.19/1.19)
      - iva                          : DecimalField (calculado = (documento=="Boleta") ? iva_calculo : 0)
      - venta_neta_de_iva            : DecimalField (calculado = total_venta - iva)
      - iva_envio                    : DecimalField (calculado = int(valor_envio_cobrado * 0.19/1.19))
      - cuenta_debito                : IntegerField (calculado = (forma_pago=="A plazo") ? 1010500 : 1010100)
      - debito                       : DecimalField (calculado = total_venta)
      - cuenta_credito               : IntegerField (7 dígitos, default=1000000)
      - credito                      : DecimalField (default = 0.00)
      - cuenta_debito_eerr           : IntegerField (7 dígitos, default=1000000)
      - debito_eerr                  : DecimalField (default = 0.00)
      - cuenta_credito_eerr          : IntegerField (7 dígitos, default=1000000)
      - credito_eerr                 : DecimalField (calculado = venta_neta_de_iva)
      - costo_directo                : DecimalField (default = 0.00)
      - comentario                   : CharField (texto corto, default = "")
      - credito_iva                  : DecimalField (calculado = (forma_pago=="A plazo") ? iva : iva + iva_envio)
      - cuenta_credito_iva           : IntegerField (calculado = (forma_pago=="A plazo") ? 2011311 : 2011310)
      - cuenta_debito_envio          : IntegerField (7 dígitos, default=1000000)
      - debito_envio                 : DecimalField (calculado = valor_envio_cobrado)
      - cuenta_credito_envio         : IntegerField (7 dígitos, default=1000000)
      - credito_envio                : DecimalField (calculado = valor_envio_cobrado - iva_envio)
      - venta_bruta                  : DecimalField (calculado = valor_unitario_venta * cantidad)
      - comision_flow                : DecimalField (calculado = valor_unitario_venta * 0.032 )
      - cuenta_credito_existencia    : IntegerField (7 dígitos, default=1000000)
      - cuenta_debito_costo          : IntegerField (7 dígitos, default=1000000)
      - comision_plataformas_pago    : DecimalField (calculado = total_venta * 0.32)
      - cuenta_debito_iva_plataformas: IntegerField (7 dígitos, default = 1011001)
      - debito_iva_plataformas       : DecimalField (calculado = comision_plataformas_pago * 0.19)
      - cuenta_credito_plataformas   : IntegerField (7 dígitos, default = 1010100)
      - credito_plataformas          : DecimalField (calculado = comision_plataforma_pagos)
      - cuenta_debito_plataformas    : IntegerField (7 dígitos, default = 3020200)
      - debito_´plataformas          : DecimalField (calculado = comision_plataforma_pagos* 0.81)
    """

    id = models.AutoField(primary_key=True)

    fecha = models.DateField(
        verbose_name="Fecha",
        default=timezone.now
    )

    numero_pedido = models.CharField(
        max_length=100, default="", verbose_name="Número Pedido")

    comprador = models.CharField(
        max_length=100,
        verbose_name="Comprador",
        default="",
        blank=True
    )

    sku = models.ForeignKey(
    'Catalogo',
    to_field='sku',
    on_delete=models.PROTECT
    )
    

    cantidad = models.IntegerField(
        verbose_name="Cantidad",
        default=0,
        #validators=[MinValueValidator(0, message="La cantidad no puede ser negativa.")]
    )

    valor_unitario_venta = models.IntegerField(
        verbose_name="Valor Unitario Venta",  
    )

    valor_envio_cobrado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Envío Cobrado",
        default=Decimal('0.00')
    )

    costo_unitario_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Costo Unitario Venta",
        default=Decimal('0.00')
    )

    total_venta = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Total Venta",
        editable=False,
        default=Decimal('0.00')
    )

    costo_venta = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Costo Venta",
        default=Decimal('0.00')
    )

    DOCUMENTO_CHOICES = [
        ('Boleta', 'Boleta'),
        ('Otro', 'Otro'),
    ]
    documento = models.CharField(
        max_length=20,
        verbose_name="Documento",
        choices=DOCUMENTO_CHOICES,
        default='Otro'
    )

    FORMA_PAGO_CHOICES = [
        ('Contado', 'Contado'),
        ('A plazo', 'A plazo'),
    ]
    forma_pago = models.CharField(
        max_length=20,
        verbose_name="Forma de pago",
        choices=FORMA_PAGO_CHOICES,
        default='Contado'
    )

    numero_factura = models.IntegerField(
        verbose_name="Número Factura",
        default=0,
        validators=[MinValueValidator(0, message="El número de factura no puede ser negativo.")]
    )

    comprador_con_factura = models.CharField(
        max_length=100,
        verbose_name="Comprador con Factura",
        default="",
        blank=True
    )

    fecha_pago_factura = models.DateField(
        verbose_name="Fecha Pago Factura",
        null=True,
        blank=True
    )

    comentario = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        default="",
        blank=True
    )

    # — Campos calculados (todos con editable=False y default para migraciones) —
    iva_calculo = models.IntegerField(
        
        verbose_name="IVA Cálculo",
        editable=False,
    )   
    iva = models.IntegerField(
        
        verbose_name="IVA",
        editable=False,
        
    )
    venta_neta_de_iva = models.IntegerField(
        
        verbose_name="Venta Neta de IVA",
        editable=False,
        
    )
    iva_envio = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="IVA Envío",
        editable=False,
        default=Decimal('0.00')
    )
    cuenta_debito = models.IntegerField(
        verbose_name="Cuenta Débito",
        editable=False,
        default=1010100,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    debito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito",
        editable=False,
        default=Decimal('0.00')
    )
    cuenta_credito = models.IntegerField(
        verbose_name="Cuenta Crédito",
        default=1010900,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    credito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito",
        default=Decimal('0.0')
    )
    cuenta_debito_eerr = models.IntegerField(
        verbose_name="Cuenta Débito EERR",
        default=3010200,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    debito_eerr = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito EERR",
        default=Decimal('0.0')
    )
    cuenta_credito_eerr = models.IntegerField(
        verbose_name="Cuenta Crédito EERR",
        default=3010101,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    credito_eerr = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito EERR",
        editable=False,
        default=Decimal('0.0')
    )
    costo_directo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Costo Directo",
        default=Decimal('0.0')
    )
    credito_iva = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito IVA",
        editable=False,
        default=Decimal('0.0')
    )
    cuenta_credito_iva = models.IntegerField(
        verbose_name="Cuenta Crédito IVA",
        editable=False,
        default=2011310,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    cuenta_debito_envio = models.IntegerField(
        verbose_name="Cuenta Débito Envío",
        default=1010100,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    debito_envio = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito Envío",
        editable=False,
        default=Decimal('0.00')
    )
    cuenta_credito_envio = models.IntegerField(
        verbose_name="Cuenta Crédito Envío",
        default=3010111,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    credito_envio = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito Envío",
        editable=False,
        default=Decimal('0.00')
    )
    venta_bruta = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Venta Bruta",
        editable=False,
        default=Decimal('0.00')
    )
    comision_flow = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        verbose_name="Comisión Flow",
        editable=False,
        default=Decimal('0.00')
    )
    cuenta_credito_existencia = models.IntegerField(
        verbose_name="Cuenta Crédito Existencia",
        default=1010900,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    cuenta_debito_costo = models.IntegerField(
        verbose_name="Cuenta Débito Costo",
        default=3010200,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    comision_plataformas_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Comisión Plataforma Pago",
        editable=False,
        default=Decimal('0.00')
    )
    
    cuenta_debito_iva_plataformas = models.IntegerField(
        verbose_name="Cuenta Débito IVA Plataforma",
        default=1011001,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )
    debito_iva_plataformas = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito IVA Plataforma",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_credito_plataformas = models.IntegerField(
        verbose_name="Cuenta Crédito Plataforma",
        default=1010100,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    credito_plataformas = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Crédito Plataforma",
        editable=False,
        default=Decimal('0.00')
    )

    cuenta_debito_plataformas = models.IntegerField(
        verbose_name="Cuenta Débito Plataforma",
        default=3020200,
        validators=[
            MinValueValidator(1000000, message="La cuenta debe tener exactamente 7 dígitos."),
            MaxValueValidator(9999999, message="La cuenta debe tener exactamente 7 dígitos.")
        ]
    )

    debito_plataformas = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Débito Plataforma",
        editable=False,
        default=Decimal('0.00')
    )


    class Meta:
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def save(self, *args, **kwargs):
        """
        Recalcular todos los campos derivados antes de guardar:

        1) total_venta = cantidad * valor_unitario_venta
        2) iva_calculo = cantidad * valor_unitario_venta * (0.19 / 1.19)
        3) iva = (documento == 'Boleta') ? iva_calculo : 0
        4) venta_neta_de_iva = total_venta - iva
        5) iva_envio = int(valor_envio_cobrado * (0.19 / 1.19))
        6) cuenta_debito = (forma_pago == 'A plazo') ? 1010500 : 1010100
        7) debito = total_venta
        8) credito (se deja como está; si necesitas cálculo, modifícalo manualmente)
        9) debito_eerr = venta_neta_de_iva
        10) credito_eerr = venta_neta_de_iva
        11) venta_bruta = cantidad * valor_unitario_venta
        12) comision_flow = valor_unitario_venta * 0.032 * 1.19
        12.5) cuanta_credito_plataformas = 1010100
        13) comision_plataformas_pago = comision_flow * cantidad
        14) cuenta_credito_iva = (forma_pago == 'A plazo') ? 2011311 : 2011310
        15) credito_iva = (forma_pago == 'A plazo') ? iva : (iva + iva_envio)
        16) debito_envio = valor_envio_cobrado
        17) credito_envio = valor_envio_cobrado - iva_envio
        """

        cantidad = Decimal(self.cantidad or 0)
        precio = Decimal(self.valor_unitario_venta or Decimal('0.00'))
        envio = Decimal(self.valor_envio_cobrado or Decimal('0.00'))

        # 1) comision_flow primero neto de IVA
        self.comision_flow = (self.valor_unitario_venta * Decimal('0.032') ).quantize(Decimal('0.01'))

        # 2) total_venta (usa self.comision_flow ya calculada)
        self.total_venta = (cantidad * precio).quantize(Decimal('0.01'))

        # 2) iva_calculo
        self.iva_calculo = (cantidad * precio * (Decimal('0.19') / Decimal('1.19'))).to_integral_value()  # int()

        # 3) iva
        if self.documento == 'Boleta':
            self.iva = self.iva_calculo
        else:
            self.iva = Decimal('0.00')

        # 4) venta_neta_de_iva
        self.venta_neta_de_iva = (self.total_venta - self.iva).quantize(Decimal('0.01'))

        # 5) iva_envio
        self.iva_envio = (envio * (Decimal('0.19') / Decimal('1.19'))).to_integral_value()  # int()

        # 6) cuenta_debito
        if self.forma_pago == 'A plazo':
            self.cuenta_debito = 1010500
        else:
            self.cuenta_debito = 1010100

        # 7) debito = total_venta
        self.debito = self.total_venta

        # 9) debito_eerr = venta_neta_de_iva
        self.debito_eerr = 0

        # 10) credito_eerr = venta_neta_de_iva
        self.credito_eerr = self.venta_neta_de_iva

        # 11) venta_bruta = cantidad * valor_unitario_venta
        self.venta_bruta = (cantidad * precio).quantize(Decimal('0.01'))

        # 14) cuenta_credito_iva
        if self.forma_pago == 'A plazo':
            self.cuenta_credito_iva = 2011311
        else:
            self.cuenta_credito_iva = 2011310

        # 15) credito_iva
        if self.forma_pago == 'A plazo':
            self.credito_iva = self.iva
        else:
            self.credito_iva = (self.iva + Decimal(self.iva_envio)).to_integral_value()  # int()
            
        # 16) debito_envio = valor_envio_cobrado
        self.debito_envio = envio

        # 17) credito_envio = valor_envio_cobrado - iva_envio
        self.credito_envio = (envio - Decimal(self.iva_envio)).quantize(Decimal('0.01'))

        #18) comision_plataformas_pago = total_venta * 0.032
        self.comision_plataformas_pago = (self.total_venta * (Decimal (0.032))).quantize(Decimal('0.01'))

        #18) debito_iva_plataformas = comision_plataformas_pago * 0.19
        self.debito_iva_plataformas = (self.comision_plataformas_pago * (Decimal (0.19))).quantize(Decimal('0.01'))

        #18) credito_plataformas = comision_plataformas_pago 
        self.credito_plataformas = (self.comision_plataformas_pago).quantize(Decimal('0.01'))

        #18) debito_plataformas = comision_flow * 0.81
        self.debito_plataformas = (self.comision_plataformas_pago * (Decimal(0.81)) ).quantize(Decimal('0.01'))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} — Pedido #{self.numero_pedido} — {self.sku} (Cant: {self.cantidad})"
    
        class Meta:
            ordering = ['-fecha']  # más reciente primero


# ——————————————————————————————————————————————————————————————
# 8) Modelo: Ajuste Inventario
# ——————————————————————————————————————————————————————————————

class AjusteInventario(models.Model):
    fecha = models.DateField(verbose_name="Fecha")
    sku = models.ForeignKey(
        'Catalogo',                # Asegúrate que tu modelo catálogo se llama así
        to_field='sku',
        on_delete=models.PROTECT,
        verbose_name="SKU"
    )
    cantidad = models.IntegerField(verbose_name="Cantidad")
    costo_producto = models.IntegerField(verbose_name="Costo Producto")
    cuenta_debito = models.IntegerField(verbose_name="Cuenta Débito", default=3020900)
    debito = models.IntegerField(verbose_name="Débito", default=0)
    cuenta_credito = models.IntegerField(verbose_name="Cuenta Crédito", default=1010900)
    credito = models.IntegerField(verbose_name="Crédito",default=0)

    comentario = models.CharField(
        verbose_name="Comentario",
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'ajuste_inventario'
        verbose_name = "Ajuste Inventario"
        verbose_name_plural = "Ajustes Inventario"

    def __str__(self):
        return f"{self.fecha} - {self.sku.sku} ({self.cantidad})"  

# ——————————————————————————————————————————————————————————————
# 9) Modelo: TABLA UNION CUENTAS CREDITO
# ————————————————————————————————————————————————————————

class MovimientoUnion(models.Model):
    """
    Este modelo almacenará de manera permanente la unión de los movimientos
    (OtrosGastos, SueldosHonorarios, AsientosContables).
    """

    fecha = models.DateField(verbose_name="Fecha")
    cta_credito = models.IntegerField(
        verbose_name="Cuenta Crédito",
        # Note que aquí usamos MinValueValidator y MaxValueValidator, no models.MinValueValidator
        validators=[
            MinValueValidator(1000000, message="Debe tener 7 dígitos"),
            MaxValueValidator(9999999, message="Debe tener 7 dígitos"),
        ]
    )
    monto_credito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Monto Crédito",
        default=Decimal('0.00')
    )
    texto_coment = models.CharField(
        max_length=100,
        verbose_name="Comentario",
        blank=True,
        default=""
    )
    tabla = models.CharField(
        max_length=30,
        verbose_name="Origen",
        help_text="Indica de qué tabla proviene este registro",
        default=""
    )

    class Meta:
        db_table = 'movimiento_union'
        verbose_name = 'Movimiento Unión'
        verbose_name_plural = 'Movimientos Unión'

    def __str__(self):
        return f"{self.fecha} — {self.tabla} — CTA {self.cta_credito} — Monto {self.monto_credito}"

# ——————————————————————————————————————————————————————————————
# 9) Modelo: TABLA UNION CUENTAS CREDITO
# ————————————————————————————————————————————————————————

class MovimientoUnificadoCredito(models.Model):
    fecha         = models.DateField()
    cta_credito   = models.IntegerField()
    monto_credito = models.DecimalField(max_digits=14, decimal_places=2)
    texto_coment  = models.CharField(
        max_length=100,
        blank=True,
        null=True,         # <-- permitir NULL en la base
        default=""         # <-- opcional, para que Django ponga "" en lugar de NULL
    )
    tabla_origen  = models.CharField(max_length=50)

    class Meta:
        db_table = 'union_creditos'
        verbose_name = 'Union Credito'
        verbose_name_plural = 'Union Creditos'

    def __str__(self):
        return f"{self.fecha} — {self.tabla_origen} — {self.monto_credito}"

# ——————————————————————————————————————————————————————————————
# 9) Modelo: TABLA UNION CUENTAS DEBITO
# ————————————————————————————————————————————————————————

class MovimientoUnificadoDebito(models.Model):
    
    fecha         = models.DateField()
    cta_debito    = models.IntegerField()
    monto_debito  = models.DecimalField(max_digits=14, decimal_places=2)
    texto_coment  = models.CharField(max_length=100, blank=True, null=True, default="")
    tabla_origen  = models.CharField(max_length=50)

    class Meta:
        db_table = 'union_debitos'
        verbose_name = 'Union Debito'
        verbose_name_plural = 'Union Debitos'

    def __str__(self):
        return f"{self.fecha} — {self.tabla_origen} — {self.monto_debito}"

# ——————————————————————————————————————————————————————————————
# 10) Modelo: VENTAS CONSULTA
# ——————————————————————————————————————————————————————————————

class VentasConsulta(models.Model):
    fecha = models.DateField()
    codigo_producto = models.CharField(max_length=50)
    comprador = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    total_venta = models.DecimalField(max_digits=15, decimal_places=2)
    cuenta_debito = models.IntegerField()
    debito = models.DecimalField(max_digits=15, decimal_places=2)
    cuenta_credito = models.IntegerField()
    cuenta_debito_eerr = models.IntegerField()
    debito_eerr = models.DecimalField(max_digits=15, decimal_places=2)
    cuenta_credito_eerr = models.IntegerField()
    credito_eerr = models.DecimalField(max_digits=15, decimal_places=2)
    costo_directo_producto= models.DecimalField(max_digits=15, decimal_places=2)
    comentario = models.TextField(blank=True)
    costo_venta = models.DecimalField(max_digits=15, decimal_places=2)
    categoria = models.CharField(max_length=100)
    producto = models.CharField(max_length=100)
    cuenta_debito_envio = models.IntegerField()
    credito_iva = models.DecimalField(max_digits=15, decimal_places=2)
    venta_neta_iva = models.DecimalField(max_digits=15, decimal_places=2)
    credito_envio = models.DecimalField(max_digits=15, decimal_places=2)
    debito_envio = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = "ventas_consulta"

# ——————————————————————————————————————————————————————————————
# 10) Modelo: SUMA CREDITOS
# ——————————————————————————————————————————————————————————————

class ResumenCredito(models.Model):
    cuenta_credito = models.IntegerField()
    total_credito = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'suma_creditos'
        verbose_name = 'Suma Crédito'
        verbose_name_plural = 'Suma Créditos'

    def __str__(self):
        return f"Crédito — {self.cuenta_credito}: {self.total_credito}"

# ——————————————————————————————————————————————————————————————
# 10) Modelo: SUMA DEBITOS
# ——————————————————————————————————————————————————————————————

class ResumenDebito(models.Model):
    cuenta_debito = models.IntegerField()
    total_debito = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'suma_debitos'
        verbose_name = 'Suma Débito'
        verbose_name_plural = 'Suma Débitos'

    def __str__(self):
        return f"Débito — {self.cuenta_debito}: {self.total_debito}"

    
# ——————————————————————————————————————————————————————————————
# 10) Modelo: TABLAS PARA INVENTARIO
# ——————————————————————————————————————————————————————————————

class Inventario(models.Model):
    id = models.AutoField(primary_key=True)
    cod_producto = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50)   # <- SIN tilde
    producto = models.CharField(max_length=100)
    ingresado = models.IntegerField()
    vendido = models.IntegerField()
    ajuste = models.IntegerField(null=True, blank=True)

    class Meta:
        
        db_table = 'inventario'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventario'

    def __str__(self):
        return self.producto

class InvEP(models.Model):
    id = models.AutoField(primary_key=True)
    cod_producto = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    producto = models.CharField(max_length=200)
    suma_cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=12, decimal_places=2)
    costo_neto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'invEP'

class InvVP(models.Model):
    id = models.AutoField(primary_key=True)
    cod_producto = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    producto = models.CharField(max_length=200)
    suma_cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=12, decimal_places=2)
    costo_neto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'invVP'

class InvEPVP(models.Model):
    id = models.AutoField(primary_key=True)
    cod_producto = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    producto = models.CharField(max_length=200)
    ingresado = models.IntegerField()
    vendido = models.IntegerField(null=True)
    expr2 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    costo_neto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'invEP_VP'

class inventarioactualproxy(Catalogo):
    class Meta:
        proxy = True
        verbose_name = 'inventario Actual'
        verbose_name_plural = 'inventario Actual'


# ——————————————————————————————————————————————————————————————
# 10) Modelo: TABLAS PARA INVENTARIO
# ——————————————————————————————————————————————————————————————
#from django.db import models

#class ResumenMensual(models.Model):
    #mes = models.DateField(unique=True)  # Mejor usar solo el primer día del mes, ejemplo: 2024-07-01
    #ventas = models.DecimalField(max_digits=18, decimal_places=2)
    #costos = models.DecimalField(max_digits=18, decimal_places=2)
    #utilidad = models.DecimalField(max_digits=18, decimal_places=2)
    #margen_bruto = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    #otros = models.TextField(blank=True, default="")  # Puedes ir agregando más campos si lo necesitas

    #def__str__(self):
        #return self.mes.strftime('%Y-%m')

# ——————————————————————————————————————————————————————————————
# TABLA Resumen mensual Resultados
# ——————————————————————————————————————————————————————————————

from django.db import models

# models.py
class ResumenMensual(models.Model):
    mes = models.DateField(unique=True)
    ventas = models.DecimalField(max_digits=18, decimal_places=2)
    costos = models.DecimalField(max_digits=18, decimal_places=2)
    utilidad = models.DecimalField(max_digits=18, decimal_places=2)
    margen_bruto = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    utilidad_acumulada = models.DecimalField(max_digits=18, decimal_places=2, default=0)  # NUEVO CAMPO
    otros = models.TextField(blank=True, default="")

    def __str__(self):
        return self.mes.strftime('%Y-%m')


# ——————————————————————————————————————————————————————————————
# TABLA Para Resumen mensual Resultados Detallado
# ——————————————————————————————————————————————————————————————

from django.db import models

class ResultadoMensualDetalle(models.Model):
    CONCEPTOS_BASE = [
        ("ventas", "Ventas"),
        ("costo_venta", "Costo de Venta"),
        ("gastos_comercializacion", "Gastos de Comercialización"),
        ("gastos_marketing", "Gastos Publicidad y Marketing"),
        ("gastos_arriendos", "Gastos arriendos Comisiones Tiendas"),
        ("gastos_envios", "Gastos de Envíos Adicionales"),
        ("gastos_administracion", "Gastos de Administración"),
        ("gastos_financieros", "Gastos Financieros"),
        ("depreciacion", "Depreciación del Ejercicio"),
        ("utilidad_no_operacional", "Utilidad (pérd.) No Operacional"),
        ("ajuste_monetario", "Ajuste Monetario"),
        ("impuesto_renta", "Impuesto a la Renta"),
        ("ajustes", "Ajustes"),
        # Agrega más si fuera necesario
    ]
    mes = models.DateField()  # ejemplo: 2024-01-01
    concepto = models.CharField(max_length=64, choices=CONCEPTOS_BASE)
    valor = models.IntegerField()

    class Meta:
        unique_together = ('mes', 'concepto')

    def __str__(self):
        return f"{self.get_concepto_display()} ({self.mes:%Y-%m}): {self.valor:,}"
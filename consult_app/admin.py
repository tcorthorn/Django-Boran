from django.contrib import admin
from .models import BodegaTienda, EnviosATiendas
from .models import InventarioInicialTiendas
from boran_app.admin_export_excel_mixin import ExportExcelMixin 
from .models import AjusteInventarioTienda
from boran_app.models import Catalogo


@admin.register(BodegaTienda)
class BodegaTiendaAdmin(ExportExcelMixin,admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(EnviosATiendas)
class EnviosATiendasAdmin(ExportExcelMixin, admin.ModelAdmin):
    list_display = ('id', 'fecha', 'sku', 'cantidad', 'tienda_bodega', 'comentario')
    list_filter = ('fecha', 'tienda_bodega')
    search_fields = ('sku__sku', 'tienda_bodega__nombre', 'comentario')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

@admin.register(InventarioInicialTiendas)
class InventarioInicialTiendasAdmin(ExportExcelMixin, admin.ModelAdmin):
    list_display = ('id', 'fecha', 'sku', 'tienda', 'cantidad', 'comentario')
    list_filter = ('fecha', 'tienda')
    search_fields = ('sku__sku', 'tienda__nombre', 'comentario')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

# consult_app/admin.py


@admin.register(AjusteInventarioTienda)
class AjusteInventarioTiendaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "sku", "tienda", "cantidad", "comentario_corto")
    list_filter = ("tienda", "fecha")
    search_fields = ("sku__sku", "tienda__nombre", "comentario")
    date_hierarchy = "fecha"
    ordering = ("-fecha", "tienda", "sku")
    list_select_related = ("sku", "tienda")
    list_per_page = 50
    # Quita raw_id_fields / autocomplete_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ordena las opciones de los dropdowns
        if db_field.name == "sku":
            kwargs["queryset"] = Catalogo.objects.order_by("sku")
        elif db_field.name == "tienda":
            kwargs["queryset"] = BodegaTienda.objects.order_by("nombre")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Comentario")
    def comentario_corto(self, obj):
        return (obj.comentario[:60] + "…") if obj.comentario and len(obj.comentario) > 60 else (obj.comentario or "")

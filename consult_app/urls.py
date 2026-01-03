
from django.urls import path
from . import views

urlpatterns = [
    # Productos mas Rentables
    path('resultados/', views.productos_rentables, name='productos_rentables'),
    path('exportar_excel/', views.exportar_productos_excel, name='exportar_productos_excel'),

   # Inventario Tiendas
    path("consultas/inventario-tiendas/", views.informe_inventario_tiendas, name="inventario_tiendas"),
    path("consultas/export-inventario-tiendas-xlsx/", views.exportar_inventario_tiendas_excel,  name="export_inventario_tiendas_excel"),

   # Importar Inventario Inicial Tiendas
   path("importar/inventario-inicial/", views.importar_inventario_inicial_tiendas, name="importar_inventario_inicial_tiendas"),

   # Validar cuentas contables
    path('validar-plan-cuentas/', views.validar_plan_cuentas_view, name='validar_plan_cuentas'),

  # Movimiento Cuenta Contable
    path("movimientos-cuenta/", views.movimientos_cuenta_endpoint, name="movimientos_cuenta"),
    path("movimientos-cuenta/export-xlsx/", views.export_movimientos_excel, name="exportar_movimientos_cuenta_excel"),  

  # Movimientos por FECHA 
    path("movimientos-por-fecha/", views.movimientos_por_fecha_view, name="movimientos_por_fecha"),
    path("movimientos-por-fecha/export-xlsx/", views.exportar_movimientos_fecha_excel, name="exportar_movimientos_fecha_excel"),

  # Movimientos por RANGO (agrupado por cuenta)
    path("movimientos-por-rango/", views.movimientos_por_rango_view, name="movimientos_por_rango"),
    path("movimientos-por-rango/export-xlsx/", views.exportar_movimientos_rango_excel, name="exportar_movimientos_rango_excel"),
]

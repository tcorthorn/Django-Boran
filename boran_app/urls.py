from django.urls import path
from . import views
from .views import resumen_balance_view
from .views import resumen_balance_segun_fecha_view
from .views import home

urlpatterns = [
    path('', views.home, name='home'),
    
    # Cambiar año fiscal (dos rutas: nueva y alias para compatibilidad)
    path('set-panel-year/', views.set_panel_year, name='set_panel_year'),
    path('cambiar-anno-fiscal/', views.cambiar_anno_fiscal, name='cambiar_anno_fiscal'),
    
    # Generar Balance Inicial para nuevo año
    path('generar-balance-inicial/', views.generar_balance_inicial_anno, name='generar_balance_inicial'),
    path('eliminar-balance-inicial/', views.eliminar_balance_inicial_anno, name='eliminar_balance_inicial_anno'),

    # Importar datos Balance
    path('importar-ajuste-inventario/', views.import_ajuste_inventario, name='import_ajuste_inventario'),
    path('importar-asientos-contables/', views.import_asientos_contables, name='import_asientos_contables'),
    path('importar-catalogo/', views.import_catalogo, name='import_catalogo'),
    path('importar-balance-inicial/', views.import_balance_inicial, name='import_balance_inicial'),
    path('importar-entrada-productos/', views.import_entrada_productos, name='import_entrada_productos'),
    path('importar-inventario-inicial/', views.import_inventario_inicial, name='import_inventario_inicial'),
    path('importar-sueldos/', views.import_sueldos, name='import_sueldos'),
    path('importar-ventas/', views.import_ventas, name='import_ventas'),
    path('importar-envios/', views.import_envios, name='import_envios'),
    path('importar-otros-gastos/', views.import_otros_gastos, name='import_otros_gastos'),
    path('importar-envios-a-tiendas/', views.import_envios_a_tiendas, name='import_envios_a_tiendas'),

    # Procesar datos Balance
    path('procesar-union-credito/', views.procesar_union_credito, name='procesar_union_credito'),
    path('procesar-union-debito/', views.procesar_union_debito, name='procesar_union_debito'),
    path('procesar-resumenes/', views.procesar_resumenes, name='procesar_resumenes'),
    path('procesar-ventas-consulta/', views.procesar_ventas_consulta, name='procesar_ventas_consulta'),
    path('procesar-todo/', views.procesar_todo, name='procesar_todo'),
    path('exportar-ventasconsulta-excel/', views.exportar_ventasconsulta_excel, name='exportar_ventasconsulta_excel'),

    # Procesar Inventario y Exportar datos 
    path('procesar-inventario/', views.procesar_inventario, name='procesar_inventario'),
    path('inventario/', views.inventario_actual, name='inventario_actual'),
    path('exportar-a-excel/', views.exportar_resumen_excel, name='export_a_excel'),
    path('exportar-inventario/', views.exportar_inventario_actual, name='exportar_inventario_actual'),

    # Balance
    path('balance/', views.balance_view, name='balance'),
    path('resumen_balance/', resumen_balance_view, name='resumen_balance'),
    path('balance-segun-fecha/', views.balance_segun_fecha_view, name='balance_segun_fecha'),
    path('resumen_balance_segun_fecha/', views.resumen_balance_segun_fecha_view, name='resumen_balance_segun_fecha'),

    # Resumen Financiero
    path('resumenfinanciero/', views.resumen_financiero, name='resumen_financiero'),
    path('resumenfinancierosegunfecha/', views.resumen_financiero_segun_fecha_view, name='resumen_financiero_segun_fecha'),
    path('exportar_excel_resumen_financiero/', views.exportar_excel_resumen_financiero, name='exportar_excel_resumen_financiero'),

   # Resumen mensual
    path('resumen_mensual/', views.resumen_mensual, name='resumen_mensual'),
    path('actualizar_resumen_mensual/', views.actualizar_resumen_mensual, name='actualizar_resumen_mensual'),
    path('exportar_resumen_excel/', views.exportar_resumen_excel, name='exportar_resumen_excel'),

    # Resumen detallado mensual
    path('resultados-mensuales/', views.tabla_resultados_mensual, name='tabla_resultados_mensual'),
    path('actualizar-resultados-mensuales/', views.actualizar_resultados_mensuales, name='actualizar_resultados_mensuales'),

    # Resumen ventas Tiendas
    path('resumen-ventas-tiendas/', views.resumen_ventas_tiendas_view, name='resumen_ventas_tiendas'),
    path('resumen-ventas-tiendas/excel/', views.exportar_resumen_ventas_tiendas_excel, name='exportar_resumen_ventas_tiendas_excel'),

    path("importar/", views.importar_datos, name="importar_datos"),

    # Puedes agregar más paths según tus views
]

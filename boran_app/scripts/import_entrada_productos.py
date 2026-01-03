def main():
    import os
    import sys
    import django
    import pandas as pd
    from decimal import Decimal
    from datetime import datetime

    # Configurar entorno Django
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    from boran_app.models import EntradaProductos
    catalog_model = django.apps.apps.get_model('boran_app', 'Catalogo')

    # Leer archivo Excel
    excel_path = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Entrada de productos.xlsx"
    mensajes = []
    errores = []
    objetos = []

    try:
        df = pd.read_excel(excel_path)
    except FileNotFoundError:
        return f"Error: no se encontró el archivo Excel en:\n  {excel_path}"

    # Renombrar columnas según modelo
    rename_map = {
        'Fecha': 'fecha',
        'Codigo proveedor': 'proveedor',
        'Codigo producto': 'sku',
        'Documento/ anticipo': 'documento_anticipo',
        'Cantidad ingresada': 'cantidad_ingresada',
        #'Lote': 'lote',
        'Costo confección o comprado': 'costo_con_iva',
        'Costo género en el producto': 'costo_adicional',
        'Costo unitario total producto': 'costo_unitario_total_producto',
        'Costo Total': 'costo_total',
        'IVA compra': 'iva_compra',
        'Costo neto': 'costo_neto',
        'Cuenta Débito': 'cuenta_debito',
        'Débito': 'debito',
        'Cuenta Débito IVA': 'cuenta_debito_iva',
        'Débito IVA': 'debito_iva',
        'Inventario inicio': 'inventario_inicio',
        'Cuenta Crédito': 'cuenta_credito',
        'Crédito': 'credito',
        'Cuenta Crédito género': 'cuenta_credito_genero',
        'Crédito género producto': 'credito_genero',
        'Comentario': 'comentario',
        'Numero Factura / Boleta': 'numero_factura_boleta',
        'Fecha pago Factura a plazo': 'fecha_pago_factura_plazo',
    }
    df.rename(columns=rename_map, inplace=True)

    # Funciones de conversión segura
    def safe_int(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def safe_decimal(value, default=Decimal('0.00')):
        try:
            return Decimal(value)
        except (ValueError, TypeError):
            return default

    # Preparar objetos
    for idx, row in df.iterrows():
        try:
            fecha = pd.to_datetime(row['fecha']).date()
            proveedor = safe_int(row.get('proveedor'))
            sku_code = str(row['sku']).strip()

            if not catalog_model.objects.filter(sku=sku_code).exists():
                raise ValueError(f"SKU '{sku_code}' no existe en el catálogo.")

            sku_fk = catalog_model.objects.get(sku=sku_code)

            obj = EntradaProductos(
                fecha=fecha,
                proveedor=proveedor,
                sku=sku_fk,
                documento_anticipo=row.get('documento_anticipo', 'Otro'),
                cantidad_ingresada=safe_int(row.get('cantidad_ingresada')),
                #lote=safe_int(row.get('lote')),
                costo_con_iva=safe_decimal(row.get('costo_con_iva')),
                costo_adicional=safe_decimal(row.get('costo_adicional')),
                costo_unitario_total_producto=safe_decimal(row.get('costo_unitario_total_producto')),
                costo_total=safe_decimal(row.get('costo_total')),
                iva_compra=safe_decimal(row.get('iva_compra')),
                costo_neto=safe_decimal(row.get('costo_neto')),
                cuenta_debito=safe_int(row.get('cuenta_debito')),
                debito=safe_decimal(row.get('debito')),
                cuenta_debito_iva=safe_int(row.get('cuenta_debito_iva')),
                debito_iva=safe_decimal(row.get('debito_iva')),
                inventario_inicio=row.get('inventario_inicio') or '',
                cuenta_credito=safe_int(row.get('cuenta_credito')),
                credito=safe_decimal(row.get('credito')),
                cuenta_credito_genero=safe_int(row.get('cuenta_credito_genero')),
                credito_genero=safe_decimal(row.get('credito_genero')),
                comentario=row.get('comentario') or '',
                numero_factura_boleta=safe_int(row.get('numero_factura_boleta')),
                fecha_pago_factura_plazo=pd.to_datetime(row['fecha_pago_factura_plazo']).date()
                    if not pd.isna(row['fecha_pago_factura_plazo']) else None
            )
            objetos.append(obj)

        except Exception as e:
            errores.append(f"Fila {idx+2}: {e}")

    # Insertar con bulk_create y preparar mensaje para Django
    if objetos:
        EntradaProductos.objects.bulk_create(objetos)
        mensajes.append(f"✅ {len(objetos)} registros importados exitosamente en 'EntradaProductos'.")
    else:
        mensajes.append("⚠️ No se importó ningún registro válido en EntradaProductos.")

    # Mostrar errores si los hay
    if errores:
        mensajes.append("🧨 Errores detectados:<br>" + "<br>".join(errores[:10]))
        if len(errores) > 10:
            mensajes.append(f"...y {len(errores)-10} errores más.")

    return "<br>".join(mensajes)

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
def main():
    import sys
    import os
    import django
    import pandas as pd
    from decimal import Decimal, InvalidOperation

    # --- CONFIGURA EL PATH ---
    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Ventas.xlsx"
    df = pd.read_excel(archivo_excel)

    # --- FUNCIONES DE CASTEO SEGURAS ---
    def safe_int(val, default=0):
        try:
            if pd.isna(val) or str(val).strip().lower() == 'nan':
                return default
            return int(float(val))
        except Exception:
            return default

    def safe_decimal(val, default='0.00'):
        try:
            if pd.isna(val) or str(val).strip().lower() == 'nan':
                return Decimal(default)
            # Si llega como float, str(val) lo arregla
            return Decimal(str(val).replace(',', '.'))
        except (InvalidOperation, ValueError):
            return Decimal(default)

    # --- INICIALIZA DJANGO ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGORA.settings")
    django.setup()

    # --- MODELOS ---
    from boran_app.models import Ventas, Catalogo

    # --- RENOMBRA COLUMNAS ---
    rename_map = {
        'Fecha': 'fecha',
        'Número Pedido OnLine': 'numero_pedido',
        'Comprador': 'comprador',
        'Codigo producto': 'sku',
        'Cantidad': 'cantidad',
        'Valor unitario venta': 'valor_unitario_venta',
        'Valor envio cobrado': 'valor_envio_cobrado',
        'Costo unitario venta': 'costo_unitario_venta',
        'Documento': 'documento',
        'Forma de pago': 'forma_pago',
        'Comentario': 'comentario',
    }
    df.rename(columns=rename_map, inplace=True)

    # --- LISTA DE CAMPOS DECIMAL (ajusta según tu modelo) ---
    campos_decimal = [
        'cantidad',
        'valor_unitario_venta',
        'valor_envio_cobrado',
        'costo_unitario_venta',
    ]

    # --- CAMPOS INT (id cuentas y similares) ---
    campos_int = [
        'numero_factura',
    ]

    # --- CREAR REGISTROS ---
    ventas_creadas = []
    errores = []

    for idx, row in df.iterrows():
        try:
            sku_code = str(row.get('sku')).strip()
            sku_obj = Catalogo.objects.get(sku=sku_code)

            data = {}
            # Castea todos los decimales
            for campo in campos_decimal:
                data[campo] = safe_decimal(row.get(campo)) if campo in row else Decimal('0.00')
            # Castea todos los enteros
            for campo in campos_int:
                data[campo] = safe_int(row.get(campo)) if campo in row else 0

            # Otros campos de texto
            data.update({
                'fecha': pd.to_datetime(row.get('fecha')).date() if row.get('fecha') else None,
                'numero_pedido': row.get('numero_pedido', ''),
                'comprador': row.get('comprador', ''),
                'sku': sku_obj,
                'documento': row.get('documento', 'Otro'),
                'forma_pago': row.get('forma_pago', 'Contado'),
                'comprador_con_factura': row.get('comprador_con_factura', ''),
                'fecha_pago_factura': pd.to_datetime(row.get('fecha_pago_factura')) if pd.notnull(row.get('fecha_pago_factura')) else None,
                'comentario': row.get('comentario', ''),
            })

            venta = Ventas(**data)
            venta.save()
            ventas_creadas.append(venta)

        except Catalogo.DoesNotExist:
            errores.append(f"Fila {idx+2}: SKU no existe en catálogo → {sku_code}")
        except Exception as e:
            errores.append(f"Fila {idx+2}: {e}")

    # --- REPORTE FINAL ---
    msg = f"✅ Se importaron {len(ventas_creadas)} registros a 'ventas'."
    if errores:
        msg += "\n🧨 Errores:\n" + "\n".join(errores[:10])
        if len(errores) > 10:
            msg += f"\n...y {len(errores)-10} errores más."
    return msg

if __name__ == "__main__":
    print(main())

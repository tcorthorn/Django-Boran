def main():
    import os
    import sys
    import django
    import pandas as pd
    from decimal import Decimal
    from datetime import datetime

    # --- Configurar entorno Django ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    # --- Importar modelos ---
    from boran_app.models import Envios
    catalog_model = django.apps.apps.get_model('boran_app', 'Catalogo')

    # --- Leer Excel y preparar DataFrame ---
    excel_path = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Envios.xlsx"
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        return f"Error al leer el Excel: {e}"

    # Eliminar columna 'Tienda_Bodega' si existe
    if "Tienda_Bodega" in df.columns:
        df.drop(columns=["Tienda_Bodega"], inplace=True)

    # Renombrar columnas (solo si existen)
    renames = {}
    for old, new in [('Fecha', 'fecha'), ('SKU', 'sku'), ('Cantidad', 'cantidad'), ('Comentario', 'comentario')]:
        if old in df.columns:
            renames[old] = new
    df.rename(columns=renames, inplace=True)

    # Agregar columna 'proveedor' con valor por defecto si no existe
    if 'proveedor' not in df.columns:
        df['proveedor'] = 0

    envios_objs = []
    errores = []

    for idx, row in df.iterrows():
        try:
            fecha = pd.to_datetime(row['fecha']).date()
            sku_code = str(row['sku']).strip()

            if not catalog_model.objects.filter(sku=sku_code).exists():
                raise ValueError(f"SKU '{sku_code}' no existe en catálogo.")

            sku_fk = catalog_model.objects.get(sku=sku_code)

            envio = Envios(
                fecha=fecha,
                sku=sku_fk,
                cantidad=int(row['cantidad'] or 0),
                comentario=row.get('comentario') or '',
                proveedor=int(row['proveedor'])
            )
            envios_objs.append(envio)
        except Exception as e:
            errores.append(f"Fila {idx+2}: {e}")

    # Guardar en la base de datos
    if envios_objs:
        Envios.objects.bulk_create(envios_objs)
        msg = f"✅ {len(envios_objs)} registros importados exitosamente en 'envios'."
    else:
        msg = "No hay registros válidos para importar."

    # Reportar errores si los hay (agrega a mensaje)
    if errores:
        msg += "<br>🧨 Errores detectados:<br>" + "<br>".join(errores[:10])
        if len(errores) > 10:
            msg += f"<br>...y {len(errores)-10} errores más."

    return msg

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
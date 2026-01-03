def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime
    from django.db import transaction
    from boran_app.models import Catalogo
    from consult_app.models import EnviosATiendas, BodegaTienda

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Envios a Tiendas.xlsx"

    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return f"Error: No se encontró el archivo Excel en: {archivo_excel}"

    # Normalización básica
    req_cols = {"Fecha", "SKU", "Cantidad", "Tienda/Bodega"}
    if not req_cols.issubset(set(df.columns)):
        faltan = req_cols - set(df.columns)
        return f"Error: Al Excel le faltan columnas: {', '.join(faltan)}"

    df["SKU"] = df["SKU"].astype(str).str.strip().str.upper()
    df["Tienda/Bodega"] = df["Tienda/Bodega"].astype(str).str.strip()
    # fuerza enteros (NaN -> 0 y luego int)
    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0).astype(int)

    skus = set(df["SKU"].dropna().unique())
    tiendas = set(df["Tienda/Bodega"].dropna().unique())

    # Mapas para resolver claves rápidas (sin traer instancias enteras)
    # Catalogo.sku es unique=True, y tenemos to_field='sku' en el FK
    skus_existentes = set(
        Catalogo.objects.filter(sku__in=skus).values_list("sku", flat=True)
    )

    tienda_map = dict(
        BodegaTienda.objects.filter(nombre__in=tiendas).values_list("nombre", "id")
    )

    errores = []
    objetos = []

    for i, row in df.iterrows():
        fila_excel = i + 2  # header en fila 1
        # Fecha
        fecha_val = row["Fecha"]
        try:
            if not isinstance(fecha_val, datetime):
                fecha_val = pd.to_datetime(fecha_val)
            fecha_val = fecha_val.date()
        except Exception:
            errores.append(f"Fila {fila_excel}: Fecha inválida '{row['Fecha']}'")
            continue

        sku_val = row["SKU"]
        if sku_val not in skus_existentes:
            errores.append(f"Fila {fila_excel}: SKU '{sku_val}' no existe en Catalogo.")
            continue

        tienda_nombre = row["Tienda/Bodega"]
        tienda_id = tienda_map.get(tienda_nombre)
        if not tienda_id:
            errores.append(f"Fila {fila_excel}: Tienda '{tienda_nombre}' no existe en BodegaTienda.")
            continue

        cantidad_val = int(row["Cantidad"])
        comentario = row.get("Comentario", "") or ""

        try:
            objetos.append(
                EnviosATiendas(
                    fecha=fecha_val,
                    sku_id=sku_val,               # <- ¡clave!: asigna por to_field (sku)
                    tienda_bodega_id=tienda_id,   # <- id directo
                    cantidad=cantidad_val,
                    comentario=comentario,
                )
            )
        except Exception as e:
            errores.append(f"Fila {fila_excel}: {e}")

    if not objetos and not errores:
        return "No hay registros válidos para importar."

    msg = ""
    if objetos:
        with transaction.atomic():
            EnviosATiendas.objects.bulk_create(objetos, batch_size=1000)
        msg = f"✅ {len(objetos)} registros importados exitosamente en EnviosATiendas."
    else:
        msg = "No hay registros válidos para importar."

    if errores:
        msg += "<br>🧨 Errores detectados:<br>" + "<br>".join(errores[:10])
        if len(errores) > 10:
            msg += f"<br>...y {len(errores)-10} errores más."

    return msg

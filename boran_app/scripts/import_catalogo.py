def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime
    from decimal import Decimal, InvalidOperation
    import tkinter as tk  # 👈 Importamos el módulo completo
    from tkinter import messagebox  # 👈 Importamos messagebox

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGORA.settings")
    django.setup()

    from boran_app.models import Catalogo

    archivo_excel = r"C:\Users\tcort\OneDrive\BORANGORA\Django-Boran\Catalogo de productos.xlsx"
    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo Excel en:\n  {archivo_excel}")
        sys.exit(1)

    print("Columnas leídas del Excel:")
    print(df.columns.tolist())

    skus_archivo = set(df["COD PRODUCTO"].astype(str))
    skus_bd = set(Catalogo.objects.filter(sku__in=skus_archivo).values_list('sku', flat=True))
    nuevos_skus = skus_archivo - skus_bd

    cantidad_importada = 0

    for idx, row in df.iterrows():
        sku_val = str(row["COD PRODUCTO"]).upper()
        if sku_val not in nuevos_skus:
            continue  # Omitir si ya existe

        try:
            costo_base = row["Costo confección o comprado"]
            costo_adicional = row["Costo adicional"]
            print(f"[Fila {idx+2}] SKU: {sku_val}, costo_base: {costo_base}, costo_adicional: {costo_adicional}")

            # Forzamos a decimal:
            try:
                costo_base = Decimal(str(costo_base).replace(",", ".").strip())
            except Exception as e:
                print(f"Error convirtiendo costo_base: {e}")
                costo_base = Decimal("0.00")
            try:
                costo_adicional = Decimal(str(costo_adicional).replace(",", ".").strip())
            except Exception as e:
                print(f"Error convirtiendo costo_adicional: {e}")
                costo_adicional = Decimal("0.00")

            fecha_val = row["Fecha Ingreso"]
            if not isinstance(fecha_val, datetime):
                fecha_val = pd.to_datetime(fecha_val, errors='coerce')
            if pd.isnull(fecha_val):
                raise ValueError(f"Fecha Ingreso vacía o inválida en fila {idx + 2}.")
            fecha_val = fecha_val.date()

            clase_producto = str(row.get("Clase de producto", "") or "")
            categoria      = str(row.get("Categoría", "") or "")
            producto       = str(row.get("Producto", "") or "")
            cod_proveedor  = str(row.get("Codigo proveedor", "") or "")
            descripcion    = str(row.get("Descripción", "") or "")
            comentario     = str(row.get("Comentario", "") or "")

            obj = Catalogo(
                fecha_ingreso=fecha_val,
                sku=sku_val,
                clase_producto=clase_producto,
                categoria=categoria,
                producto=producto,
                cod_proveedor=cod_proveedor,
                descripcion=descripcion,
                costo_base=costo_base,
                costo_adicional=costo_adicional,
                comentario=comentario,
            )
            
            obj.save()
            print(f"--> costo_directo_producto calculado: {obj.costo_directo_producto}")
            cantidad_importada += 1

        except Exception as e:
            print(f"Error en fila {idx + 2}: {e}")
            
            
    if cantidad_importada > 0:
            print(f"{cantidad_importada} nuevos SKUs importados en Catálogo.")
    else:
            print("No hay nuevos SKUs importados.")

   
if __name__ == "__main__":
    main()

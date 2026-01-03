def main():
    import os
    import sys
    import django
    import pandas as pd
    from decimal import Decimal

    # 1) Agregar la carpeta raíz del proyecto al PYTHONPATH
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)

    # 2) Configurar entorno Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    # 3) Importar el modelo
    from boran_app.models import InventarioInicial

    # 4) Leer el Excel
    archivo_excel = r"C:\Users\tcort\OneDrive\BORANGORA\Django\Otros\Inventario inicial Total.xlsx"
    mensajes = []
    errores = []
    objetos = []

    try:
        df = pd.read_excel(archivo_excel, sheet_name="Inventario Inicial Total")
    except Exception as e:
        return f"Error: no se pudo abrir el archivo Excel: {e}"

    # 5) Recorrer el DataFrame y crear instancias
    for idx, row in df.iterrows():
        try:
            sku_val = row.get("SKU", "")
            producto_val = row.get("Producto", "")
            stock_val = int(row.get("Stock", 0) or 0)
            bodega_val = row.get("Bodega", "")
            comentario_val = row.get("Comentario", "")

            obj = InventarioInicial(
                sku=sku_val,
                producto=producto_val,
                stock=stock_val,
                bodega=bodega_val,
                comentario=comentario_val
            )
            objetos.append(obj)
        except Exception as e:
            errores.append(f"Fila {idx+2}: {e}")

    # 6) Guardar todo de una vez con bulk_create
    if objetos:
        InventarioInicial.objects.bulk_create(objetos)
        mensajes.append(f"✅ {len(objetos)} registros importados en InventarioInicial.")
    else:
        mensajes.append("⚠️ No se importó ningún registro válido en InventarioInicial.")

    if errores:
        mensajes.append("🧨 Errores detectados:<br>" + "<br>".join(errores[:10]))
        if len(errores) > 10:
            mensajes.append(f"...y {len(errores)-10} errores más.")

    return "<br>".join(mensajes)

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
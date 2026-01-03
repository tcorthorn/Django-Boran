import pandas as pd

# Cambia la ruta si es necesario
df = pd.read_excel(r"C:\Users\tcort\OneDrive\BORANGORA\Django\Otros\Ventas.xlsx")
print("Columnas:", df.columns.tolist())
print("Filas leídas:", len(df))
print(df.head())

errores = []
for idx, row in df.iterrows():
    print(f"Fila {idx+2}: SKU={row.get('Codigo producto')}, Fecha={row.get('Fecha')}")
    try:
        sku_val = row.get('Codigo producto')
        if sku_val is None:
            raise ValueError("SKU vacío")
        # SOLO PRUEBA: no importa en Django aún
        print(f"Intentando buscar en Catalogo: {sku_val}")
        # Si quieres probar en Django shell, descomenta la siguiente línea:
        # obj = Catalogo.objects.get(sku=sku_val)
    except Exception as e:
        print(f"Error fila {idx+2}: {e}")
        errores.append(f"Fila {idx+2}: {e}")

print("Errores:", len(errores))
for err in errores:
    print(err)

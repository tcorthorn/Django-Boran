import sqlite3

# Ruta a tu base de datos
ruta_db = r'C:\Users\tcort\OneDrive\BORANGORA\Django-Boran\BORANGO.db'

# Lista de tablas que quieres vaciar
tablas_a_borrar = [
    #'ajuste_inventario',
    #'asientos_contables',
    #'balance_inicial',
    'entrada_productos',
    #'envios',
    #'inventario_inicial',
    #'movimiento_union',
    #'otros_gastos',
    #'sueldos',
    #'boran_app_catalogo',
    #'ventas'
    #c:\Users\tcort\OneDrive\Respaldo Django-Boran\18-07\boran_app\scripts\import_catalogo.py'ventas',

    # Añade más tablas aquí
]

conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Opcional: Verificar si la tabla existe antes de intentar borrar
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tablas_existentes = set(row[0] for row in cursor.fetchall())

for tabla in tablas_a_borrar:
    if tabla in tablas_existentes:
        cursor.execute(f'DELETE FROM "{tabla}";')
        print(f"[OK] Borrados todos los valores de la tabla: {tabla}")
    else:
        print(f"[ADVERTENCIA] La tabla '{tabla}' no existe en la base de datos.")

conn.commit()
conn.close()
print("¡Datos borrados solo de las tablas seleccionadas!")

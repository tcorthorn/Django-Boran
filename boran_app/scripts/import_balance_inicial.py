def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    from boran_app.models import BalanceInicial

    archivo_excel = r"C:\Users\tcort\OneDrive\BORANGORA\Django\Otros\Cuentas ajuste inicial.xlsx"
    mensajes = []
    errores = []
    objetos = []

    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return f"Error: no se encontró el archivo Excel en:\n  {archivo_excel}"

    # — Columnas Excel (opcional)
    # mensajes.append("Columnas leídas del Excel: " + ", ".join(df.columns.tolist()))

    # — Eliminar columnas H–L si existen
    if df.shape[1] >= 12:
        columnas_a_eliminar = df.columns[7:12]  # índice 7,8,9,10,11
        df = df.drop(columns=columnas_a_eliminar, errors="ignore")
        mensajes.append(f"Se eliminaron las columnas: {list(columnas_a_eliminar)}")
    else:
        mensajes.append("Advertencia: el archivo tiene menos de 12 columnas, no se eliminaron columnas H–L.")

    # — Procesar filas
    for idx, row in df.iterrows():
        try:
            fecha_val = row["Fecha"]
            if not isinstance(fecha_val, datetime):
                fecha_val = pd.to_datetime(fecha_val)
            fecha_val = fecha_val.date()
            cta_debito_val = str(row["Cuenta Débito"])
            debito_val     = row["Monto Débito"]
            cta_credito_val= str(row["Cuenta Crédito"])
            credito_val    = row["Monto Crédito"]
            comentario_val = row.get("Comentario", "") or ""

            obj = BalanceInicial(
                fecha=fecha_val,
                cuenta_debito=cta_debito_val,
                debito=debito_val,
                cuenta_credito=cta_credito_val,
                credito=credito_val,
                comentario=comentario_val
            )
            objetos.append(obj)

        except KeyError as ke:
            errores.append(f"Fila {idx + 2}: columna no encontrada: {ke}")
        except Exception as e:
            errores.append(f"Fila {idx + 2}: {e}")

    # — Bulk create y mensajes
    if objetos:
        BalanceInicial.objects.bulk_create(objetos)
        mensajes.append(f"✅ {len(objetos)} registros importados en BalanceInicial.")
    else:
        mensajes.append("No hay registros válidos para importar.")

    # — Errores, si hubo
    if errores:
        mensajes.append("🧨 Errores detectados:<br>" + "<br>".join(errores[:10]))
        if len(errores) > 10:
            mensajes.append(f"...y {len(errores) - 10} errores más.")

    return "<br>".join(mensajes)

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
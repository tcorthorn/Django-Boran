def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORAN.settings")
    django.setup()

    from boran_app.models import AsientosContables


    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Asientos contables.xlsx"

    errores = []
    objetos = []

    # Lee el Excel y revisa errores de apertura
    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return f"Error: No se encontró el archivo Excel en: {archivo_excel}"

    # Verifica columnas leídas (sólo para debug, puedes comentar la línea)
    # columnas_excel = df.columns.tolist()

    # Procesa cada fila
    for idx, row in df.iterrows():
        try:
            fecha_val = row["Fecha"]
            if not isinstance(fecha_val, datetime):
                fecha_val = pd.to_datetime(fecha_val)

            monto_val    = row["Monto"]
            debito_val   = row["Débito"]
            cta_debito   = str(row["Cuenta Débito"])
            credito_val  = row["Crédito"]
            cta_credito  = str(row["Cuenta Crédito"])
            comentario   = row.get("Comentario", "") or ""

            obj = AsientosContables(
                fecha=fecha_val.date(),
                monto=monto_val,
                debito=debito_val,
                cuenta_debito=cta_debito,
                credito=credito_val,
                cuenta_credito=cta_credito,
                comentario=comentario
            )
            objetos.append(obj)
        except Exception as e:
            errores.append(f"Fila {idx + 2}: {e}")

    # Bulk create y mensajes
    msg = ""
    if objetos:
        AsientosContables.objects.bulk_create(objetos)
        msg = f"✅ {len(objetos)} registros importados exitosamente en AsientosContables."
    else:
        msg = "No hay registros válidos para importar."

    if errores:
        msg += "<br>🧨 Errores detectados:<br>" + "<br>".join(errores[:10])
        if len(errores) > 10:
            msg += f"<br>...y {len(errores)-10} errores más."

    return msg

# Si ejecutas desde línea de comando:
if __name__ == "__main__":
    print(main())
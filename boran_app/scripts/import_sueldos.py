def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime

    # 1) Agregar la carpeta raíz del proyecto (donde está manage.py) al PYTHONPATH
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)

    # 2) Decirle a Django dónde están los settings de tu proyecto
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    # 3) Importar el modelo destino
    from boran_app.models import SueldosHonorarios

    # 4) Leer el Excel
    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Sueldos y honorarios.xlsx"
    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return f"Error: no se encontró el archivo Excel en:\n  {archivo_excel}"
    except Exception as e:
        return f"Error al leer Excel: {e}"

    # 5) Eliminar columnas innecesarias
    df = df.drop(columns=["Rut", "Dirección", "Comuna", "Ciudad"], errors="ignore")

    # 6) Preparar lista de instancias y de errores
    objetos = []
    errores = []

    for idx, row in df.iterrows():
        try:
            fecha_val = row["Fecha"]
            if not isinstance(fecha_val, datetime):
                fecha_val = pd.to_datetime(fecha_val)
            fecha_val = fecha_val.date()

            tipo_rem   = row["Tipo remuneración"]
            monto_tot  = row["Monto total pagado"]
            retenciones = row["Retenciones"]
            nombre     = row["Comentario"]
            cta_deb    = str(row["Cuenta Débito"])
            debito_val = row["Débito"]
            cta_cred   = str(row["Cuenta Crédito"])
            credito_val= row["Crédito"]
            cta_cred2  = str(row["Cuenta Crédito 2"])
            credito2   = row["Crédito 2"]
            comentario = row.get("Comentario", "") or ""

            obj = SueldosHonorarios(
                fecha=fecha_val,
                tipo_remuneracion=tipo_rem,
                monto_total_pagado=monto_tot,
                retenciones=retenciones,
                nombre=nombre,
                cuenta_debito=cta_deb,
                debito=debito_val,
                cuenta_credito=cta_cred,
                credito=credito_val,
                cuenta_credito2=cta_cred2,
                credito2=credito2,
                comentario=comentario
            )
            objetos.append(obj)

        except Exception as e:
            errores.append(f"Error en fila {idx + 2}: {e}")

    # 7) Insertar y construir mensaje
    mensajes = []
    if objetos:
        SueldosHonorarios.objects.bulk_create(objetos)
        mensajes.append(f"✅ {len(objetos)} registros importados en SueldosHonorarios.")
    else:
        mensajes.append("⚠️ No hay registros válidos para importar.")

    if errores:
        mensajes.append("🧨 Errores:<br>" + "<br>".join(errores[:10]))
        if len(errores) > 10:
            mensajes.append(f"...y {len(errores)-10} errores más.")

    return "<br>".join(mensajes)

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
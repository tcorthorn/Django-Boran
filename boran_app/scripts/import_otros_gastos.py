def main():
    import os
    import sys
    import django
    import pandas as pd
    from decimal import Decimal
    from django.core.exceptions import ValidationError

    # 1) Agregar la carpeta del proyecto al PYTHONPATH
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)

    # 2) Configurar entorno Django
    django.setup()

    # 3) Importar modelo
    from boran_app.models import OtrosGastos

    # 4) Leer Excel
    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Otros gastos.xlsx"
    nombre_hoja = "Otros gastos"

    try:
        df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    except Exception as e:
        return f"Error al leer el archivo Excel: {e}"

    objetos = []
    errores = []

    for idx, row in df.iterrows():
        fila_num = idx + 2
        try:
            fecha_val = row.get("Fecha")
            if pd.isna(fecha_val):
                raise ValueError("El campo 'Fecha' no puede estar vacío.")

            otros_val = row.get("OTROS GASTOS")
            if pd.isna(otros_val) or otros_val == "":
                otros_val = "Otros"

            total_raw = row.get("Total")
            total_val = Decimal(str(total_raw)) if not pd.isna(total_raw) else Decimal("0.00")

            iva_raw = row.get("IVA")
            iva_val = Decimal(str(iva_raw)) if not pd.isna(iva_raw) else Decimal("0.00")

            monto_neto_raw = row.get("Monto neto")
            monto_neto_val = Decimal(str(monto_neto_raw)) if not pd.isna(monto_neto_raw) else (total_val - iva_val).quantize(Decimal("0.01"))

            cta_debito_raw = row.get("Cuenta Débito")
            cta_debito_val = str(int(cta_debito_raw)).zfill(7) if not pd.isna(cta_debito_raw) else "1011001"

            debito_raw = row.get("Débito")
            debito_val = Decimal(str(debito_raw)) if not pd.isna(debito_raw) else Decimal("0.00")

            cta_credito_raw = row.get("Cuenta Crédito")
            cta_credito_val = str(int(cta_credito_raw)).zfill(7) if not pd.isna(cta_credito_raw) else "1010100"

            credito_raw = row.get("Crédito")
            credito_val = Decimal(str(credito_raw)) if not pd.isna(credito_raw) else Decimal("0.00")

            comentario_raw = row.get("Comentario")
            comentario_val = comentario_raw if pd.notna(comentario_raw) else ""

            cta_debito_eerr_raw = row.get("Cuenta Débito EERR")
            cta_debito_eerr_val = str(int(cta_debito_eerr_raw)).zfill(7) if not pd.isna(cta_debito_eerr_raw) else "2010500"

            debito_eerr_raw = row.get("Débito EERR")
            debito_eerr_val = Decimal(str(debito_eerr_raw)) if not pd.isna(debito_eerr_raw) else monto_neto_val

            obj = OtrosGastos(
                fecha=fecha_val,
                otros_gastos=otros_val,
                total=total_val,
                iva=iva_val,
                monto_neto=monto_neto_val,
                cuenta_debito=cta_debito_val,
                debito=debito_val,
                cuenta_credito=cta_credito_val,
                credito=credito_val,
                comentario=comentario_val,
                cuenta_debito_eerr=cta_debito_eerr_val,
                debito_eerr=debito_eerr_val
            )
            # Validar
            obj.full_clean()
            objetos.append(obj)

        except ValidationError as ve:
            errores.append(f"Fila {fila_num}: validación → {ve.message_dict}")
        except Exception as e:
            errores.append(f"Fila {fila_num}: excepción → {str(e)}")

    mensajes = []
    if objetos:
        OtrosGastos.objects.bulk_create(objetos)
        mensajes.append(f"✅ {len(objetos)} registros importados en OtrosGastos.")
    else:
        mensajes.append("⚠️ No hay registros válidos para insertar en OtrosGastos.")

    if errores:
        mensajes.append("🧨 Errores detectados:<br>" + "<br>".join(errores[:10]))
        if len(errores) > 10:
            mensajes.append(f"...y {len(errores)-10} errores más.")

    return "<br>".join(mensajes)

# Solo si quieres ejecutar desde línea de comando:
if __name__ == "__main__":
    print(main())
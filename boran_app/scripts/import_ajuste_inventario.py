def main():
    import os
    import sys
    import django
    import pandas as pd
    from datetime import datetime

    # Apuntar a la raíz del proyecto (dos niveles arriba)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    # Configurar settings de Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BORANGO.settings")
    django.setup()

    from django.conf import settings
    from boran_app.models import AjusteInventario, Catalogo

    # DEBUG: ver qué base de datos está usando el script
    print("Base de datos usada por este script:")
    print("  ENGINE:", settings.DATABASES["default"]["ENGINE"])
    print("  NAME  :", settings.DATABASES["default"]["NAME"])
    print()

    # Ruta del archivo Excel
    archivo_excel = r"C:\Users\Thomas\OneDrive\BORANGORA\Django-Boran\Otros\Ajuste inventario.xlsx"

    try:
        df = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        return f"Error: no se encontró el archivo Excel en:\n  {archivo_excel}"

    columnas = df.columns.tolist()
    requeridas = [
        "Fecha",
        "Código producto",
        "Cantidad",
        "Costo producto",
        "Cuenta Débito",
        "Débito",
        "Cuenta Crédito",
        "Crédito",
        "Comentario",
    ]
    faltantes = [col for col in requeridas if col not in columnas]
    if faltantes:
        return f"Error: faltan las columnas requeridas en el Excel: {faltantes}"

    # Función auxiliar para tratar números que pueden venir como NaN o vacío
    def entero_o_cero(valor, nombre_campo, fila):
        """
        Convierte el valor a int.
        Si viene NaN o "" lo devuelve como 0.
        Si no se puede convertir, lanza excepción con mensaje claro.
        """
        if pd.isna(valor) or valor == "":
            return 0
        try:
            return int(valor)
        except Exception as e:
            print(f"Error convirtiendo '{nombre_campo}' en fila {fila}: {valor!r} -> {e}")
            raise

    objetos = []
    errores = 0
    skus_no_encontrados = []

    for idx, row in df.iterrows():
        fila_excel = idx + 2  # considerando encabezados en la fila 1

        try:
            # --- FECHA ---
            fecha = row["Fecha"]
            if not isinstance(fecha, datetime):
                fecha = pd.to_datetime(fecha)
            fecha = fecha.date()

            # --- SKU: normalización y búsqueda en catálogo ---
            valor_sku = row["Código producto"]
            print(f"DEBUG fila {fila_excel}: bruto 'Código producto' = {valor_sku!r} (tipo {type(valor_sku)})")

            # Si la celda viene vacía o NaN
            if pd.isna(valor_sku):
                skus_no_encontrados.append(("VACÍO/NaN", fila_excel))
                errores += 1
                print(f"    -> SKU vacío/NaN, se omite fila {fila_excel}")
                continue

            # Normalizar: string, sin espacios, en mayúsculas
            sku = str(valor_sku).strip().upper()
            print(f"    -> SKU normalizado = {sku!r}")

            try:
                # Buscar ignorando mayúsculas/minúsculas
                sku_obj = Catalogo.objects.get(sku__iexact=sku)
                print(f"    -> Encontrado en Catalogo: {sku_obj.sku!r}")
            except Catalogo.DoesNotExist:
                skus_no_encontrados.append((sku, fila_excel))
                errores += 1
                print(f"    -> NO encontrado en Catalogo, se omite fila {fila_excel}")
                continue

            # --- CAMPOS NUMÉRICOS ---
            cantidad = entero_o_cero(row["Cantidad"], "Cantidad", fila_excel)
            costo_producto = entero_o_cero(row["Costo producto"], "Costo producto", fila_excel)
            cuenta_debito = entero_o_cero(row["Cuenta Débito"], "Cuenta Débito", fila_excel)
            debito = entero_o_cero(row["Débito"], "Débito", fila_excel)
            cuenta_credito = entero_o_cero(row["Cuenta Crédito"], "Cuenta Crédito", fila_excel)
            credito = entero_o_cero(row["Crédito"], "Crédito", fila_excel)

            # --- COMENTARIO ---
            comentario_bruto = row.get("Comentario", "")
            if pd.isna(comentario_bruto):
                comentario = ""
            else:
                comentario = str(comentario_bruto)

            # Crear instancia (sin guardar aún)
            obj = AjusteInventario(
                fecha=fecha,
                sku=sku_obj,
                cantidad=cantidad,
                costo_producto=costo_producto,
                cuenta_debito=cuenta_debito,
                debito=debito,
                cuenta_credito=cuenta_credito,
                credito=credito,
                comentario=comentario,
            )
            objetos.append(obj)

        except KeyError as ke:
            errores += 1
            print(f"Error de columna en fila {fila_excel}: {ke}")
        except Exception as e:
            errores += 1
            print(f"Error inesperado en fila {fila_excel}: {e}")

    # --- RESULTADO FINAL ---
    if objetos:
        AjusteInventario.objects.bulk_create(objetos)
        msg = f"{len(objetos)} registros importados en AjusteInventario."

        if skus_no_encontrados:
            msg += (
                f" {len(skus_no_encontrados)} filas fueron omitidas por SKU no encontrado en el catálogo: "
                + ", ".join(f"{sku} (fila {fila})" for sku, fila in skus_no_encontrados)
            )

        if errores and errores > len(skus_no_encontrados):
            msg += f" Además se produjeron {errores - len(skus_no_encontrados)} errores adicionales (formato/valores)."

        return msg
    else:
        if skus_no_encontrados and errores == len(skus_no_encontrados):
            return (
                "No hay registros válidos para importar. "
                "Todas las filas fueron omitidas porque el SKU no se encontró en el catálogo: "
                + ", ".join(f"{sku} (fila {fila})" for sku, fila in skus_no_encontrados)
            )
        elif errores > 0:
            return (
                f"No hay registros válidos para importar. "
                f"Se produjeron {errores} errores (valores vacíos, NaN o formatos incorrectos)."
            )
        else:
            return "No hay registros válidos para importar."


if __name__ == "__main__":
    print("Iniciando script de importación de Ajuste de Inventario...")
    respuesta = input('¿Está seguro de importar Ajuste de Inventario?\nEscriba "SI" para continuar: ').strip().upper()
    if respuesta == "SI":
        print("Importando, por favor espere...\n")
        print(main())
    else:
        print("Importación cancelada.")


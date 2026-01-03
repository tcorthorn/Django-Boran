
def main():
    import sqlite3
    import pandas as pd
    import xlwings as xw

    def exportar_a_excel():
        try:
            # Hardcodea las rutas para que funcione desde Django:
            excel_path = r'C:\Users\tcort\OneDrive\BORANGORA\Django\Otros\GestionBoranX.xlsm'
            sheet_name = 'Datos'
            db_path = r'C:\Users\tcort\OneDrive\BORANGORA\Django\BORAN.db'  # <-- usa la de settings si puedes

            conn = sqlite3.connect(db_path)

            queries = {
                'union_debitos': "SELECT fecha, cta_debito, monto_debito FROM union_debitos;",
                'union_creditos': "SELECT fecha, cta_credito, monto_credito FROM union_creditos;",
                'suma_debitos': "SELECT cuenta_debito, total_debito FROM suma_debitos;",
                'suma_creditos': "SELECT cuenta_credito, total_credito FROM suma_creditos;"
            }

            df_debitos = pd.read_sql_query(queries['union_debitos'], conn)
            df_debitos['monto_debito'] = df_debitos['monto_debito'].round().astype('Int64')

            df_creditos = pd.read_sql_query(queries['union_creditos'], conn)
            df_creditos['monto_credito'] = df_creditos['monto_credito'].round().astype('Int64')

            df_suma_debitos = pd.read_sql_query(queries['suma_debitos'], conn)
            df_suma_debitos['total_debito'] = df_suma_debitos['total_debito'].round().astype('Int64')

            df_suma_creditos = pd.read_sql_query(queries['suma_creditos'], conn)
            df_suma_creditos['total_credito'] = df_suma_creditos['total_credito'].round().astype('Int64')

            # 3. Abrir y escribir en Excel (sin macros)
            app = xw.App(visible=False)
            wb = xw.Book(excel_path)
            ws = wb.sheets[sheet_name]

            for col in ['A', 'B', 'C', 'E', 'F', 'G', 'J', 'K', 'L', 'M']:
                ws.range(f'{col}2:{col}1048576').clear_contents()

            if not df_debitos.empty:
                ws.range('A2').options(index=False, header=False).value = df_debitos
            if not df_creditos.empty:
                ws.range('E2').options(index=False, header=False).value = df_creditos
            if not df_suma_debitos.empty:
                ws.range('J2').options(index=False, header=False).value = df_suma_debitos
            if not df_suma_creditos.empty:
                ws.range('L2').options(index=False, header=False).value = df_suma_creditos

            wb.save()
            wb.close()
            app.quit()
            return "✅ Datos exportados correctamente y las macros/botones se mantienen intactos."

        except Exception as e:
            return f"🧨 Error durante la exportación: {str(e)}"

if __name__ == "__main__":
    print(main())   
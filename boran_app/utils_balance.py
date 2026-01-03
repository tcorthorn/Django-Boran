# boran_app/utils_balance.py

from datetime import date
from .models import ResumenDebito, ResumenCredito
from .cod_cuentas_balance import balance_rows

def intdot(val):
    try:
        val_float = float(val)
        val_int = int(round(val_float))
        return f"{val_int:,}".replace(",", ".")
    except Exception:
        return ""

def obtener_matriz_balance():
    debitos_dict = {d.cuenta_debito: float(d.total_debito) for d in ResumenDebito.objects.all()}
    creditos_dict = {c.cuenta_credito: float(c.total_credito) for c in ResumenCredito.objects.all()}
    matriz_balance = []

    for fila in balance_rows:
        codigo = fila['codigo']
        nombre = fila['nombre']
        debito = debitos_dict.get(codigo, 0)
        credito = creditos_dict.get(codigo, 0)
        saldo_deudor = saldo_acreedor = activo = pasivo = perdidas = ganancias = 0

        if 1010100 <= codigo <= 2040000:
            saldo_deudor = debito - credito if debito > credito else 0
            saldo_acreedor = credito - debito if credito > debito else 0
            activo = saldo_deudor
            pasivo = saldo_acreedor
        elif 3010100 <= codigo <= 3010300:
            saldo_deudor = debito - credito if debito > credito else 0
            saldo_acreedor = credito - debito if credito > debito else 0
            perdidas = saldo_deudor
            ganancias = saldo_acreedor

        matriz_balance.append({
            'codigo': codigo,
            'nombre': nombre,
            'debito': intdot(debito),
            'credito': intdot(credito),
            'saldo_deudor': intdot(saldo_deudor),
            'saldo_acreedor': intdot(saldo_acreedor),
            'activo': intdot(activo),
            'pasivo': intdot(pasivo),
            'perdidas': intdot(perdidas),
            'ganancias': intdot(ganancias)
        })

    return matriz_balance

#------------------------------------------
 # RESUMEN RESULTADOS DETALLADOS
#------------------------------------------

from boran_app.models import (
    ResultadoMensualDetalle,
    MovimientoUnificadoCredito,
    MovimientoUnificadoDebito
)
# Importa tus funciones utilitarias de procesamiento aquí
from .utils import (
    regenerar_ventas_consulta,
    poblar_movimientos_unificados_credito,
    poblar_movimientos_unificados_debito,
    regenerar_resumenes_credito_debito, 
)
from datetime import date
from collections import defaultdict

# Mapping con naturaleza
CONCEPTOS_CUENTAS = {
    "ventas": {
        "codigos": [3010101, 3010111],
        "naturaleza": "credito"
    },
    "costo_venta": {
        "codigos": [3010200],
        "naturaleza": "debito"
    },
    "gastos_comercializacion": {
        "codigos": [3010201,3010203],
        "naturaleza": "debito"
    },
    "comision_plataformas": {
        "codigos": [3020200],
        "naturaleza": "debito"
    },

    "gastos_marketing": {
        "codigos": [3010205],
        "naturaleza": "debito"
    },
    "gastos_arriendos": {
        "codigos": [3010211,3010212,3010213,3010214,3010215,3010216],
        "naturaleza": "debito"
    },
    "gastos_envios": {
        "codigos": [3010202],
        "naturaleza": "debito"
    },
    "gastos_administracion": {
        "codigos": [3010300],
        "naturaleza": "debito"
    },
    "gastos_financieros": {
        "codigos": [3020600],
        "naturaleza": "debito"
    },
    "depreciacion": {
        "codigos": [3010400],
        "naturaleza": "debito"
    },
    "utilidad_no_operacional": {
        "codigos": [3020300, 3020100],
        "naturaleza": "debito"
    },
    "ajuste_monetario": {
        "codigos": [3021100],
        "naturaleza": "debito"
    },
    "impuesto_renta": {
        "codigos": [3030100],
        "naturaleza": "debito"
    },
    "ajustes": {
        "codigos": [],
        "naturaleza": "debito"
    },
    # Agrega otros conceptos según necesites
}

def calcular_resultados_mensuales(año=None):

 # Procesos previos (puedes incluir solo los necesarios para el financiero)
    regenerar_ventas_consulta()
    poblar_movimientos_unificados_debito()
    poblar_movimientos_unificados_credito()
    regenerar_resumenes_credito_debito()

    if not año:
        from datetime import date
        año = date.today().year

    from collections import defaultdict
    resumen = defaultdict(lambda: defaultdict(float))

    for concepto, config in CONCEPTOS_CUENTAS.items():
        codigos = config["codigos"]
        naturaleza = config["naturaleza"]

        for codigo in codigos:
            # SUMA DÉBITOS
            debitos = MovimientoUnificadoDebito.objects.filter(
                cta_debito=codigo, fecha__year=año
            )
            total_debito_mes = defaultdict(float)
            for mov in debitos:
                total_debito_mes[mov.fecha.month] += float(mov.monto_debito)

            # SUMA CRÉDITOS
            creditos = MovimientoUnificadoCredito.objects.filter(
                cta_credito=codigo, fecha__year=año
            )
            total_credito_mes = defaultdict(float)
            for mov in creditos:
                total_credito_mes[mov.fecha.month] += float(mov.monto_credito)

            for mes in range(1, 13):
                if naturaleza == "credito":
                    resumen[mes][concepto] += total_credito_mes[mes]
                else:  # "debito" (gastos/costos)
                    resumen[mes][concepto] += total_debito_mes[mes] - total_credito_mes[mes]

    # Guarda los resultados en la base
    for mes in range(1, 13):
        mes_date = date(año, mes, 1)
        for concepto in CONCEPTOS_CUENTAS.keys():
            valor = int(round(resumen[mes][concepto]))
            ResultadoMensualDetalle.objects.update_or_create(
                mes=mes_date,
                concepto=concepto,
                defaults={"valor": valor}
            )

# boran_app/eerr.py

from datetime import date
from django.db.models import Sum
from .codigos_eerr import EERR, SUBTOTALES_EERR
from .models import MovimientoUnificadoDebito, MovimientoUnificadoCredito


def generar_estado_resultados(fecha_corte=None):
    """
    Genera el Estado de Resultados hasta la fecha indicada (valor_fecha)
    y para el año 2024 completo (valor_2024), devolviendo una lista de filas:
    [{ 'nombre': ..., 'valor_2024': ..., 'valor_fecha': ..., 'tipo': 'item'|'total' }]
    """
    # 1) Preparar querysets con y sin fecha de corte
    debit_qs_fecha = MovimientoUnificadoDebito.objects.all()
    credit_qs_fecha = MovimientoUnificadoCredito.objects.all()
    if fecha_corte:
        debit_qs_fecha = debit_qs_fecha.filter(fecha__lte=fecha_corte)
        credit_qs_fecha = credit_qs_fecha.filter(fecha__lte=fecha_corte)

    # Para todo 2024
    debit_qs_2024 = MovimientoUnificadoDebito.objects.filter(fecha__year=2024)
    credit_qs_2024 = MovimientoUnificadoCredito.objects.filter(fecha__year=2024)

    # 2) Agregar montos por cuenta, convirtiendo a float
    agg_d_fecha = {
        r['cta_debito']: float(r['total_debito'] or 0)
        for r in debit_qs_fecha.values('cta_debito')
                           .annotate(total_debito=Sum('monto_debito'))
    }
    agg_c_fecha = {
        r['cta_credito']: float(r['total_credito'] or 0)
        for r in credit_qs_fecha.values('cta_credito')
                            .annotate(total_credito=Sum('monto_credito'))
    }
    agg_d_2024 = {
        r['cta_debito']: float(r['total_debito'] or 0)
        for r in debit_qs_2024.values('cta_debito')
                          .annotate(total_debito=Sum('monto_debito'))
    }
    agg_c_2024 = {
        r['cta_credito']: float(r['total_credito'] or 0)
        for r in credit_qs_2024.values('cta_credito')
                           .annotate(total_credito=Sum('monto_credito'))
    }

    # 3) Calcular cada línea del EERR
    rows = []
    vals_fecha = {}
    vals_2024 = {}

    for nombre, items in EERR.items():
        total_fecha = 0.0
        total_2024 = 0.0
        for cta, signo in items:
            # Saldo hasta fecha de corte
            d_fecha = agg_d_fecha.get(cta, 0.0)
            k_fecha = agg_c_fecha.get(cta, 0.0)
            saldo_fecha = (d_fecha - k_fecha) * signo
            total_fecha += saldo_fecha
            # Saldo para todo 2024
            d_2024 = agg_d_2024.get(cta, 0.0)
            k_2024 = agg_c_2024.get(cta, 0.0)
            saldo_2024 = (d_2024 - k_2024) * signo
            total_2024 += saldo_2024
        # Agregar fila detalle
        rows.append({
            'nombre': nombre,
            'valor_2024': total_2024,
            'valor_fecha': total_fecha,
            'tipo': 'item'
        })
        vals_fecha[nombre] = total_fecha
        vals_2024[nombre] = total_2024

    # 4) Insertar subtotales según SUBTOTALES_EERR
    for grupos, etiqueta in SUBTOTALES_EERR:
        sum_fecha = sum(vals_fecha.get(g, 0.0) for g in grupos)
        sum_2024 = sum(vals_2024.get(g, 0.0) for g in grupos)
        rows.append({
            'nombre': etiqueta,
            'valor_2024': sum_2024,
            'valor_fecha': sum_fecha,
            'tipo': 'total'
        })

    return rows

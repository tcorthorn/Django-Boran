# boran_app/indicadores.py

from .ficha import generar_ficha_financiera
from .eerr import generar_estado_resultados

def _get_eerr_val(rows, nombre):
    """
    Busca en la lista de filas EERR la fila cuyo 'nombre' coincida
    y devuelve (valor_2024, valor_fecha). Si no encuentra, retorna (0.0, 0.0).
    """
    for r in rows:
        if r.get('nombre') == nombre:
            return r.get('valor_2024', 0.0), r.get('valor_fecha', 0.0)
    return 0.0, 0.0

def generar_indicadores(fecha_corte=None):
    # 1) Traer balance y EERR
    ficha = generar_ficha_financiera(fecha_corte)
    eerr_rows = generar_estado_resultados(fecha_corte)

    # 2) Extraer los valores clave del EERR
    ventas_2024, ventas_fecha = _get_eerr_val(eerr_rows, 'Ventas netas')
    cogs_2024,  cogs_fecha  = _get_eerr_val(eerr_rows, 'Costo de Ventas y GAVs')
    rob_2024,   rob_fecha   = _get_eerr_val(eerr_rows, 'Resultado Operacional Bruto (ROB)')
    gf_2024,    gf_fecha    = _get_eerr_val(eerr_rows, 'Gastos Financieros')
    unet_2024,  unet_fecha  = _get_eerr_val(eerr_rows, 'Utilidad (pérd.) Neta')
    ron_2024,   ron_fecha   = _get_eerr_val(eerr_rows, 'Resultado Operacional Neto')

    # 3) Extraer saldos del Balance
    act_corr_2024 = sum(ficha.get('ACTIVOS_CIRCULANTES', {}).values())
    act_corr_fecha = act_corr_2024
    pas_corr_2024 = sum(ficha.get('PASIVOS_CORRIENTES', {}).values())
    pas_corr_fecha = pas_corr_2024

    exist_2024 = ficha.get('ACTIVOS_CIRCULANTES', {}).get('Existencias', 0.0)
    exist_fecha = exist_2024
    cxc_2024 = ficha.get('ACTIVOS_CIRCULANTES', {}).get('Cuentas por Cobrar Giro', 0.0)
    cxc_fecha = cxc_2024
    cxp_2024 = (
        ficha.get('PASIVOS_CORRIENTES', {}).get('Ctas por Pagar', 0.0)
        + ficha.get('PASIVOS_CORRIENTES', {}).get('Ctas x Pagar Relacionados', 0.0)
    )
    cxp_fecha = cxp_2024

    deuda_cp_2024 = ficha.get('PASIVOS_CORRIENTES', {}).get('Obligaciones Bancarias C.P.', 0.0)
    deuda_lp_2024 = ficha.get('PASIVOS_LP', {}).get('Oblig. Bancarias L.P.', 0.0)
    deuda_fin_2024 = deuda_cp_2024 + deuda_lp_2024
    deuda_fin_fecha = deuda_fin_2024

    pas_lp_2024 = sum(ficha.get('PASIVOS_LP', {}).values())
    pn_2024 = sum(ficha.get('PATRIMONIO_NETO', {}).values())
    pas_exig_2024 = pas_corr_2024 + pas_lp_2024
    pas_exig_fecha = pas_exig_2024

    # 4) Calcular cada indicador
    indicadores = []

    # EBITDA
    indicadores.append({
        'nombre': 'EBITDA',
        'valor_2024': rob_2024,
        'valor_fecha': rob_fecha
    })

    # Margen Bruto / Ventas (%)
    mb_2024 = ventas_2024 and (ventas_2024 - cogs_2024) / ventas_2024 * 100 or 0.0
    mb_fecha = ventas_fecha and (ventas_fecha - cogs_fecha) / ventas_fecha * 100 or 0.0
    indicadores.append({
        'nombre': 'Margen Bruto / Ventas (%)',
        'valor_2024': mb_2024,
        'valor_fecha': mb_fecha
    })

    # Resultado Oper. Bruto / Ventas (%)
    robv_2024 = ventas_2024 and rob_2024 / ventas_2024 * 100 or 0.0
    robv_fecha = ventas_fecha and rob_fecha / ventas_fecha * 100 or 0.0
    indicadores.append({
        'nombre': 'Resultado Operacional Bruto / Ventas (%)',
        'valor_2024': robv_2024,
        'valor_fecha': robv_fecha
    })

    # Current Ratio
    cr_2024 = pas_corr_2024 and act_corr_2024 / pas_corr_2024 or 0.0
    cr_fecha = pas_corr_fecha and act_corr_fecha / pas_corr_fecha or 0.0
    indicadores.append({
        'nombre': 'Act. Circ. / Pas. Circ.',
        'valor_2024': cr_2024,
        'valor_fecha': cr_fecha
    })

    # Utilidad / Ventas (%)
    uv_2024 = ventas_2024 and unet_2024 / ventas_2024 * 100 or 0.0
    uv_fecha = ventas_fecha and unet_fecha / ventas_fecha * 100 or 0.0
    indicadores.append({
        'nombre': 'Utilidad / Ventas (%)',
        'valor_2024': uv_2024,
        'valor_fecha': uv_fecha
    })

    # Días de Inventario
    di_2024 = cogs_2024 and exist_2024 / cogs_2024 * 360 or 0.0
    di_fecha = cogs_fecha and exist_fecha / cogs_fecha * 360 or 0.0
    indicadores.append({
        'nombre': 'Permanencia Existencias (ds)',
        'valor_2024': di_2024,
        'valor_fecha': di_fecha
    })

    # Días CxC
    dcxc_2024 = ventas_2024 and cxc_2024 / ventas_2024 * 360 or 0.0
    dcxc_fecha = ventas_fecha and cxc_fecha / ventas_fecha * 360 or 0.0
    indicadores.append({
        'nombre': 'Permanencia Ctas. X Cobrar (ds)',
        'valor_2024': dcxc_2024,
        'valor_fecha': dcxc_fecha
    })

    # Días CxP
    dcp_2024 = cogs_2024 and cxp_2024 / cogs_2024 * 360 or 0.0
    dcp_fecha = cogs_fecha and cxp_fecha / cogs_fecha * 360 or 0.0
    indicadores.append({
        'nombre': 'Permanencia Ctas. X Pagar (ds)',
        'valor_2024': dcp_2024,
        'valor_fecha': dcp_fecha
    })

    # EBITDA / Gastos Financieros
    egf_2024 = gf_2024 and rob_2024 / gf_2024 or 0.0
    egf_fecha = gf_fecha and rob_fecha / gf_fecha or 0.0
    indicadores.append({
        'nombre': 'EBITDA / Gastos Financieros',
        'valor_2024': egf_2024,
        'valor_fecha': egf_fecha
    })

    # Deudas Financieras / EBITDA
    dfe_2024 = rob_2024 and deuda_fin_2024 / rob_2024 or 0.0
    dfe_fecha = rob_fecha and deuda_fin_fecha / rob_fecha or 0.0
    indicadores.append({
        'nombre': 'Deudas financieras / EBITDA',
        'valor_2024': dfe_2024,
        'valor_fecha': dfe_fecha
    })

    # Pasivo Exigible / Patrimonio Neto
    pen_2024 = pn_2024 and pas_exig_2024 / pn_2024 or 0.0
    pen_fecha = pn_2024 and pas_exig_fecha / pn_2024 or 0.0
    indicadores.append({
        'nombre': 'Pasivo Exigible / Patrimonio Neto',
        'valor_2024': pen_2024,
        'valor_fecha': pen_fecha
    })

    # Pasivo Exigible / Patr. Neto + Int. Min.
    # (si tuvieras interés minoritario, súmalo a pn_2024; aquí lo omitimos)
    indicadores.append({
        'nombre': 'Pasivo Exigible / Patr. Neto+ Int. Min.',
        'valor_2024': pen_2024,
        'valor_fecha': pen_fecha
    })

    return indicadores

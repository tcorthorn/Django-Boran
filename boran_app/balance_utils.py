def obtener_matriz_dict_balance():
    from .models import ResumenDebito, ResumenCredito
    from .cod_cuentas_balance import balance_rows

    debitos_dict = {d.cuenta_debito: float(d.total_debito) for d in ResumenDebito.objects.all()}
    creditos_dict = {c.cuenta_credito: float(c.total_credito) for c in ResumenCredito.objects.all()}
    matriz_dict = {}
    for fila in balance_rows:
        codigo = str(fila['codigo'])
        debito = debitos_dict.get(int(codigo), 0)
        credito = creditos_dict.get(int(codigo), 0)
        saldo_deudor = debito - credito if debito > credito else 0
        saldo_acreedor = credito - debito if credito > debito else 0
        if 1010100 <= int(codigo) <= 2040000:
            matriz_dict[f'A:{codigo}'] = saldo_deudor
            matriz_dict[f'P:{codigo}'] = saldo_acreedor
        elif 3010100 <= int(codigo) <= 3010300:
            matriz_dict[f'Pe:{codigo}'] = saldo_deudor
            matriz_dict[f'G:{codigo}'] = saldo_acreedor
    return matriz_dict

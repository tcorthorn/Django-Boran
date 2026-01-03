import re

def eval_formula(formula, matriz, linea_lookup=None, resultado_lookup=None, activo_lookup=None):
    if not formula or not formula.strip():
        return 0

    if linea_lookup is None:
        linea_lookup = {}
    if resultado_lookup is None:
        resultado_lookup = {}
    if activo_lookup is None:
        activo_lookup = {}

    # Si la fórmula es solo un número (línea), busca primero en resultado_lookup, luego en activo_lookup, luego en linea_lookup
    if re.fullmatch(r"\d+", formula.strip()):
        num = formula.strip()
        for lookup in (resultado_lookup, activo_lookup, linea_lookup):
            if num in lookup:
                return lookup[num]
        return 0

    expr = formula

    # Reemplaza A:xxxxxx, P:xxxxxx, Pe:xxxxxx, G:xxxxxx por sus valores en matriz
    def reemplazar_codigo(match):
        key = match.group(0)
        return str(matriz.get(key, 0))
    expr = re.sub(r'(A:\d{5,7}|P:\d{5,7}|Pe:\d{5,7}|G:\d{5,7})', reemplazar_codigo, expr)

    # Reemplaza referencias a líneas numéricas por sus valores en los lookups
    def reemplazar_linea(match):
        num = match.group(0)
        for lookup in (resultado_lookup, activo_lookup, linea_lookup):
            if num in lookup:
                return str(lookup[num])
        return num  # deja el número si no encuentra

    expr = re.sub(r'\b\d{2,4}\b', reemplazar_linea, expr)

    # Por seguridad, solo permitir números, (), +, -, *, /
    if re.search(r"[^0-9\+\-\*\/\(\)\.\s]", expr):
        return 0

    try:
        return eval(expr, {"__builtins__": {}})
    except Exception:
        return 0

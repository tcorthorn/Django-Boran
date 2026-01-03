# consult_app/validar_plan_cuentas.py
import re
from django.apps import apps
from django.contrib import messages
from boran_app.cod_cuentas_balance import balance_rows
from boran_app.utils import poblar_movimientos_unificados_credito, poblar_movimientos_unificados_debito
from boran_app.utils import regenerar_resumenes_credito_debito

def _get_model(app_first, model_name, app_second=None):

    # Procesos previos
    poblar_movimientos_unificados_debito()
    poblar_movimientos_unificados_credito()
    regenerar_resumenes_credito_debito()

    """
    Devuelve el primer modelo que exista entre app_first y app_second.
    """
    try:
        m = apps.get_model(app_first, model_name)
        if m is not None:
            return m
    except LookupError:
        pass
    if app_second:
        try:
            m = apps.get_model(app_second, model_name)
            if m is not None:
                return m
        except LookupError:
            pass
    return None

def _to_int_code(value):
    """
    Normaliza el código a int:
      - Acepta int, Decimal, str con espacios y separadores (.,) o basura extra.
      - Devuelve (ok: bool, iv: int | None, raw: any) para clasificar.
    """
    if value is None:
        return (False, None, value)
    # Rápido para enteros
    if isinstance(value, int):
        return (True, value, value) if value != 0 else (False, 0, value)
    # Para todo lo demás, limpiamos dejando solo dígitos y el signo (si acaso)
    s = str(value).strip()
    # quita todo lo que no sea dígito o signo
    s = re.sub(r"[^\d\-+]", "", s)
    if s in ("", "+", "-", "0"):
        # vacío, solo signo o cero => lo tratamos como nulo/0
        return (False, 0 if s == "0" else None, value)
    try:
        iv = int(s)
        return (True, iv, value) if iv != 0 else (False, 0, value)
    except Exception:
        return (False, None, value)

def validar_plan_cuentas(request):
    """
    Valida códigos contables presentes en:
      - ResumenCredito / ResumenDebito
      - MovimientoUnificadoCredito / MovimientoUnificadoDebito
    contra el plan (balance_rows).

    Emite mensajes con:
      - Cuentas fuera del plan
      - Cuentas nulas/0
      - Códigos no casteables
      - Un pequeño resumen de conteos
    """
    # 1) Set de códigos válidos del plan (como enteros)
    try:
        codigos_validos = {int(r["codigo"]) for r in balance_rows}
    except Exception as e:
        messages.error(request, f"No pude leer balance_rows: {e}")
        return

    # 2) Localiza modelos (ajusta el orden si tus modelos están en consult_app)
    RC = _get_model("boran_app", "ResumenCredito",  "consult_app")
    RD = _get_model("boran_app", "ResumenDebito",   "consult_app")
    MC = _get_model("boran_app", "MovimientoUnificadoCredito", "consult_app")
    MD = _get_model("boran_app", "MovimientoUnificadoDebito",  "consult_app")

    if not any([RC, RD, MC, MD]):
        messages.error(request, "No encontré modelos de resumen ni de movimientos para validar.")
        return

    # 3) Lee códigos presentes (distinct) en resúmenes y movimientos
    cods_resumen = set()
    if RC:
        cods_resumen |= set(RC.objects.values_list("cuenta_credito", flat=True).distinct())
    if RD:
        cods_resumen |= set(RD.objects.values_list("cuenta_debito",  flat=True).distinct())

    cods_movs = set()
    if MC:
        cods_movs |= set(MC.objects.values_list("cta_credito", flat=True).distinct())
    if MD:
        cods_movs |= set(MD.objects.values_list("cta_debito",  flat=True).distinct())

    cods_raw = list(cods_resumen | cods_movs)

    # 4) Clasifica
    desconocidos = set()
    nulos_o_cero = []
    no_casteables = []

    for v in cods_raw:
        ok, iv, raw = _to_int_code(v)
        if not ok:
            # None o 0 o no casteable
            if iv == 0:
                nulos_o_cero.append(raw)
            elif iv is None:
                # Si es None o basura imposible de castear
                no_casteables.append(raw)
            continue
        if iv not in codigos_validos:
            desconocidos.add(iv)

    # 5) Mensajes
    if desconocidos:
        sample = ", ".join(map(str, sorted(list(desconocidos))[:30]))
        messages.error(
            request,
            f"Cuentas FUERA del plan ({len(desconocidos)}): {sample}"
            + (" …" if len(desconocidos) > 30 else "")
        )
    if nulos_o_cero:
        sample = ", ".join("None" if x is None else str(x) for x in nulos_o_cero[:30])
        messages.error(
            request,
            f"Cuentas NULAS/0 detectadas ({len(nulos_o_cero)}): {sample}"
            + (" …" if len(nulos_o_cero) > 30 else "")
        )
    if no_casteables:
        sample = ", ".join(map(str, no_casteables[:30]))
        messages.error(
            request,
            f"Códigos NO CASTEABLES ({len(no_casteables)}): {sample}"
            + (" …" if len(no_casteables) > 30 else "")
        )

    # Resumen final
    total_usados = len(cods_raw)
    total_plan  = len(codigos_validos)
    if not desconocidos and not nulos_o_cero and not no_casteables:
        messages.success(
            request,
            f"Validación OK. Usados={total_usados}, Plan={total_plan}. Todas las cuentas están en el plan."
        )
    else:
        messages.info(
            request,
            f"Resumen validación: Usados={total_usados}, Plan={total_plan}, "
            f"FueraPlan={len(desconocidos)}, Nulos/0={len(nulos_o_cero)}, NoCasteables={len(no_casteables)}."
        )

        # ------------------------------------------------------------------
    # 6) DETALLE DE ORIGEN para cada cuenta FUERA DEL PLAN
    #    (pegar a continuación de tus mensajes existentes)
    # ------------------------------------------------------------------
    if desconocidos:
        # Reusar o resolver modelos de movimientos (sin romper si ya existen)
        try:
            MC = MC  # si ya existe arriba
        except NameError:
            MC = _get_model("boran_app", "MovimientoUnificadoCredito", "consult_app")
        try:
            MD = MD
        except NameError:
            MD = _get_model("boran_app", "MovimientoUnificadoDebito",  "consult_app")

        def _field_exists(model, name: str) -> bool:
            if not model:
                return False
            try:
                return name in {f.name for f in model._meta.get_fields()}
            except Exception:
                return False

        def _pick_amount_field(model, preferred: list[str]) -> str | None:
            """Devuelve el primer nombre de campo de monto que exista en el modelo."""
            for nm in preferred:
                if _field_exists(model, nm):
                    return nm
            return None

        # Detecta campos disponibles en cada modelo
        credit_amount_field = _pick_amount_field(MC, ["monto_credito", "monto", "monto_total", "importe"])
        debit_amount_field  = _pick_amount_field(MD, ["monto_debito",  "monto", "monto_total", "importe"])

        # Campos comunes deseados
        common_fields = ["fecha", "texto_coment", "tabla_origen"]

        max_rows_per_code = 10  # evita inundar messages

        for code in sorted(desconocidos):
            # --- CRÉDITO ---
            if MC:
                # arma lista de fields existentes en el modelo
                fields_c = [f for f in common_fields if _field_exists(MC, f)]
                if credit_amount_field:
                    fields_c = [credit_amount_field] + fields_c
                qs_c = (
                    MC.objects.filter(cta_credito=code)
                    .order_by("-fecha")
                )
                total_c = qs_c.count()
                if total_c:
                    # Si no hay fields detectados, solo muestra conteo
                    if fields_c:
                        rows = list(qs_c.values(*fields_c)[:max_rows_per_code])
                        # Formatea líneas
                        lineas = []
                        for r in rows:
                            fecha = r.get("fecha")
                            monto = r.get(credit_amount_field, None)
                            texto = r.get("texto_coment", "")
                            origen = r.get("tabla_origen", "")
                            lineas.append(f"{fecha} | monto_credito={monto} | {texto} | {origen}")
                        suffix = " …" if total_c > max_rows_per_code else ""
                        messages.error(
                            request,
                            f"[{code}] en CRÉDITO ({total_c} ocurrencias): " + " ; ".join(lineas) + suffix
                        )
                    else:
                        messages.error(
                            request,
                            f"[{code}] en CRÉDITO: {total_c} ocurrencias (no pude leer campos detalle)."
                        )

            # --- DÉBITO ---
            if MD:
                fields_d = [f for f in common_fields if _field_exists(MD, f)]
                if debit_amount_field:
                    fields_d = [debit_amount_field] + fields_d
                qs_d = (
                    MD.objects.filter(cta_debito=code)
                    .order_by("-fecha")
                )
                total_d = qs_d.count()
                if total_d:
                    if fields_d:
                        rows = list(qs_d.values(*fields_d)[:max_rows_per_code])
                        lineas = []
                        for r in rows:
                            fecha = r.get("fecha")
                            monto = r.get(debit_amount_field, None)
                            texto = r.get("texto_coment", "")
                            origen = r.get("tabla_origen", "")
                            lineas.append(f"{fecha} | monto_debito={monto} | {texto} | {origen}")
                        suffix = " …" if total_d > max_rows_per_code else ""
                        messages.error(
                            request,
                            f"[{code}] en DÉBITO ({total_d} ocurrencias): " + " ; ".join(lineas) + suffix
                        )
                    else:
                        messages.error(
                            request,
                            f"[{code}] en DÉBITO: {total_d} ocurrencias (no pude leer campos detalle)."
                        )


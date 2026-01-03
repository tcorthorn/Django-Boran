# boran_app/context_processors.py
"""
Context processor para manejar el año fiscal seleccionado.
El año fiscal se guarda en la sesión del usuario.
"""
from datetime import date

def anno_fiscal(request):
    """
    Agrega el año fiscal seleccionado al contexto de todas las plantillas.
    Por defecto usa el año actual.
    """
    # Obtener año fiscal de la sesión, por defecto el año actual
    anno_actual = date.today().year
    anno_fiscal_seleccionado = request.session.get('anno_fiscal', anno_actual)
    
    # Años disponibles para selección
    annos_disponibles = [2025, 2026]
    
    # Calcular fechas de inicio y fin del año fiscal
    fecha_inicio_fiscal = date(anno_fiscal_seleccionado, 1, 1)
    fecha_fin_fiscal = date(anno_fiscal_seleccionado, 12, 31)
    
    return {
        'anno_fiscal': anno_fiscal_seleccionado,
        'annos_disponibles': annos_disponibles,
        'fecha_inicio_fiscal': fecha_inicio_fiscal,
        'fecha_fin_fiscal': fecha_fin_fiscal,
    }

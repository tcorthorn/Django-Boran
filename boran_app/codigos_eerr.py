# boran_app/codigos_eerr.py

# Cada línea del EERR: nombre → lista de (cuenta, factor)
EERR = {
    'Ventas netas': [
        (3010101, +1),  # Ingresos por Ventas
        (3010111, +1),  # Otros ingresos netos
    ],
       'Costo de Ventas y GAVs': [
        (3020100, -1),  # Costo de Producción
        (3010120, -1),  # Devoluciones
        (3010130, -1),
        (3010200, -1),
        (3010201, -1),
        (3010202, -1),
        (3010203, -1),
        (3010205, -1),
        (3010211, -1),
        (3010212, -1),
        (3010213, -1),
        (3010214, -1),
        (3010215, -1),
        (3010300, -1),

    ],
    'Gastos Financieros': [
        (3030216, -1),
    ],
    'Depreciación Ejercicio': [
        (3010400, -1),
    ],
    'Utilidad (pérd.) No Operacional': [
        (3020100, +1),
        (3020200, +1),
        (3020300, +1),
        (3020400, -1),
        (3020500, -1),
        (3020600, -1),
        (3020700, -1),
        (3020800, -1),
        (3020900, -1),
        (3021000, -1),
        
    ],
   'Ajuste Monetario': [
        (3021100, -1),
    ], 
    'Impuesto a la Renta': [
        (3030100, -1),
    ],
    'Ajustes(-)': [
        (3030200, -1),
    ],

    # … sigue con cada línea …
}

# Subtotales que quieres calcular:
# cada tuple: (lista de líneas, etiqueta del subtotal)
SUBTOTALES_EERR = [
    (['Ventas netas'], 'Ventas Netas'),
    (['Costo de Ventas y GAVs'], 'Costo de Ventas y GAVs'),
    (
    ['Ventas netas',  'Costo de Ventas y GAVs'],
      'Resultado Operacional Bruto (ROB)'
    ),
    (
      ['Resultado Operacional Bruto (ROB)', 'Gastos Financieros', 'Depreciación Ejercicio'],
      'Resultado Operacional Neto'
    ),
    (
      ['Resultado Operacional Neto', 'Utilidad (pérd.) No Operacional', 'Ajuste Monetario', 'Impuesto a la Renta','Ajustes(-)'],
      'Utilidad Neta'
    ),
    
    
    # y así hasta Utilidad Neta…
]

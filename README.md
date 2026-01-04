# Django-BORAN - Panel Contable

## Descripcion
Panel contable Django para gestion financiera con selector de ano fiscal (2025/2026).

## Cambios Implementados (Enero 2026)

### 1. Selector de Ano Fiscal
- **Ubicacion**: Header del Panel Home
- **Opciones**: 2025 y 2026
- **Funcionamiento**: 
  - Al seleccionar un ano, todos los calculos de balance toman datos solo de ese ano
  - El ano se guarda en la sesion del usuario
  - Las fechas de inicio/fin se calculan automaticamente (1-ene hasta hoy o 31-dic)

### 2. Vistas Corregidas para Filtrar por Ano Fiscal
- `balance_segun_fecha_view`: Ahora filtra movimientos desde inicio del ano fiscal hasta la fecha de corte
- `resumen_balance_segun_fecha_view`: Regenera tablas financieras con el rango del ano fiscal
- `resumen_financiero_segun_fecha_view`: Filtrado correcto por ano fiscal seleccionado

### 3. Vistas Nuevas Agregadas
| Vista | URL | Descripcion |
|-------|-----|-------------|
| `productos_rentables` | `/productos-rentables/` | Muestra los 20 productos mas rentables del ano fiscal |
| `inventario_tiendas` | `/inventario-tiendas/` | Inventario por tienda y SKU |
| `validar_plan_cuentas` | `/validar-plan-cuentas/` | Valida cuentas contables vs plan de cuentas |
| `movimientos_cuenta` | `/movimientos-cuenta/` | Ver movimientos de una cuenta especifica |
| `movimientos_por_fecha` | `/movimientos-por-fecha/` | Movimientos de una fecha especifica |
| `movimientos_por_rango` | `/movimientos-por-rango/` | Movimientos en un rango de fechas |

### 4. Templates Nuevos
- `productos_rentables.html`
- `inventario_tiendas.html`
- `validar_plan_cuentas.html`
- `movimientos_cuenta.html`
- `movimientos_por_fecha.html`
- `movimientos_por_rango.html`

### 5. Correcciones de Bugs
- Eliminadas funciones `home()` duplicadas (habia 3 definiciones)
- Agregado footer al template base
- Corregidos imports duplicados

## URLs Principales

### Panel Principal
- `/` - Home con selector de ano fiscal

### Balance
- `/balance/` - Balance general
- `/balance-segun-fecha/` - Balance por fecha de corte
- `/resumen_balance/` - Resumen de balance
- `/resumen_balance_segun_fecha/` - Resumen por fecha

### Resumen Financiero
- `/resumenfinanciero/` - Resumen financiero completo
- `/resumenfinancierosegunfecha/` - Por fecha de corte

### Reportes
- `/resumen_mensual/` - Resumen mensual
- `/resultados-mensuales/` - Resultados detallados por mes
- `/resumen-ventas-tiendas/` - Resumen por tienda

### Contabilidad
- `/importar/` - Importar datos
- `/validar-plan-cuentas/` - Validar cuentas
- `/movimientos-cuenta/` - Buscar por cuenta
- `/movimientos-por-fecha/` - Buscar por fecha
- `/movimientos-por-rango/` - Buscar por rango

## Como Funciona el Selector de Ano

1. El usuario hace clic en el boton "2025" o "2026" en el header
2. Se envia un POST a `/set-panel-year/`
3. El ano se guarda en `request.session['panel_year']`
4. Se recalculan las fechas: 
   - `fecha_inicio`: 1 de enero del ano seleccionado
   - `fecha_fin`: Hoy si es el ano actual, o 31 de diciembre si es otro ano
5. Todas las vistas de balance/resumen filtran por este rango

## Estructura de Archivos Modificados

```
boran_app/
├── views.py          # Vistas principales (corregido home duplicado)
├── urls.py           # URLs (agregadas nuevas rutas)
├── templates/
│   └── boran_app/
│       ├── base.html                    # Template base (agregado footer)
│       ├── home.html                    # Panel principal
│       ├── productos_rentables.html     # NUEVO
│       ├── inventario_tiendas.html      # NUEVO
│       ├── validar_plan_cuentas.html    # NUEVO
│       ├── movimientos_cuenta.html      # NUEVO
│       ├── movimientos_por_fecha.html   # NUEVO
│       └── movimientos_por_rango.html   # NUEVO
```

## Requisitos
- Python 3.x
- Django 5.2.1
- SQLite3

## Ejecucion
```bash
cd /home/user/webapp
python manage.py runserver 0.0.0.0:8000
```

## Repositorio
- GitHub: https://github.com/tcorthorn/Django-Boran

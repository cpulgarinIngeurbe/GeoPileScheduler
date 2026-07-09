# FASE 4 - Motor de Recursos

## Objetivo

Modelar comportamiento dinámico de equipos de pilotaje.

## Arquitectura

```
src/resources/
├── __init__.py                  (Exporta MotorRecursos)
├── event_model.py               (Eventos de equipos)
├── equipo_state.py              (Estado dinámico)
├── equipo_manager.py            (Gestor de equipos)
├── performance_calculator.py    (Cálculos de rendimiento)
├── engine.py                    (MotorRecursos)
└── README_PHASE4.md             (Esta documentación)
```

## Ciclo de vida de trabajo en equipo

```
DISPONIBLE (equipo libre)
    ↓ (se asigna pilote)
EN_TRABAJO (equipo ejecutando)
    ↓ (finaliza ejecución)
DISPONIBLE (vuelve a estar libre)

Transversal: CAMBIO_UNIDAD (puede ocurrir en cualquier momento)
```

## Rendimiento Diario (R2)

**Restricción**:
```
Cada equipo e ejecuta exactamente r_e pilotes por jornada (8 horas)

Tiempo por pilote = 8 horas / r_e

Ejemplo: r_e = 2 pilotes/día
→ tiempo por pilote = 4 horas
```

## Módulos

### Eventos (event_model.py)
- `EventoInicioTrabajo`: equipo comienza pilote
- `EventoFinTrabajo`: equipo termina pilote
- `EventoCambioUnidad`: equipo se desplaza
- `EventoResetDiario`: reinicio de contadores

### Estado de equipo (equipo_state.py)
- `EstadoEquipo`: posición, pilote actual, contadores diarios
- Propiedades: `esta_libre`, `esta_ocupado`, `porcentaje_rendimiento`
- Métodos: `utilization_rate()`, `reset_diario()`

### Gestor de equipos (equipo_manager.py)
- `inicializar()`: setup de todos los equipos
- `asignar_pilote()`: asigna trabajo
- `finalizar_pilote()`: termina trabajo
- `cambiar_unidad()`: desplazamiento
- `get_equipos_disponibles()`: equipos libres
- `get_estadisticas_equipos()`: métricas globales

### Calculador de rendimiento (performance_calculator.py)
- `calcular_tiempo_ejecucion()`: 8h / rendimiento
- `calcular_tiempo_cambio_unidad()`: distancia / 5 km/h
- `distancia_entre_unidades_aproximada()`: usando centroides
- `utilization_rate()`: porcentaje de uso

### MotorRecursos (engine.py)
- Interfaz integrada
- `inicializar()`: setup
- `asignar_trabajo()`: asigna pilote a equipo
- `finalizar_trabajo()`: termina ejecución
- `cambiar_equipo_de_unidad()`: desplazamiento
- `get_equipos_disponibles()`: libres
- `get_estado_equipo()`: estado actual
- `get_estadisticas_equipos()`: métricas

## Uso

```python
from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.resources import MotorRecursos
from datetime import datetime

# Cargar
proyecto = load_project("proyecto.xlsx")
motor_geo = MotorGeometrico(proyecto)
motor_geo.calcular()

# Recursos
motor_rec = MotorRecursos(proyecto, motor_geo)
motor_rec.inicializar()

# Asignar trabajo
motor_rec.asignar_trabajo("EQ_A", "P_001", datetime.now())

# Finalizar
motor_rec.finalizar_trabajo("EQ_A", datetime.now() + timedelta(hours=4))

# Consultar
disponibles = motor_rec.get_equipos_disponibles()
stats = motor_rec.get_estadisticas_equipos()
```

## Validación

```bash
python test_phase4_complete.py
```

Valida:
- Inicialización de equipos
- Asignación de trabajo
- Finalización de trabajo
- Gestión de estados
- Cálculo de estadísticas
- Rendimiento controlado (R2)

## Métricas

- **Utilización**: (tiempo_trabajo / 8h) × 100%
- **Productividad**: pilotes_ejecutados
- **Eficiencia**: distancia_productiva / distancia_total
- **Carga**: tiempo_espera

## Complejidad

- Inicializar: O(E) donde E = equipos
- Asignar/Finalizar: O(1)
- Cambiar unidad: O(U) donde U = unidades
- Estadísticas: O(E)

Performance: aceptable para cualquier escala de equipos.

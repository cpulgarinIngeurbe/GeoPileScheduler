# FASE 5 - Motor de Simulación

## Objetivo

Integrar los tres motores (Geométrico, Restricciones, Recursos) en un simulador event-driven que represente la ejecución real de un proyecto de pilotaje.

## Arquitectura

```
src/simulation/
├── __init__.py                  (Exporta MotorSimulacion)
├── event_model.py               (Tipos de eventos)
├── event_queue.py               (Cola de eventos)
├── engine.py                    (MotorSimulacion)
├── validator.py                 (Validador)
├── statistics.py                (Estadísticas)
├── visualizations.py            (Gráficos)
└── README_PHASE5.md             (Esta documentación)
```

## Flujo de Simulación

```
┌─────────────────────────────────────────────────────────┐
│ MotorSimulacion.inicializar()                           │
│  • Crear EventQueue vacía                              │
│  • Agregar evento INICIO_SIMULACION                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Loop: while not queue.empty()                           │
│  • Pop próximo evento                                  │
│  • Actualizar tiempo_actual                            │
│  • Procesar según tipo:                                │
│    - INICIO_SIMULACION → agregar ASIGNACION_PILOTE    │
│    - ASIGNACION_PILOTE → agregar FIN_EJECUCION        │
│    - FIN_EJECUCION → ejecutar pilote + bloqueos       │
│  • Registrar en historial                              │
│  • Verificar si completada                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ (todos pilotes ejecutados)
┌─────────────────────────────────────────────────────────┐
│ MotorSimulacion.get_timeline()                          │
│  • Duración total                                       │
│  • Estadísticas de ejecución                            │
│  • Generar visualizaciones                              │
└─────────────────────────────────────────────────────────┘
```

## Tipos de Eventos

### TipoEvento

- `INICIO_SIMULACION`: Simulación comienza
- `FIN_SIMULACION`: Simulación finaliza
- `ASIGNACION_PILOTE`: Equipo asignado a pilote
- `INICIO_EJECUCION`: Equipo inicia trabajo
- `FIN_EJECUCION`: Equipo finaliza pilote
- `BLOQUEO_PILOTE`: Pilote bloqueado por R1
- `DESBLOQUEO_PILOTE`: Pilote liberado de bloqueo
- `CAMBIO_UNIDAD`: Equipo cambia de unidad
- `RESET_DIARIO`: Reinicio de contadores diarios
- `REPORTE_PROGRESO`: Reporte de avance
- `ERROR_RESTRICCION`: Error en restricción

### NivelEvento

- `INFO`: Evento informativo
- `WARNING`: Advertencia
- `ERROR`: Error
- `CRITICO`: Evento crítico

## Módulos

### EventoSimulacion (event_model.py)

```python
@dataclass
class EventoSimulacion:
    tipo: TipoEvento
    timestamp: datetime
    entidad_id: str
    datos: dict[str, Any] = {}
    nivel: NivelEvento = NivelEvento.INFO
```

### EventQueue (event_queue.py)

- `push(evento)`: agregar evento (O(log N))
- `pop()`: obtener y remover próximo (O(log N))
- `peek()`: ver próximo sin remover (O(1))
- `empty()`: verificar si vacía (O(1))
- `size()`: obtener tamaño (O(1))

Implementada con `heapq` para garantizar:
- Orden temporal: eventos por timestamp
- FIFO en eventos simultáneos: contador interno

### MotorSimulacion (engine.py)

**Interfaz**:
- `inicializar()`: setup de la simulación
- `ejecutar()`: loop event-driven completo
- `ejecutar_paso()`: procesar un evento
- `get_estado_global()`: estado actual
- `get_progreso()`: progreso del proyecto
- `get_eventos_historial()`: historial completo
- `get_timeline()`: estadísticas temporales

**Responsabilidades**:
- Administrar tiempo (timestamp actual)
- Administrar eventos (EventQueue)
- Actualizar estados de los motores
- Coordinar decisiones de asignación
- Registrar historial

### ReporteValidacionSimulacion (validator.py)

Valida:
- V1: Todos los pilotes ejecutados
- V2: Timeline consistente (orden temporal)
- V3: Restricción R1 respetada
- V4: Equipos sin sobreasignación
- V5: Eventos completos

### EstadisticasSimulacion (statistics.py)

Calcula:
- `tiempo_total_horas`: duración del proyecto
- `pilotes_ejecutados`: cantidad de pilotes
- `makespan`: tiempo crítico
- `utilization_promedio`: uso de equipos (%)
- `eficiencia_espacial`: desplazamientos óptimos (%)

## Uso

```python
from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos
from src.simulation import MotorSimulacion
from src.simulation.validator import validar_simulacion
from src.simulation.statistics import generar_estadisticas_completas

# Cargar
proyecto = load_project("proyecto.xlsx")

# Motores anteriores
motor_geo = MotorGeometrico(proyecto)
motor_geo.calcular()

motor_rest = MotorRestricciones(proyecto, motor_geo)
motor_rest.inicializar()

motor_rec = MotorRecursos(proyecto, motor_geo)
motor_rec.inicializar()

# Simulación
motor_sim = MotorSimulacion(proyecto, motor_geo, motor_rest, motor_rec)
motor_sim.inicializar()
motor_sim.ejecutar()

# Validar
reporte = validar_simulacion(proyecto, motor_sim)
reporte.imprimir()

# Estadísticas
stats = generar_estadisticas_completas(proyecto, motor_sim)
print(stats.resumen())

# Visualizaciones
from src.simulation.visualizations import generar_dashboard_simulacion
generar_dashboard_simulacion(proyecto, motor_sim)
```

## Validación

```bash
python test_phase5_complete.py
```

Valida:
- Carga de proyecto (T1-T2)
- Geometría calculada (FASE 2)
- Restricciones inicializadas (FASE 3)
- Recursos inicializados (FASE 4)
- Simulación ejecutada
- Validación de restricciones
- Generación de estadísticas
- Creación de visualizaciones

## Casos de Prueba

### CASO 4: Simulación Lineal
- 1 unidad, 1 equipo, 5 pilotes
- Radio grande (sin bloqueos)
- Ejecución secuencial

### CASO 5: Simulación Paralela
- 1 unidad, 3 equipos, 10 pilotes
- Radio medio (bloqueos moderados)
- Ejecución paralela con restricciones

## Complejidad

- Inicializar: O(1)
- Ejecutar paso: O(K) donde K = vecinos afectados
- Ejecutar completo: O(P × log P) donde P = pilotes
- Validar: O(P²) para verificar R1

Performance: Aceptable hasta 1000+ pilotes en simulación completa.

## Limitaciones y Supuestos

1. **Supuesto de duración**: Cada pilote tarda 8h / rendimiento_dia
2. **Desplazamiento**: Se asume 5 km/h entre unidades
3. **Sin interrupciones**: Los equipos no se interrumpen
4. **Determinístico**: La simulación es completamente determinística
5. **Monothread**: La simulación es secuencial (un evento por vez)

## Visualizaciones

- **Timeline**: Línea temporal de eventos
- **Gantt**: Diagrama de Gantt de equipos
- **Progreso**: Curva de ejecución acumulada
- **Utilización**: Pilotes por equipo
- **Histograma**: Distribución de eventos
- **Dashboard**: Panel integrado 2×2

Todas generadas en HTML interactivo (Plotly).

## Próxima Fase

**FASE 6 - Motor de Optimización**: Integrar algoritmos para:
- Asignación óptima de equipos
- Secuencia óptima de pilotes
- Minimización de makespan
- Balanceo de carga

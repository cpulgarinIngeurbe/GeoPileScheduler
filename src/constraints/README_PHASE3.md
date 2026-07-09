# FASE 3 - Motor de Restricciones

## Objetivo

Implementar control dinámico de restricciones geotécnicas (R1).

## Arquitectura

```
src/constraints/
├── __init__.py               (Exporta MotorRestricciones)
├── event_model.py            (BloqueoGeotecnico)
├── pilote_state_manager.py   (Gestor de estados)
├── restriction_r1.py         (Aplicador R1)
├── available_calculator.py   (Calculador de disponibles)
├── validator.py              (Validador)
├── engine.py                 (MotorRestricciones)
└── README_PHASE3.md          (Esta documentación)
```

## Restricción Geotécnica R1

**Fórmula**:
```
Si D(p_i, p_j) ≤ R entonces T_j - T_i ≥ H

Donde:
- D = distancia euclidiana (FASE 2)
- R = radio_critico_m
- H = tiempo_restriccion_h
- T = datetime de ejecución
```

## Ciclo de vida de un pilote

```
PENDIENTE
    ↓ (se libera bloqueo)
DISPONIBLE
    ↓ (se asigna a equipo)
ASIGNADO
    ↓ (equipo termina)
EJECUTADO
    ↓ (causa bloqueos)
[Vecinos: DISPONIBLE → BLOQUEADO]
    ↓ (tiempo expira)
[Vecinos: BLOQUEADO → DISPONIBLE]
```

## Módulos

### BloqueoGeotecnico (event_model.py)
- Representa bloqueo temporal
- `tiempo_fin`: cuándo se libera
- `esta_activo()`: ¿sigue vigente?

### PiloteStateManager (pilote_state_manager.py)
- Mantiene estado dinámico de cada pilote
- Valida transiciones de estado
- Gestiona lista de bloqueos por pilote
- `liberar_bloqueos_expirados()`: limpia automáticamente

### Aplicador R1 (restriction_r1.py)
- `aplicar_restriccion_r1()`: cuando pilote se ejecuta, bloquea vecinos
- `desbloquear_automaticamente()`: libera pilotes

### Calculador de disponibles (available_calculator.py)
- `get_pilotes_disponibles()`: lista de ejecutables
- Libera bloqueos expirados automáticamente

### MotorRestricciones (engine.py)
- Interfaz integrada
- `inicializar()`: setup
- `ejecutar_pilote()`: marca ejecutado + aplica R1
- `actualizar_tiempo()`: desbloquea expirados
- `get_pilotes_disponibles()`: lista de ejecutables
- `get_estadisticas_restricciones()`: métricas

## Uso

```python
from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from datetime import datetime

# Cargar
proyecto = load_project("proyecto.xlsx")
motor_geo = MotorGeometrico(proyecto)
motor_geo.calcular()

# Restricciones
motor_rest = MotorRestricciones(proyecto, motor_geo)
motor_rest.inicializar()

# Ejecutar pilote
motor_rest.ejecutar_pilote("P_001", datetime.now())

# Consultar
disponibles = motor_rest.get_pilotes_disponibles(datetime.now())
```

## Validación

```bash
python test_phase3_complete.py
```

Valida:
- Inicialización de estados
- Ejecución de pilotes
- Aplicación de R1
- Liberación automática de bloqueos
- Cálculo de disponibles
- Consistencia de restricciones

## Complejidad

- Inicializar: O(N)
- Ejecutar pilote: O(K) donde K = número de vecinos
- Liberar bloqueos: O(N × B) donde B = bloqueos por pilote
- Calcular disponibles: O(N)

Performance: aceptable hasta 1000+ pilotes.

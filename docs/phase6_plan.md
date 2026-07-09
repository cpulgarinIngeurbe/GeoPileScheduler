# FASE 6 - Motor de Optimización

**Estado**: 🚧 PLANIFICADA  
**Duración estimada**: 10 tasks  
**Objetivo**: Integrar algoritmos de optimización independientes del simulador

## Visión General

El Motor de Optimización toma decisiones sobre asignación de pilotes y secuenciación. Es completamente independiente de la simulación.

**Responsabilidades**:
- Recibir estado del proyecto
- Generar secuencia de asignaciones (pilote → equipo)
- Optimizar según objetivos multi-objetivo
- Retornar decisión sin modificar estado global

**No responsable de**:
- Ejecutar la simulación
- Validar restricciones (eso lo hace el simulador)
- Administrar tiempo

## Objetivos Multi-Objetivo

Del MODELO_MATEMATICO.md:

1. **O1 - Minimizar Makespan**: Duración total del proyecto
2. **O2 - Minimizar Desbalance**: Equilibrar carga entre equipos
3. **O3 - Maximizar Utilización**: Uso eficiente de equipos
4. **O4 - Minimizar Desplazamientos**: Distancia viajada
5. **O5 - Respetar Precedencias**: Completar dependencias
6. **O6 - Minimizar Esperas**: Tiempo ocioso

Pesos configurables por objetivo.

---

## Tasks

### T1: Interfaz Base de Optimizador
**Archivo**: `src/optimization/base_optimizer.py`

Definir interfaz abstracta:

```python
class BaseOptimizer(ABC):
    def __init__(proyecto, motor_geo, motor_rest, pesos_objetivos)
    @abstractmethod
    def optimizar() -> Solucion
    @abstractmethod
    def nombre() -> str
    def validar_solucion(solucion) -> bool
```

Definir `Solucion`:
- `asignaciones`: list[(equipo_id, pilote_id, timestamp)]
- `makespan`: float (horas)
- `score_multiobjetivo`: float
- `detalles`: dict (por objetivo)

---

### T2: Algoritmo Greedy (Baseline)
**Archivo**: `src/optimization/greedy_optimizer.py`

Implementar estrategia golosa simple:
1. Mientras haya pilotes disponibles:
   - Encontrar equipo libre con menor carga
   - Asignar pilote más cercano
   - Registrar asignación

Características:
- Rápido (O(P × E) donde P=pilotes, E=equipos)
- Baseline para comparación
- Respeta restricciones vía motor_rest
- Determinístico

---

### T3: Algoritmo OR-Tools
**Archivo**: `src/optimization/ortools_optimizer.py`

Usar Google OR-Tools para Vehicle Routing Problem:
- Vehículos = Equipos
- Locaciones = Pilotes
- Capacidad = Rendimiento diario
- Costo = Multi-objetivo ponderado

Características:
- Usa solucionador industrial
- Configurable: busca local, mejorador
- Rápido para instancias medianas (100+ pilotes)
- Determinístico con seed

---

### T4: Algoritmo Genético (Deap)
**Archivo**: `src/optimization/genetic_optimizer.py`

Usar DEAP (Distributed Evolutionary Algorithms in Python):
- Individuo = Secuencia de asignaciones
- Fitness = Multi-objetivo
- Operadores: cruce, mutación, selección
- Población inicial: greedy + random

Características:
- Metaheurística estocástica
- Bueno para exploración
- Configurable: población, generaciones
- Puede mejorar soluciones greedy

---

### T5: Comparador de Algoritmos
**Archivo**: `src/optimization/comparator.py`

Implementar `ComparadorOptimizadores`:
- `ejecutar_todos(proyecto)` → dict de soluciones
- `comparar_resultados()` → tabla de resultados
- `generar_reporte()` → análisis de pros/contras

Métricas por algoritmo:
- Score multi-objetivo
- Tiempo de ejecución
- Makespan
- Utilización promedio
- Desplazamientos totales

---

### T6: Validator de Solución
**Archivo**: `src/optimization/solution_validator.py`

Implementar `validar_solucion()`:
- Verificar que todos los pilotes están asignados
- Verificar que no hay sobreasignación de equipos
- Verificar que asignaciones respetan rendimiento
- Verificar orden temporal consistente
- Generar reporte de validez

---

### T7: Test de Integración Completo
**Archivo**: `test_phase6_complete.py`

Validar flujo 8-pasos:
1. Cargar proyecto
2. Calcular geometría
3. Inicializar restricciones
4. **Ejecutar greedy** ← nuevo
5. **Ejecutar OR-Tools** ← nuevo
6. **Ejecutar genético** ← nuevo
7. **Comparar resultados** ← nuevo
8. Simular mejor solución

Verificar:
- Todos los optimizadores retornan solución válida
- Soluciones son distintas (no triviales)
- OR-Tools mejor que greedy (en promedio)
- Genético converge
- Simulación de mejor solución completa exitosamente

---

### T8: Casos de Prueba
**Archivo**: `create_test_case_6.py`

**CASO 6**: Optimización compleja
- 2 unidades, 4 equipos, 20 pilotes
- Radio crítico pequeño (muchos bloqueos)
- Distancias variadas entre unidades
- Desafío: balanceo de carga + restricciones

---

### T9: Documentación
**Archivo**: `src/optimization/README_PHASE6.md`

Documentar:
- Propósito del motor de optimización
- Objetivos multi-objetivo
- Arquitectura de optimizadores
- Uso de cada algoritmo
- Comparación de algoritmos
- Configuración de pesos
- Limitaciones

---

### T10: Visualización de Soluciones (Opcional)
**Archivo**: `src/optimization/visualizations.py`

Visualizar soluciones:
- `plot_solucion()`: secuencia de asignaciones
- `plot_comparacion()`: comparación de algoritmos
- `plot_convergencia_genetico()`: fitness por generación
- Exportar a HTML

---

## Dependencias

```
FASE 6 depende de:
  ✅ FASE 1-5 (Simulador completo)
  ✅ ortools (libería permitida)
  ✅ deap (librería permitida)
```

---

## Arquitectura

```
src/optimization/
├── __init__.py
├── base_optimizer.py       (Interfaz abstracta)
├── greedy_optimizer.py     (Baseline)
├── ortools_optimizer.py    (Industrial)
├── genetic_optimizer.py    (Metaheurística)
├── comparator.py           (Comparador)
├── solution_validator.py   (Validador)
├── visualizations.py       (Gráficos)
└── README_PHASE6.md        (Documentación)
```

---

## Flujo de Optimización

```
┌─────────────────────────────────┐
│ Proyecto + MotorGeo + MotorRest │
└────────────┬────────────────────┘
             │
        ┌────▼─────────────────┐
        │ BaseOptimizer        │
        │ • Greedy             │
        │ • OR-Tools           │
        │ • Genético           │
        └────┬──────────────────┘
             │
        ┌────▼──────────────┐
        │ Solucion          │
        │ • Asignaciones    │
        │ • Score           │
        │ • Makespan        │
        └────┬──────────────┘
             │
        ┌────▼─────────────────┐
        │ Simular con          │
        │ MotorSimulacion      │
        └─────────────────────┘
```

---

## Aceptación

✅ Greedy genera solución válida  
✅ OR-Tools genera solución válida  
✅ Genético genera solución válida  
✅ Comparador funciona  
✅ Validator valida correctamente  
✅ Simulación ejecuta mejor solución  
✅ Test integración pasa  
✅ Documentación está completa  

---

## Siguiente Fase

**FASE 7 - Análisis y Reportes**: Comparar métodos de optimización, generar estudios científicos, benchmarks.

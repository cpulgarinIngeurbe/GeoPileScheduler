# FASE 6 - Motor de Optimización

## Objetivo

Generar soluciones optimizadas independientes del simulador usando múltiples algoritmos.

## Arquitectura

```
src/optimization/
├── __init__.py                      (Exporta interfaces públicas)
├── base_optimizer.py                (Interfaz abstracta + Solucion)
├── greedy_optimizer.py              (Baseline goloso)
├── ortools_optimizer.py             (VRP industrial)
├── genetic_optimizer.py             (Metaheurística DEAP)
├── comparator.py                    (Comparador multi-algoritmo)
├── solution_validator.py            (Validador)
└── README_PHASE6.md                 (Esta documentación)
```

## Concepto Clave

**Separación de Responsabilidades**:
- **Optimizador**: Toma decisiones (qué pilote → qué equipo)
- **Simulador**: Ejecuta las decisiones
- Nunca se mezclan

## Objetivos Multi-Objetivo

Definidos en MODELO_MATEMATICO.md. Cada solución optimiza:

```
Score = w1×O1 + w2×O2 + w3×O3 + w4×O4 + w5×O5 + w6×O6

Donde:
O1 = Minimizar Makespan (duración total)
O2 = Minimizar Desbalance (equilibrio de carga)
O3 = Maximizar Utilización (uso de equipos)
O4 = Minimizar Desplazamientos (distancia viajada)
O5 = Respetar Precedencias (dependencias)
O6 = Minimizar Esperas (tiempo ocioso)

Pesos configurables:
O1: 0.20  (duración crítica)
O2: 0.20  (balanceo importante)
O3: 0.20  (utilización importante)
O4: 0.15  (desplazamientos secundarios)
O5: 0.15  (precedencias rígidas)
O6: 0.10  (esperas menores)
```

## Módulos

### BaseOptimizer (base_optimizer.py)

Interfaz abstracta que todos implementan:

```python
class BaseOptimizer(ABC):
    @abstractmethod
    def optimizar() -> Solucion
    @abstractmethod
    def nombre() -> str
    def validar_solucion(solucion) -> tuple[bool, list[str]]
    def calcular_score_multiobjetivo(...) -> float
```

### Solucion (base_optimizer.py)

```python
@dataclass
class Solucion:
    nombre_optimizador: str
    asignaciones: list[Asignacion]      # Lista de pilote → equipo
    makespan: float                      # Horas
    score_multiobjetivo: float           # 0-100
    detalles: dict                       # Métricas por objetivo
    tiempo_ejecucion: float              # Segundos
```

### GreedyOptimizer (greedy_optimizer.py)

**Estrategia**: Asignar pilote a equipo con menor carga

```
While pilotes disponibles:
    Para cada pilote:
        Encontrar equipo libre más tempranamente
        Asignar pilote
        Actualizar tiempo de equipo
```

**Características**:
- O(P × E) rápido
- Determinístico
- Baseline para comparación
- Respeta restricciones

### ORToolsOptimizer (ortools_optimizer.py)

**Modelado como Vehicle Routing Problem (VRP)**:
- Vehículos = Equipos
- Nodos = Pilotes
- Capacidad = Rendimiento diario
- Costo = Distancia + multi-objetivo

**Características**:
- Solucionador industrial
- O(P²) complejidad
- Busca local configurada
- Timeout 5 segundos

### GeneticOptimizer (genetic_optimizer.py)

**Usando DEAP (Distributed Evolutionary Algorithms in Python)**:
- Individuo = Permutación de asignaciones
- Fitness = Score multi-objetivo
- Operadores: OX (cruce), Shuffle (mutación)

**Configuración**:
- Población: 50 individuos (configurable)
- Generaciones: 30 (configurable)
- Mutación: 0.2 probabilidad
- Cruce: 0.7 probabilidad

**Características**:
- Metaheurística estocástica
- Explora mejor el espacio
- Puede mejorar greedy
- Reproducible con seed

### ComparadorOptimizadores (comparator.py)

Ejecuta todos los optimizadores:

```python
comparador = ComparadorOptimizadores(proyecto, motor_geo, motor_rest)
comparacion = comparador.ejecutar_todos()  # Greedy + OR-Tools + Genético
comparacion.imprimir_reporte()
mejor_solucion = comparacion.get_mejor_solucion()
```

### ValidadorSolucion (solution_validator.py)

Valida 5 puntos:
- V1: Todos los pilotes asignados
- V2: Sin sobreasignación de equipos
- V3: Timestamps en orden temporal
- V4: Makespan positivo
- V5: Score entre 0-100

## Uso

```python
from src.optimization import GreedyOptimizer, ORToolsOptimizer, GeneticOptimizer
from src.optimization.comparator import ComparadorOptimizadores
from src.optimization.solution_validator import validar_solucion

# Cargar proyecto y motores
proyecto = load_project("proyecto.xlsx")
motor_geo = MotorGeometrico(proyecto)
motor_geo.calcular()
motor_rest = MotorRestricciones(proyecto, motor_geo)
motor_rest.inicializar()

# Ejecutar optimizadores individuales
greedy = GreedyOptimizer(proyecto, motor_geo, motor_rest)
solucion_greedy = greedy.optimizar()

ortools = ORToolsOptimizer(proyecto, motor_geo, motor_rest)
solucion_ortools = ortools.optimizar()

genetico = GeneticOptimizer(proyecto, motor_geo, motor_rest, poblacion=50, generaciones=30)
solucion_genetico = genetico.optimizar()

# Comparar todas
comparador = ComparadorOptimizadores(proyecto, motor_geo, motor_rest)
comparacion = comparador.ejecutar_todos()
comparacion.imprimir_reporte()

# Validar soluciones
for solucion in comparacion.soluciones:
    reporte = validar_solucion(proyecto, solucion)
    reporte.imprimir()

# Simular mejor solución
mejor = comparacion.get_mejor_solucion()
motor_sim = MotorSimulacion(proyecto, motor_geo, motor_rest, motor_rec)
motor_sim.inicializar()
motor_sim.ejecutar()
```

## Validación

```bash
python test_phase6_complete.py
```

Valida:
- Carga de proyecto y motores anteriores (FASE 1-5)
- Ejecución de 3 optimizadores
- Comparación de soluciones
- Validación de consistencia
- Simulación de mejor solución
- Generación de reportes

## Casos de Prueba

### CASO 6: Optimización Compleja
- 2 unidades, 4 equipos, 20 pilotes
- Radio crítico pequeño (7m)
- Equipos con rendimiento variable (1-4 pilotes/día)
- Desafío: balanceo + restricciones + multi-unidad

## Complejidad

| Algoritmo | Complejidad | Tiempo Típico |
|-----------|------------|--------------|
| Greedy | O(P × E) | <100ms |
| OR-Tools | O(P²) | 1-5s |
| Genético | O(G × P × E) | 2-10s |

Donde P = pilotes, E = equipos, G = generaciones

## Configuración de Pesos

Personalizar prioridades:

```python
pesos = {
    "O1_makespan": 0.30,      # Priorizar duración
    "O2_desbalance": 0.15,
    "O3_utilizacion": 0.20,
    "O4_desplazamientos": 0.10,
    "O5_precedencias": 0.15,
    "O6_esperas": 0.10,
}

optimizer = GreedyOptimizer(proyecto, motor_geo, motor_rest, pesos)
```

## Limitaciones

1. **Asignaciones estáticas**: Decisiones tomadas upfront, no adaptativas
2. **Supuesto de duración**: 8h / rendimiento_dia
3. **Desplazamientos estimados**: 5 km/h entre unidades
4. **Determinístico**: Greedy y OR-Tools; Genético con seed
5. **Single-thread**: Ejecución secuencial

## Próxima Fase

**FASE 7 - Análisis y Reportes**: 
- Comparación estadística de métodos
- Benchmarks en instancias variadas
- Generación de papers científicos
- Visualización de resultados

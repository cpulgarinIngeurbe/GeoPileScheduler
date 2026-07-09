# FASE 2 - Motor Geométrico

## Objetivo

Construir la representación espacial completa del proyecto:
- ✅ Matriz de distancias euclidiana entre pilotes
- ✅ Grafo espacial basado en radio crítico
- ✅ Identificación de vecinos geotécnicos
- ✅ Visualizaciones interactivas

## Arquitectura

### Módulos implementados

```
src/geometry/
├── __init__.py
├── distance_matrix.py    (Cálculo de matriz N×N)
├── spatial_graph.py      (Construcción de grafo NetworkX)
├── neighbors.py          (Identificación de vecinos)
├── visualizations.py     (Gráficos Plotly)
├── engine.py             (MotorGeometrico - interfaz integrada)
└── README_PHASE2.md      (Esta documentación)
```

## Uso

### Uso programático

```python
from src.io.loader import load_project
from src.geometry import MotorGeometrico

# Cargar proyecto
proyecto = load_project("data/input/proyecto.xlsx")

# Crear motor
motor = MotorGeometrico(proyecto)

# Ejecutar cálculos
motor.calcular()

# Consultar distancia
distancia = motor.get_distancia("P_001", "P_002")
print(f"Distancia: {distancia:.2f} m")

# Obtener vecinos
vecinos = motor.get_vecinos("P_001")
print(f"Vecinos: {vecinos}")

# Generar visualizaciones
motor.export_heatmap_html("heatmap.html")
motor.export_geometry_html("geometry.html")
```

### Ejecución de validación

```bash
python test_phase2.py
```

Genera:
- `data/output/heatmap_distancias.html`
- `data/output/geometria_proyecto.html`
- `data/output/distribucion_distancias.html`

## Algoritmos

### Matriz de Distancias

**Fórmula**:
```
D[i,j] = sqrt((x_i - x_j)² + (y_i - y_j)²)
```

**Propiedades**:
- Simétrica: D[i,j] = D[j,i]
- Diagonal cero: D[i,i] = 0
- Positiva: D[i,j] ≥ 0

**Implementación**: Vectorizada con NumPy (O(N²) pero muy rápida)

### Grafo Espacial

**Definición**:
- **Nodos**: Todos los pilotes
- **Aristas**: Entre pilotes si D[i,j] ≤ radio_critico_m
- **Pesos**: Distancia euclidiana

**Construcción**:
```python
for i, j in pares_pilotes:
    if distancia[i,j] <= radio_critico:
        agregar_arista(i, j, peso=distancia[i,j])
```

**Propiedades**:
- No dirigido (simétrico)
- Puede tener múltiples componentes conexas
- Densidad depende del radio crítico

### Identificación de Vecinos

**Algoritmo**: Para cada pilote, obtener adyacentes en el grafo
```python
neighbors[pilote_id] = list(graph.neighbors(pilote_id))
```

**Resultado**: Diccionario {pilote_id: [vecino_1, vecino_2, ...]}

## Complejidad Computacional

| Operación | Complejidad | Tiempo (1000 pilotes) |
|-----------|------------|----------------------|
| Matriz distancias | O(N²) | ~1ms |
| Grafo espacial | O(N²) | ~5ms |
| Vecinos | O(N + E) | ~1ms |
| Heatmap | O(N²) | ~100ms |
| Geometría | O(N + E) | ~200ms |

**Total**: ~300ms para 1000 pilotes (aceptable)

## Métodos de MotorGeometrico

### Inicialización

```python
motor = MotorGeometrico(proyecto)
```

### Cálculos

```python
motor.calcular()  # Ejecuta toda la geometría
```

### Consultas

```python
distancia = motor.get_distancia(pilote_id1, pilote_id2)
vecinos = motor.get_vecinos(pilote_id)
tiene_relacion = motor.hay_relacion_geotecnica(pilote_id1, pilote_id2)
stats = motor.get_estadisticas_geometria()
```

### Visualizaciones

```python
fig1 = motor.plot_heatmap()              # Matriz de distancias
fig2 = motor.plot_geometry()             # Proyecto 2D
fig3 = motor.plot_distance_distribution() # Histograma

motor.export_heatmap_html("heatmap.html")
motor.export_geometry_html("geometry.html")
motor.export_distribution_html("dist.html")
```

## Restricción Geotécnica (R1)

El motor geométrico implementa **R1** parcialmente:

✅ **Detecta relaciones geotécnicas**:
- Si D[i,j] ≤ radio_critico_m, i y j tienen restricción temporal

❌ **No implementado aún**:
- Tiempo mínimo entre excavaciones (H)
- Coordinación temporal de restricciones
- Control de bloqueos dinámicos

Esto se implementará en **FASE 3 (Motor de Restricciones)**.

## Visualizaciones

### Heatmap de Distancias

- Matriz N×N de distancias con escala de colores
- Azul = cercano, Rojo = lejano
- Hover muestra distancia exacta

### Geometría del Proyecto

- Scatter plot con coordenadas reales (X, Y)
- Colores por unidad estructural
- Líneas entre pilotes vecinos (radio crítico)
- Tamaño de marcador proporcional a número de vecinos
- Labels con IDs de pilotes

### Distribución de Distancias

- Histograma de todas las distancias
- Muestra cómo están distribuidas las distancias
- Útil para entender el patrón geométrico

## Datos CASO 1

```
5 pilotes en patrón circular
Radio crítico: 10 m
Distancias: 0 → 5 m (todos están conectados)
Grafo: 5 nodos, 10 aristas (completo)
```

## Notas de diseño

1. **Vectorización NumPy**: Matriz se calcula una sola vez, luego se usa
2. **NetworkX Graph**: No dirigido, permite consultar vecinos eficientemente
3. **Plotly interactivo**: Permite zoom, hover, export a PNG
4. **MotorGeometrico wrapper**: Interfaz limpia que encapsula complejidad
5. **Sin hardcodes**: Todo parametrizable desde Proyecto

## Próximos pasos (FASE 3)

- Motor de Restricciones: Manejo dinámico de bloqueos
- Control de tiempo: Implementar restricción temporal (R1)
- Desbloqueo automático: Marcar cuándo se liberan pilotes

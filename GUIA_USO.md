# GuíA de Uso - GeoPile Scheduler

## Descripción General

GeoPile Scheduler es un sistema inteligente para planificación y optimización de proyectos de pilotaje profundo. Toma decisiones sobre qué equipo ejecuta qué pilote, cuándo y en qué orden, respetando restricciones geotécnicas y optimizando múltiples objetivos.

---

## Estructura de Carpetas

```
GeoPileScheduler/
├── data/
│   ├── input/                    # Archivos Excel de entrada
│   │   ├── caso_prueba_3.xlsx    # 1 unidad, 2 equipos, 5 pilotes
│   │   ├── caso_prueba_5.xlsx    # 1 unidad, 3 equipos, 10 pilotes (RECOMENDADO)
│   │   └── caso_prueba_6.xlsx    # 2 unidades, 4 equipos, 20 pilotes (COMPLEJO)
│   └── output/                   # Resultados (se crea automáticamente)
│       ├── 01_progreso.html
│       ├── 02_utilizacion.html
│       ├── 03_eventos.html
│       └── reporte_completo.txt
├── src/
│   ├── core/                     # Modelos de datos
│   ├── io/                       # Carga de Excel
│   ├── geometry/                 # Motor geométrico (distancias, grafo)
│   ├── constraints/              # Motor de restricciones (R1)
│   ├── resources/                # Motor de recursos (equipos)
│   ├── simulation/               # Motor de simulación (event-driven)
│   └── optimization/             # Optimizadores (Greedy, DEAP, OR-Tools)
├── docs/                         # Documentación técnica
├── demo.py                       # Script de demostración (USAR ESTO)
├── test_phase6_complete.py       # Script de prueba completa
└── requirements.txt              # Dependencias
```

---

## Cómo Usar el Sistema

### Opción 1: Demostración Rápida (RECOMENDADO)

```bash
# Ejecutar con archivo por defecto (caso_prueba_5.xlsx)
python demo.py

# Ejecutar con archivo específico
python demo.py data/input/caso_prueba_6.xlsx
```

**Salida esperada:**
```
================================================================================
GEOPILE SCHEDULER - DEMOSTRACIÓN COMPLETA
================================================================================

Archivo de entrada: data/input/caso_prueba_5.xlsx

------------------------------------------------------------------------
[1] CARGAR PROYECTO DESDE EXCEL
------------------------------------------------------------------------
[OK] Proyecto cargado: Caso 5 - Simulación Paralela
     - Pilotes: 10
     - Equipos: 3
     - Unidades: 1

------------------------------------------------------------------------
[2] CALCULAR GEOMETRÍA ESPACIAL
------------------------------------------------------------------------
[OK] Geometría calculada
     - Matriz distancias: (10, 10)
     - Grafo espacial: 10 nodos

... (más pasos) ...

ARCHIVOS GENERADOS EN output/:
  - 01_progreso.html         (Gráfico de progreso)
  - 02_utilizacion.html      (Utilización de equipos)
  - 03_eventos.html          (Distribución de eventos)
  - reporte_completo.txt     (Reporte en texto)
```

---

## Entradas (Input)

### Formato Excel

El archivo de entrada es un Excel con 5 hojas:

#### Hoja 1: Proyecto
```
Proyecto                    FechaInicio      RadioCritico_m    TiempoRestriccion_h
Caso 5 - Simulación Paralela 2026-01-01      8.0               24.0
```

- **Proyecto**: Nombre descriptivo
- **FechaInicio**: Cuándo comienza la simulación
- **RadioCritico_m**: Radio de influencia geotécnica (metros)
- **TiempoRestriccion_h**: Tiempo mínimo entre ejecuciones cercanas (horas)

#### Hoja 2: Unidades
```
UnidadID    Nombre
TORRE_1     Torre 1
TORRE_2     Torre 2
```

#### Hoja 3: Pilotes
```
PiloteID    UnidadID    X      Y
P_001       TORRE_1     0.0    0.0
P_002       TORRE_1     6.0    0.0
P_003       TORRE_1     3.54   3.54
```

- **PiloteID**: Identificador único
- **UnidadID**: A qué unidad pertenece
- **X, Y**: Coordenadas en metros

#### Hoja 4: Equipos
```
EquipoID    Nombre              RendimientoPilotesDia    ModoInicio    ModoFin
EQ_A        Equipo Rápido       3                        AUTO          AUTO
EQ_B        Equipo Medio        2                        AUTO          AUTO
EQ_C        Equipo Lento        1                        AUTO          AUTO
```

- **EquipoID**: Identificador único
- **Nombre**: Descripción
- **RendimientoPilotesDia**: Cuántos pilotes/día ejecuta
- **ModoInicio/ModoFin**: AUTO (automático) o MANUAL

#### Hoja 5: AsignacionEquipos
```
EquipoID    UnidadID    Prioridad
EQ_A        TORRE_1     1
EQ_B        TORRE_1     2
EQ_C        TORRE_1     3
```

- Indica qué equipos trabajan en qué unidades

---

## Salidas (Output)

### 1. Gráficos HTML Interactivos

Abre cualquiera en tu navegador:

#### `01_progreso.html`
- **Qué muestra**: Curva de pilotes ejecutados en el tiempo
- **Para qué**: Ver si la ejecución es lineal, paralela o lenta
- **Eje X**: Tiempo (fecha/hora)
- **Eje Y**: Cantidad de pilotes completados

#### `02_utilizacion.html`
- **Qué muestra**: Cuántos pilotes ejecutó cada equipo
- **Para qué**: Ver si la carga está balanceada
- **Eje X**: Equipos (EQ_A, EQ_B, etc.)
- **Eje Y**: Número de pilotes

#### `03_eventos.html`
- **Qué muestra**: Distribución de eventos por tipo
- **Para qué**: Diagnóstico de qué está pasando en la simulación
- **Eventos**: ASIGNACION, FIN_EJECUCION, BLOQUEO, etc.

### 2. Reporte de Texto

`reporte_completo.txt`
- Resumen de todos los resultados
- Comparación de optimizadores
- Scores y makespan
- Fácil para exportar o compartir

---

## Resultados Explicados

### Ejemplo de Salida

```
Greedy (Baseline):
  Score:         79.8/100
  Makespan:      16.0 horas
  Asignaciones:  10 pilotes
  Tiempo ejecución: 0.00 segundos

Genético (DEAP):
  Score:         80.0/100
  Makespan:      24.0 horas
  Asignaciones:  10 pilotes
  Tiempo ejecución: 0.01 segundos
```

### Qué Significan

| Métrica | Significado | Mejor |
|---------|-----------|--------|
| **Score** | Calidad general (0-100) | Más alto |
| **Makespan** | Duración total (horas) | Más bajo |
| **Asignaciones** | Pilotes procesados | Todos |
| **Tiempo ejecución** | Segundos para optimizar | Más rápido |

### Fórmula del Score

```
Score = 0.20×O1 + 0.20×O2 + 0.20×O3 + 0.15×O4 + 0.15×O5 + 0.10×O6

Donde:
  O1 = Minimizar Makespan (duración)
  O2 = Minimizar Desbalance (equilibrio de carga)
  O3 = Maximizar Utilización (uso de equipos)
  O4 = Minimizar Desplazamientos (distancia viajada)
  O5 = Respetar Precedencias (dependencias)
  O6 = Minimizar Esperas (tiempo ocioso)
```

---

## Casos de Prueba Disponibles

| Archivo | Unidades | Equipos | Pilotes | Complejidad | Caso de Uso |
|---------|----------|---------|---------|------------|-----------|
| `caso_prueba_3.xlsx` | 1 | 2 | 5 | Baja | Pruebas rápidas |
| `caso_prueba_5.xlsx` | 1 | 3 | 10 | Media | **RECOMENDADO** |
| `caso_prueba_6.xlsx` | 2 | 4 | 20 | Alta | Estrés |

---

## Cómo Crear tu Propio Caso de Prueba

1. Copia `caso_prueba_5.xlsx`
2. Modifica los datos:
   - Cambia coordenadas de pilotes
   - Agrega más equipos
   - Ajusta rendimientos
3. Guarda en `data/input/`
4. Ejecuta: `python demo.py data/input/tu_archivo.xlsx`

---

## Algoritmos Disponibles

El sistema automáticamente prueba 3 optimizadores:

### 1. Greedy (Baseline)
- **Velocidad**: Muy rápido (<1ms)
- **Calidad**: Buena (baseline)
- **Algoritmo**: Asigna equipo con menor carga
- **Uso**: Referencia, pruebas rápidas

### 2. Genético (DEAP)
- **Velocidad**: Lento (1-10s)
- **Calidad**: Muy buena (80%+)
- **Algoritmo**: Evoluciona población de soluciones
- **Uso**: Optimización seria

### 3. OR-Tools (Industrial)
- **Velocidad**: Medio (1-5s)
- **Calidad**: Excelente (85%+)
- **Algoritmo**: Solucionador VRP profesional
- **Estado**: Requiere instalación especial en Windows

---

## Preguntas Frecuentes

### ¿Dónde quedan los resultados?

En la carpeta `output/`:
```
output/
├── 01_progreso.html
├── 02_utilizacion.html
├── 03_eventos.html
└── reporte_completo.txt
```

### ¿Puedo ver los gráficos?

Sí, son HTML. Abre cualquiera en tu navegador:
```
# En Windows
start output/01_progreso.html

# En Linux/Mac
open output/01_progreso.html
```

### ¿Cuánto tarda la ejecución?

- Cargar proyecto: <1s
- Geometría: <1s
- Optimizadores: 0.01 - 10s (depende del tamaño)
- Simulación: <1s
- **Total**: 1-15 segundos

### ¿Qué pasa si hay un error?

Mira la salida de consola. Incluirá:
- Qué paso falló
- Por qué falló
- Línea del código

### ¿Cómo cambio los pesos de optimización?

Aún no hay interfaz fácil. Requiere editar código Python. Próxima versión.

### ¿Puedo exportar a Excel los resultados?

Sí, crea un script personalizado. El reporte está en `output/reporte_completo.txt`.

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `FileNotFoundError: caso_prueba_5.xlsx` | Verifica que exista en `data/input/` |
| `ModuleNotFoundError: pandas` | Instala: `pip install -r requirements.txt` |
| Gráficos HTML no abren | Son interactivos. Abre en navegador moderno (Chrome, Firefox) |
| Modelo muy lento | Usa `caso_prueba_3.xlsx` (más pequeño) |

---

## Contacto / Soporte

Para reportar bugs o sugerir mejoras:
- GitHub: https://github.com/cpulgarinIngeurbe/GeoPileScheduler
- Email: cpulgarin@construccion.com.co

---

**Versión**: 1.0 (FASE 1-6 completa)  
**Última actualización**: 2026-07-09

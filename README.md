# GeoPile Scheduler

Sistema inteligente para la planificación y optimización de secuencias constructivas de pilotaje.

## Descripción

GeoPile Scheduler es una plataforma científica para la planificación automatizada de proyectos de pilotaje en cimentación profunda. El sistema simula la ejecución completa del proyecto y genera la planificación óptima considerando simultáneamente:

- **Restricciones geotécnicas** (radio crítico, tiempo entre excavaciones)
- **Restricciones operativas** (rendimiento, compatibilidad de equipos, unidades)
- **Optimización multiobjetivo** (duración, distancia, continuidad, carga de equipos)
- **Múltiples equipos y unidades estructurales**

## Características

- ✅ Simulación realista de obras de pilotaje
- ✅ Optimizadores intercambiables (OR-Tools, Algoritmos Genéticos, Simulated Annealing, Tabu Search)
- ✅ Validación automática de restricciones
- ✅ Indicadores de desempeño y análisis
- ✅ Visualizaciones interactivas
- ✅ Escalabilidad hasta 1000+ pilotes
- ✅ Entrada/salida vía Excel

## Documentación

La documentación completa del proyecto se encuentra en la carpeta `docs/`:

- **[CLAUDE.md](docs/CLAUDE.md)** - Guía maestra de desarrollo
- **[ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Arquitectura del sistema
- **[ESPECIFICACION_FUNCIONAL.md](docs/ESPECIFICACION_FUNCIONAL.md)** - Especificación funcional
- **[MODELO_MATEMATICO.md](docs/MODELO_MATEMATICO.md)** - Formalización matemática
- **[MODELO_DATOS.md](docs/MODELO_DATOS.md)** - Esquema Excel oficial
- **[CRITERIOS.md](docs/CRITERIOS.md)** - Restricciones y objetivos de optimización
- **[CASOS_PRUEBA.md](docs/CASOS_PRUEBA.md)** - 16 casos de validación oficial
- **[ROADMAP.md](docs/ROADMAP.md)** - Plan de desarrollo en 13 fases

## Estructura

```
GeoPileScheduler/
├── docs/                 # Documentación oficial
├── src/                  # Código fuente Python
│   ├── core/            # Modelos y tipos de datos
│   ├── geometry/        # Motor geométrico
│   ├── constraints/     # Motor de restricciones
│   ├── resources/       # Gestor de equipos
│   ├── simulation/      # Motor de simulación
│   ├── optimization/    # Motor de optimización
│   ├── validation/      # Validador global
│   ├── io/              # Carga/exportación
│   └── utils/           # Utilidades
├── tests/                # Tests unitarios
├── notebooks/            # Jupyter notebooks
├── data/
│   ├── input/           # Archivos Excel de entrada
│   └── output/          # Resultados generados
└── requirements.txt     # Dependencias
```

## Instalación

### Requisitos
- Python 3.12+
- pip

### Setup

```bash
# Clonar repositorio
git clone https://github.com/cpulgarinIngeurbe/GeoPileScheduler.git
cd GeoPileScheduler

# Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso Rápido

```python
from geopile.core import load_project
from geopile.optimization import ORToolsOptimizer
from geopile.simulation import SimulationEngine

# Cargar proyecto desde Excel
project = load_project('data/input/proyecto.xlsx')

# Crear motor de simulación
simulation = SimulationEngine(project)

# Crear optimizador
optimizer = ORToolsOptimizer(project)

# Resolver
schedule = optimizer.solve()

# Simular
results = simulation.run(schedule)

# Exportar
results.export_excel('data/output/resultados.xlsx')
results.plot_gantt()
```

## Fases de Desarrollo

El proyecto se desarrolla en 13 fases incrementales:

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Diseño del sistema | ✅ Completado |
| 1 | Base del proyecto | ⏳ En desarrollo |
| 2 | Motor geométrico | ⏳ Pendiente |
| 3 | Motor de restricciones | ⏳ Pendiente |
| 4 | Motor de recursos | ⏳ Pendiente |
| 5 | Motor de simulación | ⏳ Pendiente |
| 6 | Primer optimizador (OR-Tools) | ⏳ Pendiente |
| 7 | Validación global | ⏳ Pendiente |
| 8 | Visualización | ⏳ Pendiente |
| 9 | Comparación de optimizadores | ⏳ Pendiente |
| 10 | Optimización inicio/fin automático | ⏳ Pendiente |
| 11 | Inteligencia Artificial | ⏳ Pendiente |
| 12 | Versión 1.0 | ⏳ Pendiente |

Ver [ROADMAP.md](docs/ROADMAP.md) para detalles completos.

## Principios Clave

1. **Simulación > Optimización**: El motor de simulación es independiente del optimizador
2. **Optimizadores intercambiables**: Varios algoritmos bajo una interfaz única
3. **Validación rigurosa**: 16 casos de prueba por fase
4. **Investigación**: Diseñado para comparar métodos y generar nuevos conocimientos
5. **Extensibilidad**: Preparado para nuevas restricciones y algoritmos

## Restricciones Obligatorias

El sistema garantiza:

- **R1**: Restricción geotécnica (radio crítico + tiempo mínimo)
- **R2**: Rendimiento diario respetado
- **R3**: Exclusividad de equipos (1 pilote por equipo)
- **R4**: Compatibilidad equipo-unidad
- **R5**: Coordinación global entre equipos
- **R6**: Todos los pilotes ejecutados exactamente una vez
- **R7**: Respeto a puntos de inicio/fin manuales

Ver [CRITERIOS.md](docs/CRITERIOS.md) para detalles.

## Contribuciones

Este es un proyecto de investigación aplicada. Las contribuciones deben mantener la independencia entre simulación y optimización.

## Licencia

[Especificar licencia]

## Autor

Autor: cpulgarin@construccion.com.co

## Contacto

Para preguntas, reportar bugs o sugerencias, contactar al equipo de desarrollo.

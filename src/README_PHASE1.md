# FASE 1 - Base del Proyecto

## Objetivo

Construir la estructura base del sistema capaz de:
- ✅ Leer archivos Excel con estructura oficial
- ✅ Validar datos según MODELO_DATOS.md
- ✅ Construir modelo interno del proyecto
- ✅ Generar resumen estadístico

## Arquitectura

### Módulos implementados

```
src/
├── core/
│   ├── __init__.py
│   ├── models.py       (5 clases: Proyecto, UnidadEstructural, Pilote, Equipo, AsignacionEquipo)
│   └── enums.py        (3 enumeraciones: ModoInicio, ModoFin, EstadoPilote)
├── io/
│   ├── __init__.py
│   ├── loader.py       (Cargador Excel → Proyecto)
│   └── validator.py    (Validador de datos)
└── utils/
    ├── __init__.py
    └── project_summary.py (Resumen estadístico)
```

## Uso

### 1. Crear archivo de prueba

```bash
python create_test_case_1.py
```

Genera: `data/input/caso_prueba_1.xlsx`

### 2. Ejecutar validación

```bash
python test_phase1.py
```

Salida esperada:
```
[1/4] Verificando archivo de prueba... ✅
[2/4] Cargando proyecto desde Excel... ✅
[3/4] Validando contenido del proyecto... ✅
[4/4] Generando resumen estadístico... ✅

✅ FASE 1 COMPLETADA EXITOSAMENTE
```

### 3. Uso programático

```python
from src.io.loader import load_project
from src.utils.project_summary import summarize_project

# Cargar proyecto
proyecto = load_project("data/input/mi_proyecto.xlsx")

# Acceder a datos
print(f"Unidades: {proyecto.num_unidades}")
print(f"Equipos: {proyecto.num_equipos}")
print(f"Pilotes: {proyecto.num_pilotes}")

# Generar resumen
resumen = summarize_project(proyecto)
```

## Estructura de datos

### Archivo Excel requerido

Debe contener exactamente 5 hojas:

#### 1. Proyecto (1 fila de datos)

| Proyecto | FechaInicio | RadioCritico_m | TiempoRestriccion_h |
|----------|-------------|-----------------|-------------------|
| Nombre   | YYYY-MM-DD  | 10.0           | 24.0              |

#### 2. Unidades (N filas)

| UnidadID | Nombre    |
|----------|-----------|
| TORRE_1  | Torre 1   |
| PODIO    | Podio     |

#### 3. Pilotes (N filas)

| PiloteID | UnidadID | X     | Y     |
|----------|----------|-------|-------|
| P_001    | TORRE_1  | 0.0   | 0.0   |
| P_002    | TORRE_1  | 5.0   | 0.0   |

#### 4. Equipos (M filas)

| EquipoID | Nombre   | RendimientoPilotesDia | ModoInicio | PiloteInicio | ModoFin | PiloteFin |
|----------|----------|----------------------|------------|--------------|---------|-----------|
| EQ_A     | Equipo A | 2                    | MANUAL     | P_001        | MANUAL  | P_005     |

#### 5. AsignacionEquipos (P filas)

| EquipoID | UnidadID | Prioridad |
|----------|----------|-----------|
| EQ_A     | TORRE_1  | 1         |

## Validaciones implementadas

### Por hoja

- **Proyecto**: Campos obligatorios, tipos correctos, valores válidos
- **Unidades**: IDs únicos, nombres no vacíos
- **Pilotes**: IDs únicos, coordenadas válidas (no negativas), unidades referenciadas
- **Equipos**: IDs únicos, rendimiento > 0, modo inicio/fin válidos
- **AsignacionEquipos**: Prioridad es entero, referencias existen

### Referencias cruzadas

- Pilotes referenciados por equipos (inicio/fin manual) existen
- Unidades en pilotes existen en hoja Unidades
- Equipos en asignaciones existen en hoja Equipos
- Unidades en asignaciones existen en hoja Unidades

## Modelos de datos

### Clase Proyecto

```python
@dataclass
class Proyecto:
    nombre: str
    fecha_inicio: datetime
    radio_critico_m: float
    tiempo_restriccion_h: float
    unidades: Dict[str, UnidadEstructural]
    equipos: Dict[str, Equipo]
    asignaciones: List[AsignacionEquipo]
    
    # Métodos
    agregar_unidad(unidad: UnidadEstructural)
    agregar_equipo(equipo: Equipo)
    obtener_pilote(pilote_id: str) -> Optional[Pilote]
    obtener_unidad_pilote(pilote_id: str) -> Optional[UnidadEstructural]
```

### Clase UnidadEstructural

```python
@dataclass
class UnidadEstructural:
    id: str
    nombre: str
    pilotes: Dict[str, Pilote]
    
    # Métodos
    agregar_pilote(pilote: Pilote)
```

### Clase Pilote

```python
@dataclass
class Pilote:
    id: str
    unidad_id: str
    x: float
    y: float
    estado: EstadoPilote = PENDIENTE
    
    # Métodos
    distancia_a(otro: Pilote) -> float
```

### Clase Equipo

```python
@dataclass
class Equipo:
    id: str
    nombre: str
    rendimiento_pilotes_dia: int
    modo_inicio: ModoInicio
    pilote_inicio: Optional[str]
    modo_fin: ModoFin
    pilote_fin: Optional[str]
```

## Casos de prueba validados

### CASO 1: Base simple
- ✅ 1 unidad, 1 equipo, 5 pilotes
- ✅ Inicio/fin manuales
- ✅ Carga sin errores
- ✅ Resumen generado

## Próximos pasos (FASE 2)

La siguiente fase implementará:
- Motor Geométrico: Matriz de distancias, grafo espacial
- Visualización de geometría
- Identificación de vecinos

## Notas de diseño

1. **Sin dependencias innecesarias**: Solo pandas, openpyxl, numpy
2. **Type hints completos**: Todas las funciones públicas tipadas
3. **Validación robusta**: Errores descriptivos, referencias cruzadas
4. **Modular**: Cada módulo responsabilidad única
5. **Extensible**: Fácil agregar nuevas validaciones

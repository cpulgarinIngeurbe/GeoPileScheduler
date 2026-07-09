# FASE 5 - Motor de Simulación

**Estado**: 🚧 PLANIFICADA  
**Duración estimada**: 10 tasks  
**Objetivo**: Integrar los tres motores en un simulador event-driven

## Visión General

El Motor de Simulación (MotorSimulacion) es el núcleo del sistema. Coordina los tres motores anteriores en una simulación temporal que representa la ejecución real de un proyecto de pilotaje.

**Responsabilidades**:
- Administrar tiempo
- Administrar eventos
- Actualizar estados globales
- Coordinar módulos
- Generar estadísticas
- Permitir visualización del progreso

**No responsable de**:
- Optimización (eso es FASE 6+)
- Decisiones de asignación (eso es el Optimizador)
- Restricciones específicas (eso son los motores)

---

## Tasks

### T1: Event Model para Simulación
**Archivo**: `src/simulation/event_model.py`

Definir tipos de eventos:
- `EventoInicio`: simulación comienza
- `EventoFin`: simulación finaliza
- `EventoAsignacion`: equipo asignado a pilote
- `EventoEjecucion`: pilote ejecutado
- `EventoBloqueo`: pilote bloqueado
- `EventoDesbloqueo`: pilote desbloqueado
- `EventoAvance`: reporte de progreso

Cada evento tiene:
- `tipo`: enum
- `timestamp`: datetime
- `entidad_id`: str (pilote, equipo)
- `datos`: dict (contexto)
- `severidad`: enum (INFO, WARNING, ERROR)

---

### T2: Event Queue and Scheduler
**Archivo**: `src/simulation/event_queue.py`

Implementar:
- `EventQueue`: cola de prioridad ordenada por timestamp
- `push()`: agregar evento
- `pop()`: obtener próximo evento
- `peek()`: ver próximo sin remover
- `empty()`: verificar si está vacía

Garantías:
- Eventos procesados en orden temporal
- O(log N) para agregar y remover
- Manejo de eventos simultáneos

---

### T3: Simulador Principal
**Archivo**: `src/simulation/engine.py`

Implementar `MotorSimulacion`:

```python
class MotorSimulacion:
    def __init__(proyecto, motor_geo, motor_rest, motor_rec)
    def inicializar() -> bool
    def ejecutar() -> bool
    def ejecutar_paso() -> tuple[EventoSimulacion, bool]
    def get_estado_global() -> EstadoGlobal
    def get_progreso() -> dict
    def get_eventos_historial() -> list[EventoSimulacion]
    def get_timeline() -> dict
```

Flujo:
1. Inicializar todos los motores
2. Loop: obtener evento → procesarlo → registrarlo
3. Condición de fin: todos los pilotes ejecutados
4. Retornar estadísticas finales

---

### T4: Validator de Simulación
**Archivo**: `src/simulation/validator.py`

Implementar `validar_simulacion()`:
- Verificar que todas las restricciones se respetaron
- Verificar que todos los pilotes se ejecutaron
- Verificar que no hay inconsistencias de estado
- Verificar que el timeline es válido
- Generar reporte de validación

Retornar: `ReporteValidacionSimulacion` con:
- `es_valida`: bool
- `errores`: list[str]
- `advertencias`: list[str]
- `estadisticas`: dict

---

### T5: Estadísticas y Métricas
**Archivo**: `src/simulation/statistics.py`

Implementar calculadores:
- `calcular_tiempo_total()`: duración simulación
- `calcular_utilization_equipos()`: uso de cada equipo
- `calcular_eficiencia_espacial()`: distancia vs productiva
- `calcular_secuencia_ejecucion()`: orden de pilotes
- `calcular_makespan()`: tiempo total proyecto

Retornar: `EstadisticasSimulacion` con todas las métricas

---

### T6: Visualizaciones de Simulación
**Archivo**: `src/simulation/visualizations.py`

Implementar:
- `plot_timeline()`: línea temporal de eventos
- `plot_gantt()`: diagrama Gantt de equipos
- `plot_progression()`: progreso de ejecución
- `plot_equipment_utilization()`: uso de equipos
- `plot_event_histogram()`: distribución de eventos

Exportar a HTML interactivo

---

### T7: Test de Integración Completo
**Archivo**: `test_phase5_complete.py`

Validar flujo 6-pasos:
1. Cargar proyecto
2. Calcular geometría
3. Inicializar restricciones
4. Inicializar recursos
5. **Ejecutar simulación** ← nuevo
6. Validar y generar reportes

Verificar:
- Simulación completa sin errores
- Todos los pilotes ejecutados
- Restricciones respetadas
- Estadísticas generadas
- Visualizaciones creadas

---

### T8: Casos de Prueba (CASO 4 y CASO 5)
**Archivos**: `create_test_case_4.py`, `create_test_case_5.py`

**CASO 4**: Simulación simple lineal
- 1 unidad, 1 equipo, 5 pilotes
- Sin bloqueos
- Rendimiento 2 pilotes/día
- Verificar ejecución secuencial

**CASO 5**: Simulación con paralelismo
- 1 unidad, 3 equipos, 10 pilotes
- Radio crítico pequeño (bloqueos)
- Equipos con distinto rendimiento
- Verificar ejecución paralela con restricciones

---

### T9: Documentación
**Archivo**: `src/simulation/README_PHASE5.md`

Documentar:
- Propósito del Motor de Simulación
- Arquitectura de eventos
- Ciclo de simulación
- Uso del MotorSimulacion
- Ejemplos de código
- Validación y estadísticas
- Limitaciones y supuestos

---

### T10: Visualización Avanzada (Opcional)
**Archivo**: `src/simulation/advanced_visualizations.py`

Implementar:
- `plot_animation()`: animación 2D de ejecución
- `plot_3d_timeline()`: visualización 3D de progreso
- `plot_constraint_satisfaction()`: cumplimiento de R1-R7
- Exportar a video o GIF

**Nota**: Es componente Nice-To-Have, no crítico

---

## Dependencias

```
FASE 5 depende de:
  ✅ FASE 1 (Modelos + Loader)
  ✅ FASE 2 (MotorGeometrico)
  ✅ FASE 3 (MotorRestricciones)
  ✅ FASE 4 (MotorRecursos)
```

---

## Aceptación

✅ Simulación ejecuta correctamente  
✅ Todos los pilotes se ejecutan  
✅ Restricciones se respetan  
✅ Estadísticas son correctas  
✅ Visualizaciones funcionan  
✅ Test integración pasa  
✅ Documentación está completa  

---

## Siguiente Fase

**FASE 6 - Motor de Optimización**: Integrar algoritmo de asignación (OR-Tools, Genéticos, etc.)

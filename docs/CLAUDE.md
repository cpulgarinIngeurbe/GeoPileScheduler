# CLAUDE.md

# GeoPile Scheduler

## Guía Maestra de Desarrollo

---

# Propósito

Este documento define las reglas de desarrollo del proyecto **GeoPile Scheduler**.

Todas las decisiones de diseño e implementación deberán respetar este documento.

En caso de conflicto entre una implementación y esta guía, deberá prevalecer esta guía.

---

# Descripción del proyecto

GeoPile Scheduler es una plataforma científica para la planificación inteligente de proyectos de pilotaje.

El sistema tiene como objetivo optimizar la ejecución de pilotes considerando simultáneamente:

* restricciones geotécnicas;
* restricciones espaciales;
* restricciones temporales;
* múltiples equipos de pilotaje;
* múltiples unidades estructurales;
* simulación completa del proceso constructivo.

El proyecto está orientado a investigación aplicada y deberá mantenerse preparado para futuras publicaciones científicas.

---

# Filosofía del proyecto

Este proyecto **no busca únicamente generar una secuencia de pilotes**.

Su objetivo es construir un **motor de simulación y optimización** capaz de representar el comportamiento real de una obra de pilotaje.

La simulación es el núcleo del sistema.

La optimización es un componente intercambiable.

---

# Principios de arquitectura

Todo el software deberá seguir los siguientes principios:

* Arquitectura modular.
* Bajo acoplamiento.
* Alta cohesión.
* Responsabilidad única (SRP).
* Interfaces claras entre módulos.
* Componentes fácilmente reemplazables.
* Código orientado a mantenimiento.
* Código orientado a investigación.

No deberán existir dependencias innecesarias entre módulos.

---

# Entorno de desarrollo

El sistema deberá ejecutarse completamente en:

* Python 3.12
* Google Colab

El código no dependerá de:

* Docker
* Kubernetes
* Bases de datos
* Servicios externos
* APIs
* Infraestructura cloud

Todo deberá ejecutarse localmente dentro del notebook utilizando archivos Excel como entrada.

---

# Librerías permitidas

Se priorizará el uso de:

* pandas
* numpy
* networkx
* scipy
* ortools
* deap
* plotly
* matplotlib
* openpyxl

No incorporar nuevas dependencias sin una justificación técnica.

---

# Organización del proyecto

```text
GeoPileScheduler/

docs/
data/
src/
tests/
notebooks/
output/
```

Cada módulo tendrá una única responsabilidad.

---

# Documentación

Todo módulo deberá incluir:

* descripción;
* propósito;
* entradas;
* salidas;
* dependencias.

Las funciones públicas deberán incluir:

* docstring;
* tipos;
* descripción de parámetros;
* valor de retorno;
* posibles excepciones.

---

# Tipado

Todo el código deberá utilizar type hints.

Ejemplo:

def calcular_distancias(...) -> ...

No utilizar funciones públicas sin tipado.

---

# Estilo de programación

Priorizar:

* claridad;
* simplicidad;
* legibilidad;
* mantenimiento.

Evitar:

* funciones excesivamente largas;
* duplicación de código;
* variables ambiguas;
* constantes "quemadas" en el código.

Toda constante configurable deberá provenir del modelo del proyecto.

---

# Manejo de errores

Nunca permitir errores silenciosos.

Los errores deberán:

* ser detectados;
* describirse claramente;
* indicar la posible causa.

---

# Modelo de datos

La estructura oficial de entrada es el archivo Excel definido para el proyecto.

No modificar dicha estructura sin actualizar previamente la documentación.

---

# Motor de simulación

El Motor de Simulación es el componente central del sistema.

Debe ser completamente independiente del algoritmo de optimización.

Su responsabilidad es:

* administrar el tiempo;
* administrar eventos;
* actualizar estados;
* coordinar los módulos.

Nunca deberá tomar decisiones de optimización.

---

# Motor de optimización

El optimizador solamente toma decisiones.

No administra:

* tiempo;
* estados;
* eventos;
* restricciones.

Debe recibir un estado del sistema y devolver una decisión.

---

# Estrategia de optimización

La arquitectura deberá permitir utilizar distintos algoritmos.

Ejemplos:

* OR-Tools
* Algoritmos Genéticos
* Simulated Annealing
* Tabu Search

Todos deberán implementar la misma interfaz.

No acoplar la arquitectura a un único método de optimización.

---

# Restricciones geotécnicas

Las restricciones nunca deberán estar codificadas directamente.

Siempre deberán provenir de la configuración del proyecto.

---

# Desarrollo incremental

El desarrollo seguirá estrictamente el ROADMAP.md.

No implementar funcionalidades de fases posteriores.

Cada fase deberá:

* compilar;
* ejecutarse;
* validarse;
* documentarse.

Solo entonces podrá iniciarse la siguiente.

---

# Pruebas

Cada módulo deberá ser verificable de forma independiente.

Las pruebas deberán ser simples, reproducibles y fáciles de interpretar.

---

# Visualización

Las visualizaciones deberán utilizar preferentemente Plotly.

El objetivo es facilitar la interpretación del proceso constructivo y la depuración del algoritmo.

---

# Rendimiento

No optimizar prematuramente.

Primero:

* claridad;
* estabilidad;
* exactitud.

Posteriormente:

* rendimiento.

---

# Investigación

Las decisiones de diseño deberán favorecer la comparación de métodos de optimización.

El sistema deberá permitir ejecutar exactamente el mismo caso de estudio utilizando distintos algoritmos sin modificar el motor de simulación.

---

# Código reutilizable

Siempre que sea posible:

* evitar código duplicado;
* reutilizar funciones;
* encapsular lógica repetitiva.

---

# Convenciones

Clases:

PascalCase

Funciones:

snake_case

Variables:

snake_case

Constantes:

UPPER_CASE

---

# Commits

Cada fase del roadmap deberá finalizar con un commit independiente.

No mezclar varias fases en un mismo commit.

---

# Regla más importante

Antes de escribir código, preguntarse:

> **¿Esta implementación mantiene la independencia entre simulación, optimización y restricciones?**

Si la respuesta es no, deberá replantearse el diseño.

---

# Comportamiento esperado de Claude

Durante todo el desarrollo, Claude deberá actuar como un Arquitecto de Software Senior especializado en Python científico y optimización.

Antes de implementar una funcionalidad deberá:

1. Verificar que pertenece a la fase actual del ROADMAP.
2. Confirmar que no rompe la arquitectura.
3. Proponer alternativas si identifica un diseño mejor.
4. Explicar brevemente las decisiones arquitectónicas relevantes.
5. Implementar únicamente el alcance solicitado.

No deberá añadir funcionalidades fuera del alcance de la fase actual sin aprobación explícita.

---

# Objetivo final

Construir una plataforma de investigación robusta, mantenible y extensible para la planificación inteligente del pilotaje, capaz de integrar múltiples métodos de optimización bajo una arquitectura única basada en simulación de eventos y análisis espacial.

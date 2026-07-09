# CRITERIOS.md

# GeoPile Scheduler

## Criterios de Diseño, Restricciones y Optimización

---

# 1. Objetivo

Definir todos los criterios que una planificación debe satisfacer para considerarse válida y óptima.

---

# 2. Clasificación

Los criterios se dividen en cuatro grupos:

1. Restricciones obligatorias.
2. Objetivos de optimización.
3. Criterios de calidad.
4. Criterios de extensibilidad.

---

# 3. Restricciones obligatorias

Estas restricciones nunca podrán violarse.

## R1. Restricción geotécnica

Dos pilotes ubicados dentro del radio crítico deberán respetar el tiempo mínimo entre excavaciones.

---

## R2. Rendimiento

Cada equipo únicamente podrá ejecutar el número de pilotes correspondiente a su rendimiento diario.

---

## R3. Exclusividad

Un equipo no podrá ejecutar dos pilotes simultáneamente.

---

## R4. Compatibilidad

Un equipo únicamente podrá ejecutar pilotes pertenecientes a unidades estructurales para las cuales esté autorizado.

---

## R5. Coordinación entre equipos

Todos los equipos deberán respetar simultáneamente las restricciones geotécnicas.

Esto aplica incluso cuando pertenezcan a unidades estructurales diferentes.

---

## R6. Integridad del proyecto

Todos los pilotes deberán ejecutarse exactamente una vez.

---

## R7. Inicio y fin manual

Cuando el usuario defina manualmente un punto de inicio o de finalización, el sistema deberá respetarlo.

---

# 4. Objetivos de optimización

El algoritmo buscará minimizar:

* duración total del proyecto;
* distancia recorrida por los equipos;
* cambios innecesarios entre unidades estructurales;
* tiempos muertos;
* retornos innecesarios;
* recorridos sin producción.

---

# 5. Objetivos operativos

El sistema deberá procurar:

* continuidad del frente de trabajo;
* utilización eficiente de los equipos;
* equilibrio de carga entre equipos;
* reducción de esperas.

---

# 6. Decisiones automáticas

Cuando corresponda, el sistema decidirá:

* mejor punto de inicio;
* mejor punto de finalización;
* siguiente pilote;
* mejor equipo para ejecutarlo;
* momento de cambio de unidad estructural.

---

# 7. Casos operativos admitidos

El sistema deberá resolver:

* una unidad con un equipo;
* una unidad con múltiples equipos;
* múltiples unidades con un equipo por unidad;
* múltiples unidades con múltiples equipos;
* equipos compartidos entre varias unidades.

---

# 8. Principios de planificación

La máquina nunca deberá permanecer inactiva si existen pilotes disponibles compatibles con todas las restricciones.

Cuando un pilote permanezca bloqueado por tiempo geotécnico, el sistema deberá buscar alternativas cercanas para mantener la continuidad del frente y minimizar futuros desplazamientos.

---

# 9. Validación final

Una solución será aceptada únicamente cuando:

* todos los pilotes hayan sido ejecutados;
* no existan conflictos geotécnicos;
* todos los equipos respeten su rendimiento;
* todas las restricciones hayan sido satisfechas.

---

# 10. Principio fundamental

El sistema no optimiza únicamente una secuencia.

El sistema optimiza la ejecución completa de la obra considerando simultáneamente espacio, tiempo, recursos y restricciones.

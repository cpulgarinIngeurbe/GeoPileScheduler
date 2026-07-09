# CASOS_PRUEBA.md

# GeoPile Scheduler

## Casos Oficiales de Validación

---

# Objetivo

Garantizar que cada módulo del sistema funcione correctamente antes de avanzar a la siguiente fase del desarrollo.

---

# Caso 1

Una unidad estructural.

Un equipo.

Inicio manual.

Fin manual.

---

# Caso 2

Una unidad estructural.

Un equipo.

Inicio automático.

Fin automático.

---

# Caso 3

Una unidad estructural.

Dos equipos.

Ambos con inicio manual.

Validar que nunca se crucen ni incumplan restricciones geotécnicas.

---

# Caso 4

Una unidad estructural.

Tres equipos.

Balancear automáticamente la carga de trabajo.

---

# Caso 5

Dos unidades estructurales.

Un equipo por unidad.

Validar conflictos entre unidades al finalizar la planificación.

---

# Caso 6

Dos unidades estructurales.

Un equipo compartido entre ambas.

Validar la decisión de cambio de unidad estructural.

---

# Caso 7

Tres unidades estructurales.

Cinco equipos.

Dos equipos compartidos.

Evaluar coordinación global.

---

# Caso 8

Radio crítico pequeño.

Verificar incremento de productividad.

---

# Caso 9

Radio crítico grande.

Verificar incremento de bloqueos y correcta selección de alternativas.

---

# Caso 10

Rendimiento de un pilote por día.

Comprobar el avance correcto de la simulación.

---

# Caso 11

Rendimiento de cuatro pilotes por día.

Verificar que nunca se exceda el rendimiento configurado.

---

# Caso 12

Inicio manual.

Comparar la solución obtenida con la solución automática.

---

# Caso 13

Fin manual.

Comparar la solución obtenida con la solución automática.

---

# Caso 14

Proyecto con 100 pilotes.

Validar resultados.

---

# Caso 15

Proyecto con 500 pilotes.

Evaluar rendimiento computacional.

---

# Caso 16

Proyecto con más de 1.000 pilotes.

Validar escalabilidad del sistema.

---

# Criterios de aceptación

Cada caso de prueba será considerado satisfactorio cuando:

* la simulación finalice sin errores;
* todos los pilotes sean ejecutados;
* no existan conflictos geotécnicos;
* se respeten todas las restricciones del proyecto;
* los indicadores sean generados correctamente.

---

# Estrategia de validación

Cada fase del ROADMAP deberá superar los casos de prueba correspondientes antes de iniciar la siguiente fase del desarrollo.

Los casos de prueba crecerán progresivamente conforme se incorporen nuevas funcionalidades.

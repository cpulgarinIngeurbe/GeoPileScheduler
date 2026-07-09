# MODELO_DATOS.md

# GeoPile Scheduler

## Modelo de Datos Oficial

---

# 1. Objetivo

Definir el modelo de datos oficial del sistema GeoPile Scheduler.

Este documento constituye el contrato de intercambio de información entre el usuario y el sistema. Ningún módulo podrá asumir estructuras de datos diferentes a las aquí definidas.

---

# 2. Filosofía del modelo

El sistema utilizará un único archivo Excel como fuente de información.

Toda la información calculada (matrices, grafos, cronogramas, eventos, estados e indicadores) será generada automáticamente por el sistema y nunca será ingresada manualmente.

Se busca mantener un modelo de entrada simple, robusto y fácilmente exportable desde modelos BIM.

---

# 3. Estructura del archivo Excel

El archivo de entrada estará compuesto por las siguientes hojas:

1. Proyecto
2. Unidades
3. Pilotes
4. Equipos
5. AsignacionEquipos

No se permitirán hojas adicionales como parte del modelo oficial.

---

# 4. Hoja Proyecto

Contiene la configuración general del proyecto.

| Campo               | Tipo    | Obligatorio | Descripción                               |
| ------------------- | ------- | ----------- | ----------------------------------------- |
| Proyecto            | Texto   | Sí          | Nombre del proyecto                       |
| FechaInicio         | Fecha   | Sí          | Fecha de inicio de la simulación          |
| RadioCritico_m      | Decimal | Sí          | Distancia mínima entre excavaciones       |
| TiempoRestriccion_h | Decimal | Sí          | Tiempo mínimo entre excavaciones cercanas |

Observaciones:

* Los horarios de trabajo NO hacen parte del modelo.
* El sistema utiliza únicamente el rendimiento diario de los equipos.

---

# 5. Hoja Unidades

Representa cada unidad estructural del proyecto.

| Campo    | Tipo  | Obligatorio |
| -------- | ----- | ----------- |
| UnidadID | Texto | Sí          |
| Nombre   | Texto | Sí          |

Ejemplos:

* Torre 1
* Torre 2
* Podio
* Sótano
* Pantalla Norte

---

# 6. Hoja Pilotes

Es la hoja principal del proyecto.

Cada registro representa un pilote.

| Campo    | Tipo    | Obligatorio |
| -------- | ------- | ----------- |
| PiloteID | Texto   | Sí          |
| UnidadID | Texto   | Sí          |
| X        | Decimal | Sí          |
| Y        | Decimal | Sí          |

Observaciones:

Las coordenadas provienen del modelo BIM.

No se utilizarán por ahora:

* diámetro
* profundidad
* tipo de pilote

Estos atributos podrán incorporarse en versiones futuras.

---

# 7. Hoja Equipos

Cada registro representa una piloteadora.

| Campo                 | Tipo   | Obligatorio |
| --------------------- | ------ | ----------- |
| EquipoID              | Texto  | Sí          |
| Nombre                | Texto  | Sí          |
| RendimientoPilotesDia | Entero | Sí          |
| ModoInicio            | Texto  | Sí          |
| PiloteInicio          | Texto  | No          |
| ModoFin               | Texto  | Sí          |
| PiloteFin             | Texto  | No          |

Valores permitidos para ModoInicio y ModoFin:

* AUTO
* MANUAL

Cuando el modo sea AUTO el sistema optimizará automáticamente el punto correspondiente.

Cuando el modo sea MANUAL el sistema respetará el pilote indicado.

---

# 8. Hoja AsignacionEquipos

Define la relación muchos-a-muchos entre equipos y unidades estructurales.

| Campo     | Tipo   | Obligatorio |
| --------- | ------ | ----------- |
| EquipoID  | Texto  | Sí          |
| UnidadID  | Texto  | Sí          |
| Prioridad | Entero | Sí          |

La prioridad representa una preferencia inicial de asignación.

El optimizador podrá modificar dicha asignación si encuentra una solución mejor.

---

# 9. Relaciones

Proyecto

1 → N Unidades

Unidad

1 → N Pilotes

Equipo

N ↔ N Unidad

---

# 10. Validaciones

El cargador deberá verificar:

* IDs únicos.
* Coordenadas válidas.
* Rendimiento mayor que cero.
* Unidades existentes.
* Pilotes pertenecientes a una unidad válida.
* Equipos asignados únicamente a unidades existentes.
* Pilotes manuales de inicio y fin existentes.

---

# 11. Información calculada por el sistema

Nunca hará parte del archivo de entrada:

* matriz de distancias;
* grafo espacial;
* vecinos;
* estados de pilotes;
* eventos;
* cronograma;
* indicadores;
* recorridos;
* conflictos.

Toda esta información será generada automáticamente.

---

# 12. Principio del modelo de datos

El archivo Excel describe únicamente el proyecto.

Toda la inteligencia pertenece al sistema.

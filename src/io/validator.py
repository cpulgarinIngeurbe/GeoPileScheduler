"""Validador de datos para GeoPile Scheduler.

Responsabilidad: Verificar que los datos de entrada cumplan
con las restricciones definidas en MODELO_DATOS.md
"""

from datetime import datetime
from typing import Dict, List, Tuple, Any

from src.core.models import Proyecto, Pilote, UnidadEstructural, Equipo, AsignacionEquipo
from src.core.enums import ModoInicio, ModoFin


def validate_project_data(
    proyecto_data: Dict[str, Any],
    unidades_data: List[Dict[str, Any]],
    pilotes_data: List[Dict[str, Any]],
    equipos_data: List[Dict[str, Any]],
    asignaciones_data: List[Dict[str, Any]],
) -> Tuple[bool, List[str]]:
    """Valida todos los datos de entrada antes de construir el modelo.

    Args:
        proyecto_data: Diccionario con datos de proyecto.
        unidades_data: Lista de diccionarios con datos de unidades.
        pilotes_data: Lista de diccionarios con datos de pilotes.
        equipos_data: Lista de diccionarios con datos de equipos.
        asignaciones_data: Lista de diccionarios con datos de asignaciones.

    Returns:
        Tupla (is_valid: bool, errors: List[str]).
        Si is_valid es False, errors contiene lista descriptiva de errores.
    """
    errors: List[str] = []

    # Validar datos de proyecto
    errors.extend(_validar_proyecto(proyecto_data))

    # Validar datos de unidades
    errors.extend(_validar_unidades(unidades_data))

    # Validar datos de pilotes
    errors.extend(_validar_pilotes(pilotes_data))

    # Validar datos de equipos
    errors.extend(_validar_equipos(equipos_data))

    # Validar asignaciones
    errors.extend(_validar_asignaciones(asignaciones_data))

    # Validar referencias cruzadas
    errors.extend(
        _validar_referencias_cruzadas(
            proyecto_data, unidades_data, pilotes_data, equipos_data, asignaciones_data
        )
    )

    return (len(errors) == 0, errors)


def _validar_proyecto(proyecto_data: Dict[str, Any]) -> List[str]:
    """Valida datos de la hoja Proyecto."""
    errors: List[str] = []

    if "Proyecto" not in proyecto_data or not proyecto_data["Proyecto"]:
        errors.append("Proyecto: Campo 'Proyecto' es obligatorio y no puede estar vacío")

    if "FechaInicio" not in proyecto_data:
        errors.append("Proyecto: Campo 'FechaInicio' es obligatorio")
    elif not isinstance(proyecto_data["FechaInicio"], datetime):
        errors.append(
            f"Proyecto: 'FechaInicio' debe ser fecha, recibido {type(proyecto_data['FechaInicio'])}"
        )

    if "RadioCritico_m" not in proyecto_data:
        errors.append("Proyecto: Campo 'RadioCritico_m' es obligatorio")
    else:
        try:
            radio = float(proyecto_data["RadioCritico_m"])
            if radio <= 0:
                errors.append(f"Proyecto: 'RadioCritico_m' debe ser > 0, recibido {radio}")
        except (ValueError, TypeError):
            errors.append(
                f"Proyecto: 'RadioCritico_m' debe ser número, recibido {proyecto_data['RadioCritico_m']}"
            )

    if "TiempoRestriccion_h" not in proyecto_data:
        errors.append("Proyecto: Campo 'TiempoRestriccion_h' es obligatorio")
    else:
        try:
            tiempo = float(proyecto_data["TiempoRestriccion_h"])
            if tiempo < 0:
                errors.append(
                    f"Proyecto: 'TiempoRestriccion_h' debe ser >= 0, recibido {tiempo}"
                )
        except (ValueError, TypeError):
            errors.append(
                f"Proyecto: 'TiempoRestriccion_h' debe ser número, recibido {proyecto_data['TiempoRestriccion_h']}"
            )

    return errors


def _validar_unidades(unidades_data: List[Dict[str, Any]]) -> List[str]:
    """Valida datos de la hoja Unidades."""
    errors: List[str] = []

    if not unidades_data:
        errors.append("Unidades: No hay unidades definidas (mínimo 1 requerido)")
        return errors

    unidad_ids: set = set()

    for idx, unidad in enumerate(unidades_data):
        row = idx + 2  # Excel empieza en row 2

        # Validar UnidadID
        if "UnidadID" not in unidad or not unidad["UnidadID"]:
            errors.append(f"Unidades(fila {row}): 'UnidadID' es obligatorio")
            continue

        unidad_id = str(unidad["UnidadID"]).strip()

        if unidad_id in unidad_ids:
            errors.append(f"Unidades: 'UnidadID' duplicado '{unidad_id}' (fila {row})")
        unidad_ids.add(unidad_id)

        # Validar Nombre
        if "Nombre" not in unidad or not unidad["Nombre"]:
            errors.append(f"Unidades(fila {row}): 'Nombre' es obligatorio para {unidad_id}")

    return errors


def _validar_pilotes(pilotes_data: List[Dict[str, Any]]) -> List[str]:
    """Valida datos de la hoja Pilotes."""
    errors: List[str] = []

    if not pilotes_data:
        errors.append("Pilotes: No hay pilotes definidos (mínimo 1 requerido)")
        return errors

    pilote_ids: set = set()

    for idx, pilote in enumerate(pilotes_data):
        row = idx + 2  # Excel empieza en row 2

        # Validar PiloteID
        if "PiloteID" not in pilote or not pilote["PiloteID"]:
            errors.append(f"Pilotes(fila {row}): 'PiloteID' es obligatorio")
            continue

        pilote_id = str(pilote["PiloteID"]).strip()

        if pilote_id in pilote_ids:
            errors.append(f"Pilotes: 'PiloteID' duplicado '{pilote_id}' (fila {row})")
        pilote_ids.add(pilote_id)

        # Validar UnidadID
        if "UnidadID" not in pilote or not pilote["UnidadID"]:
            errors.append(f"Pilotes(fila {row}): 'UnidadID' es obligatorio para {pilote_id}")

        # Validar X
        if "X" not in pilote:
            errors.append(f"Pilotes(fila {row}): 'X' es obligatorio para {pilote_id}")
        else:
            try:
                x = float(pilote["X"])
                if x < 0:
                    errors.append(f"Pilotes(fila {row}): 'X' no puede ser negativo ({x})")
            except (ValueError, TypeError):
                errors.append(
                    f"Pilotes(fila {row}): 'X' debe ser número, recibido '{pilote['X']}'"
                )

        # Validar Y
        if "Y" not in pilote:
            errors.append(f"Pilotes(fila {row}): 'Y' es obligatorio para {pilote_id}")
        else:
            try:
                y = float(pilote["Y"])
                if y < 0:
                    errors.append(f"Pilotes(fila {row}): 'Y' no puede ser negativo ({y})")
            except (ValueError, TypeError):
                errors.append(
                    f"Pilotes(fila {row}): 'Y' debe ser número, recibido '{pilote['Y']}'"
                )

    return errors


def _validar_equipos(equipos_data: List[Dict[str, Any]]) -> List[str]:
    """Valida datos de la hoja Equipos."""
    errors: List[str] = []

    if not equipos_data:
        errors.append("Equipos: No hay equipos definidos (mínimo 1 requerido)")
        return errors

    equipo_ids: set = set()

    for idx, equipo in enumerate(equipos_data):
        row = idx + 2  # Excel empieza en row 2

        # Validar EquipoID
        if "EquipoID" not in equipo or not equipo["EquipoID"]:
            errors.append(f"Equipos(fila {row}): 'EquipoID' es obligatorio")
            continue

        equipo_id = str(equipo["EquipoID"]).strip()

        if equipo_id in equipo_ids:
            errors.append(f"Equipos: 'EquipoID' duplicado '{equipo_id}' (fila {row})")
        equipo_ids.add(equipo_id)

        # Validar Nombre
        if "Nombre" not in equipo or not equipo["Nombre"]:
            errors.append(f"Equipos(fila {row}): 'Nombre' es obligatorio para {equipo_id}")

        # Validar RendimientoPilotesDia
        if "RendimientoPilotesDia" not in equipo:
            errors.append(
                f"Equipos(fila {row}): 'RendimientoPilotesDia' es obligatorio para {equipo_id}"
            )
        else:
            try:
                rend = int(equipo["RendimientoPilotesDia"])
                if rend <= 0:
                    errors.append(
                        f"Equipos(fila {row}): 'RendimientoPilotesDia' debe ser > 0, recibido {rend}"
                    )
            except (ValueError, TypeError):
                errors.append(
                    f"Equipos(fila {row}): 'RendimientoPilotesDia' debe ser entero, recibido '{equipo['RendimientoPilotesDia']}'"
                )

        # Validar ModoInicio
        if "ModoInicio" not in equipo or not equipo["ModoInicio"]:
            errors.append(f"Equipos(fila {row}): 'ModoInicio' es obligatorio para {equipo_id}")
        elif str(equipo["ModoInicio"]).upper() not in ["AUTO", "MANUAL"]:
            errors.append(
                f"Equipos(fila {row}): 'ModoInicio' debe ser AUTO o MANUAL, recibido '{equipo['ModoInicio']}'"
            )
        elif str(equipo["ModoInicio"]).upper() == "MANUAL":
            if "PiloteInicio" not in equipo or not equipo["PiloteInicio"]:
                errors.append(
                    f"Equipos(fila {row}): 'PiloteInicio' es obligatorio cuando ModoInicio=MANUAL para {equipo_id}"
                )

        # Validar ModoFin
        if "ModoFin" not in equipo or not equipo["ModoFin"]:
            errors.append(f"Equipos(fila {row}): 'ModoFin' es obligatorio para {equipo_id}")
        elif str(equipo["ModoFin"]).upper() not in ["AUTO", "MANUAL"]:
            errors.append(
                f"Equipos(fila {row}): 'ModoFin' debe ser AUTO o MANUAL, recibido '{equipo['ModoFin']}'"
            )
        elif str(equipo["ModoFin"]).upper() == "MANUAL":
            if "PiloteFin" not in equipo or not equipo["PiloteFin"]:
                errors.append(
                    f"Equipos(fila {row}): 'PiloteFin' es obligatorio cuando ModoFin=MANUAL para {equipo_id}"
                )

    return errors


def _validar_asignaciones(asignaciones_data: List[Dict[str, Any]]) -> List[str]:
    """Valida datos de la hoja AsignacionEquipos."""
    errors: List[str] = []

    if not asignaciones_data:
        errors.append("AsignacionEquipos: No hay asignaciones definidas (mínimo 1 requerida)")
        return errors

    for idx, asig in enumerate(asignaciones_data):
        row = idx + 2  # Excel empieza en row 2

        # Validar EquipoID
        if "EquipoID" not in asig or not asig["EquipoID"]:
            errors.append(f"AsignacionEquipos(fila {row}): 'EquipoID' es obligatorio")

        # Validar UnidadID
        if "UnidadID" not in asig or not asig["UnidadID"]:
            errors.append(f"AsignacionEquipos(fila {row}): 'UnidadID' es obligatorio")

        # Validar Prioridad
        if "Prioridad" not in asig:
            errors.append(f"AsignacionEquipos(fila {row}): 'Prioridad' es obligatorio")
        else:
            try:
                int(asig["Prioridad"])
            except (ValueError, TypeError):
                errors.append(
                    f"AsignacionEquipos(fila {row}): 'Prioridad' debe ser entero, recibido '{asig['Prioridad']}'"
                )

    return errors


def _validar_referencias_cruzadas(
    proyecto_data: Dict[str, Any],
    unidades_data: List[Dict[str, Any]],
    pilotes_data: List[Dict[str, Any]],
    equipos_data: List[Dict[str, Any]],
    asignaciones_data: List[Dict[str, Any]],
) -> List[str]:
    """Valida que las referencias entre tablas sean consistentes."""
    errors: List[str] = []

    # Construir conjuntos de IDs válidos
    unidad_ids = {str(u["UnidadID"]).strip() for u in unidades_data}
    pilote_ids = {str(p["PiloteID"]).strip() for p in pilotes_data}
    equipo_ids = {str(e["EquipoID"]).strip() for e in equipos_data}

    # Validar pilotes → unidades
    for idx, pilote in enumerate(pilotes_data):
        row = idx + 2
        unidad_id = str(pilote.get("UnidadID", "")).strip()
        if unidad_id and unidad_id not in unidad_ids:
            errors.append(
                f"Pilotes(fila {row}): UnidadID '{unidad_id}' no existe en Unidades"
            )

    # Validar equipos → pilotes manuales
    for idx, equipo in enumerate(equipos_data):
        row = idx + 2
        equipo_id = str(equipo.get("EquipoID", "")).strip()

        if str(equipo.get("ModoInicio", "")).upper() == "MANUAL":
            pilote_inicio = str(equipo.get("PiloteInicio", "")).strip()
            if pilote_inicio and pilote_inicio not in pilote_ids:
                errors.append(
                    f"Equipos(fila {row}): PiloteInicio '{pilote_inicio}' no existe en Pilotes"
                )

        if str(equipo.get("ModoFin", "")).upper() == "MANUAL":
            pilote_fin = str(equipo.get("PiloteFin", "")).strip()
            if pilote_fin and pilote_fin not in pilote_ids:
                errors.append(
                    f"Equipos(fila {row}): PiloteFin '{pilote_fin}' no existe en Pilotes"
                )

    # Validar asignaciones → equipos y unidades
    for idx, asig in enumerate(asignaciones_data):
        row = idx + 2
        equipo_id = str(asig.get("EquipoID", "")).strip()
        unidad_id = str(asig.get("UnidadID", "")).strip()

        if equipo_id and equipo_id not in equipo_ids:
            errors.append(
                f"AsignacionEquipos(fila {row}): EquipoID '{equipo_id}' no existe en Equipos"
            )

        if unidad_id and unidad_id not in unidad_ids:
            errors.append(
                f"AsignacionEquipos(fila {row}): UnidadID '{unidad_id}' no existe en Unidades"
            )

    return errors

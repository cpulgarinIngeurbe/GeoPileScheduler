"""Calculador de pilotes disponibles.

Responsabilidad: Determinar qué pilotes pueden ejecutarse en cada momento.
"""

from datetime import datetime
from typing import List

from src.core.enums import EstadoPilote
from src.core.models import Proyecto
from src.constraints.pilote_state_manager import PiloteStateManager


def get_pilotes_disponibles(
    estado_manager: PiloteStateManager,
    proyecto: Proyecto,
    tiempo_actual: datetime,
) -> List[str]:
    """Calcula lista de pilotes disponibles para ejecutar.

    Un pilote es DISPONIBLE si:
    1. Su estado actual es PENDIENTE o DISPONIBLE
    2. No tiene bloqueos activos en este momento

    Algorithm:
    1. Liberar bloqueos expirados
    2. Iterar sobre todos los pilotes
    3. Para cada pilote:
       - SI estado == PENDIENTE o DISPONIBLE
       - Y no tiene bloqueos activos
       → es disponible

    Args:
        estado_manager: PiloteStateManager con estados actuales.
        proyecto: Objeto Proyecto.
        tiempo_actual: Tiempo actual de simulación.

    Returns:
        Lista ordenada de IDs de pilotes disponibles.
    """
    # Primero, liberar bloqueos expirados
    pilotes_liberados = estado_manager.liberar_bloqueos_expirados(tiempo_actual)

    # Para cada pilote liberado, cambiar estado a DISPONIBLE
    for pilote_id in pilotes_liberados:
        estado_actual = estado_manager.get_estado(pilote_id)
        if estado_actual == EstadoPilote.BLOQUEADO:
            estado_manager.set_estado(pilote_id, EstadoPilote.DISPONIBLE, tiempo_actual)

    # Calcular disponibles
    disponibles: List[str] = []

    for unidad in proyecto.unidades.values():
        for pilote_id in unidad.pilotes.keys():
            estado = estado_manager.get_estado(pilote_id)

            # Debe estar en PENDIENTE o DISPONIBLE
            if estado not in [EstadoPilote.PENDIENTE, EstadoPilote.DISPONIBLE]:
                continue

            # No debe tener bloqueos activos
            tiene_bloqueos = estado_manager.has_bloqueos_activos(pilote_id, tiempo_actual)
            if tiene_bloqueos:
                continue

            disponibles.append(pilote_id)

    # Retornar ordenado para consistencia
    return sorted(disponibles)


def get_pilotes_por_estado(
    estado_manager: PiloteStateManager,
    proyecto: Proyecto,
    estado: EstadoPilote,
) -> List[str]:
    """Obtiene todos los pilotes en un estado específico.

    Args:
        estado_manager: PiloteStateManager.
        proyecto: Objeto Proyecto.
        estado: EstadoPilote a buscar.

    Returns:
        Lista ordenada de IDs de pilotes en ese estado.
    """
    pilotes: List[str] = []

    for unidad in proyecto.unidades.values():
        for pilote_id in unidad.pilotes.keys():
            if estado_manager.get_estado(pilote_id) == estado:
                pilotes.append(pilote_id)

    return sorted(pilotes)


def hay_pilotes_ejecutables(
    estado_manager: PiloteStateManager,
    proyecto: Proyecto,
    tiempo_actual: datetime,
) -> bool:
    """Verifica si hay pilotes disponibles para ejecutar.

    Args:
        estado_manager: PiloteStateManager.
        proyecto: Objeto Proyecto.
        tiempo_actual: Tiempo actual de simulación.

    Returns:
        True si hay al menos un pilote disponible.
    """
    disponibles = get_pilotes_disponibles(estado_manager, proyecto, tiempo_actual)
    return len(disponibles) > 0


def progreso_ejecucion(
    estado_manager: PiloteStateManager,
    proyecto: Proyecto,
) -> tuple:
    """Calcula progreso de ejecución del proyecto.

    Args:
        estado_manager: PiloteStateManager.
        proyecto: Objeto Proyecto.

    Returns:
        Tupla (ejecutados, total, porcentaje).
    """
    total = proyecto.num_pilotes
    ejecutados = len(get_pilotes_por_estado(estado_manager, proyecto, EstadoPilote.EJECUTADO))
    porcentaje = (ejecutados / total * 100) if total > 0 else 0

    return (ejecutados, total, porcentaje)

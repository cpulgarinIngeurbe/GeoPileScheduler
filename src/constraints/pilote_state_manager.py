"""Gestor de estado dinámico de pilotes.

Responsabilidad: Mantener y actualizar estado de cada pilote durante la simulación.
"""

from datetime import datetime
from typing import Dict, List

from src.core.models import Proyecto
from src.core.enums import EstadoPilote
from src.constraints.event_model import BloqueoGeotecnico


class PiloteStateManager:
    """Gestor central del estado de todos los pilotes.

    Mantiene:
    - Estado actual de cada pilote (PENDIENTE, DISPONIBLE, etc.)
    - Lista de bloqueos activos por pilote
    - Historial de transiciones

    Responsabilidades:
    - Inicializar estados al inicio
    - Cambiar estados validando transiciones
    - Agregar/remover bloqueos
    - Liberar bloqueos expirados
    """

    def __init__(self, proyecto: Proyecto):
        """Inicializa el gestor de estados.

        Args:
            proyecto: Objeto Proyecto.
        """
        self.proyecto = proyecto
        self.estados: Dict[str, EstadoPilote] = {}  # pilote_id → estado
        self.bloqueos: Dict[str, List[BloqueoGeotecnico]] = {}  # pilote_id → bloqueos
        self.historico_cambios: List[tuple] = []  # (pilote_id, estado_anterior, estado_nuevo, tiempo)

    def inicializar(self) -> None:
        """Inicializa todos los pilotes como PENDIENTE.

        Crea entrada para cada pilote en los diccionarios de estado y bloqueos.
        """
        for unidad in self.proyecto.unidades.values():
            for pilote_id in unidad.pilotes.keys():
                self.estados[pilote_id] = EstadoPilote.PENDIENTE
                self.bloqueos[pilote_id] = []

    # ========== Métodos de consulta de estado ==========

    def get_estado(self, pilote_id: str) -> EstadoPilote:
        """Obtiene el estado actual de un pilote.

        Args:
            pilote_id: ID del pilote.

        Returns:
            EstadoPilote actual.

        Raises:
            KeyError: Si pilote no existe.
        """
        if pilote_id not in self.estados:
            raise KeyError(f"Pilote '{pilote_id}' no existe")
        return self.estados[pilote_id]

    def has_bloqueos_activos(self, pilote_id: str, tiempo_actual: datetime) -> bool:
        """Verifica si un pilote tiene bloqueos activos.

        Args:
            pilote_id: ID del pilote.
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            True si hay bloqueos activos, False en caso contrario.
        """
        if pilote_id not in self.bloqueos:
            return False

        for bloqueo in self.bloqueos[pilote_id]:
            if bloqueo.esta_activo(tiempo_actual):
                return True

        return False

    def get_bloqueos_activos(self, pilote_id: str, tiempo_actual: datetime) -> List[BloqueoGeotecnico]:
        """Obtiene lista de bloqueos activos.

        Args:
            pilote_id: ID del pilote.
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Lista de BloqueoGeotecnico que siguen activos.
        """
        if pilote_id not in self.bloqueos:
            return []

        return [b for b in self.bloqueos[pilote_id] if b.esta_activo(tiempo_actual)]

    # ========== Métodos de cambio de estado ==========

    def set_estado(self, pilote_id: str, nuevo_estado: EstadoPilote, tiempo: datetime | None = None) -> None:
        """Cambia el estado de un pilote.

        Valida que la transición sea legal antes de cambiar.

        Args:
            pilote_id: ID del pilote.
            nuevo_estado: Nuevo EstadoPilote.
            tiempo: Tiempo del cambio (para historial).

        Raises:
            KeyError: Si pilote no existe.
            ValueError: Si la transición es inválida.
        """
        if pilote_id not in self.estados:
            raise KeyError(f"Pilote '{pilote_id}' no existe")

        estado_anterior = self.estados[pilote_id]

        # Validar transición
        if not self._es_transicion_valida(estado_anterior, nuevo_estado):
            raise ValueError(
                f"Transición inválida: {estado_anterior.value} → {nuevo_estado.value} para {pilote_id}"
            )

        # Cambiar estado
        self.estados[pilote_id] = nuevo_estado

        # Registrar en historial
        self.historico_cambios.append((pilote_id, estado_anterior, nuevo_estado, tiempo))

    def _es_transicion_valida(self, estado_anterior: EstadoPilote, nuevo_estado: EstadoPilote) -> bool:
        """Valida que una transición de estado sea legal.

        Transiciones permitidas:
        - PENDIENTE → DISPONIBLE (cuando se libera bloqueo inicial)
        - PENDIENTE → BLOQUEADO (cuando hay bloqueos inmediatos)
        - DISPONIBLE → ASIGNADO (cuando se asigna a equipo)
        - DISPONIBLE → BLOQUEADO (cuando surge nuevo bloqueo)
        - ASIGNADO → EJECUTADO (cuando termina equipo)
        - BLOQUEADO → DISPONIBLE (cuando se libera bloqueo)
        - EJECUTADO → no cambia (estado final)

        Args:
            estado_anterior: Estado actual.
            nuevo_estado: Estado destino.

        Returns:
            True si la transición es válida.
        """
        # EJECUTADO es estado final
        if estado_anterior == EstadoPilote.EJECUTADO:
            return False

        # Transiciones válidas por estado
        transiciones_validas = {
            EstadoPilote.PENDIENTE: [EstadoPilote.DISPONIBLE, EstadoPilote.BLOQUEADO],
            EstadoPilote.DISPONIBLE: [EstadoPilote.ASIGNADO, EstadoPilote.BLOQUEADO],
            EstadoPilote.ASIGNADO: [EstadoPilote.EJECUTADO, EstadoPilote.DISPONIBLE],  # Cancelación
            EstadoPilote.BLOQUEADO: [EstadoPilote.DISPONIBLE, EstadoPilote.ASIGNADO],
            EstadoPilote.EJECUTADO: [],
        }

        return nuevo_estado in transiciones_validas.get(estado_anterior, [])

    # ========== Métodos de bloqueos ==========

    def agregar_bloqueo(self, bloqueo: BloqueoGeotecnico) -> None:
        """Registra un nuevo bloqueo geotécnico.

        Args:
            bloqueo: BloqueoGeotecnico a registrar.

        Raises:
            KeyError: Si pilote no existe.
        """
        if bloqueo.pilote_id not in self.bloqueos:
            raise KeyError(f"Pilote '{bloqueo.pilote_id}' no existe")

        self.bloqueos[bloqueo.pilote_id].append(bloqueo)

    def liberar_bloqueos_expirados(self, tiempo_actual: datetime) -> List[str]:
        """Libera todos los bloqueos que han expirado.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Lista de IDs de pilotes que fueron liberados.
        """
        pilotes_liberados: List[str] = []

        for pilote_id in self.bloqueos:
            # Obtener bloqueos activos antes de limpiar
            bloqueos_activos_antes = len(self.get_bloqueos_activos(pilote_id, tiempo_actual))

            # Limpiar bloqueos expirados
            self.bloqueos[pilote_id] = [
                b for b in self.bloqueos[pilote_id] if b.esta_activo(tiempo_actual)
            ]

            # Obtener bloqueos activos después
            bloqueos_activos_despues = len(self.get_bloqueos_activos(pilote_id, tiempo_actual))

            # Si pasó de tener bloqueos a no tener, fue liberado
            if bloqueos_activos_antes > 0 and bloqueos_activos_despues == 0:
                pilotes_liberados.append(pilote_id)

        return pilotes_liberados

    # ========== Métodos de estadísticas ==========

    def get_estadisticas(self, tiempo_actual: datetime) -> dict:
        """Obtiene estadísticas del estado actual.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Diccionario con conteos por estado y bloqueos activos.
        """
        conteos = {estado: 0 for estado in EstadoPilote}
        total_bloqueos_activos = 0

        for pilote_id in self.estados:
            estado = self.estados[pilote_id]
            conteos[estado] += 1

            # Contar bloqueos activos
            bloqueos_activos = self.get_bloqueos_activos(pilote_id, tiempo_actual)
            total_bloqueos_activos += len(bloqueos_activos)

        return {
            "pendientes": conteos[EstadoPilote.PENDIENTE],
            "disponibles": conteos[EstadoPilote.DISPONIBLE],
            "asignados": conteos[EstadoPilote.ASIGNADO],
            "ejecutados": conteos[EstadoPilote.EJECUTADO],
            "bloqueados": conteos[EstadoPilote.BLOQUEADO],
            "total_bloqueos_activos": total_bloqueos_activos,
        }

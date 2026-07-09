"""Cola de eventos ordenada por tiempo."""

import heapq
from datetime import datetime
from typing import Optional

from .event_model import EventoSimulacion


class EventQueue:
    """Cola de prioridad para eventos ordenados por timestamp."""

    def __init__(self) -> None:
        """Inicializar cola."""
        self._queue: list[tuple[datetime, int, EventoSimulacion]] = []
        self._counter = 0

    def push(self, evento: EventoSimulacion) -> None:
        """Agregar evento a la cola.

        Args:
            evento: EventoSimulacion a agregar

        Raises:
            TypeError: si evento no es EventoSimulacion
        """
        if not isinstance(evento, EventoSimulacion):
            raise TypeError("evento debe ser EventoSimulacion")

        # Usar contador para garantizar orden FIFO en eventos simultáneos
        heapq.heappush(self._queue, (evento.timestamp, self._counter, evento))
        self._counter += 1

    def pop(self) -> Optional[EventoSimulacion]:
        """Obtener y remover próximo evento.

        Returns:
            EventoSimulacion o None si cola está vacía
        """
        if not self._queue:
            return None
        _, _, evento = heapq.heappop(self._queue)
        return evento

    def peek(self) -> Optional[EventoSimulacion]:
        """Ver próximo evento sin remover.

        Returns:
            EventoSimulacion o None si cola está vacía
        """
        if not self._queue:
            return None
        _, _, evento = self._queue[0]
        return evento

    def empty(self) -> bool:
        """Verificar si cola está vacía.

        Returns:
            True si está vacía
        """
        return len(self._queue) == 0

    def size(self) -> int:
        """Obtener tamaño de cola.

        Returns:
            Número de eventos en cola
        """
        return len(self._queue)

    def clear(self) -> None:
        """Limpiar cola."""
        self._queue.clear()
        self._counter = 0

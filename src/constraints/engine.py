"""Motor de Restricciones - Orquestador de lógica de restricciones.

Responsabilidad: Encapsular toda la funcionalidad de restricciones en una
interfaz clara e integrada.
"""

from datetime import datetime
from typing import List, Dict

from src.core.models import Proyecto
from src.core.enums import EstadoPilote
from src.geometry.engine import MotorGeometrico
from src.constraints.pilote_state_manager import PiloteStateManager
from src.constraints.event_model import BloqueoGeotecnico
from src.constraints.restriction_r1 import aplicar_restriccion_r1, desbloquear_automaticamente
from src.constraints.available_calculator import (
    get_pilotes_disponibles,
    get_pilotes_por_estado,
    hay_pilotes_ejecutables,
    progreso_ejecucion,
)


class MotorRestricciones:
    """Orquestador del motor de restricciones geotécnicas.

    Encapsula:
    - Gestión de estados de pilotes
    - Aplicación de restricción R1 (geotécnica)
    - Cálculo de pilotes disponibles
    - Estadísticas de restricciones

    Attributes:
        proyecto: Objeto Proyecto.
        motor_geometrico: MotorGeometrico con geometría calculada.
        estado_manager: PiloteStateManager interno.
        historico_restricciones: Lista de eventos de restricción.
    """

    def __init__(self, proyecto: Proyecto, motor_geometrico: MotorGeometrico):
        """Inicializa motor de restricciones.

        Args:
            proyecto: Objeto Proyecto.
            motor_geometrico: MotorGeometrico con geometría calculada.

        Raises:
            RuntimeError: Si motor_geometrico no está calculado.
        """
        if motor_geometrico.distance_matrix is None:
            raise RuntimeError("MotorGeometrico debe estar calculado antes de crear MotorRestricciones")

        self.proyecto = proyecto
        self.motor_geometrico = motor_geometrico
        self.estado_manager = PiloteStateManager(proyecto)
        self.historico_restricciones: List[dict] = []

    def inicializar(self) -> None:
        """Inicializa todas las restricciones.

        Todos los pilotes comienzan como PENDIENTE, sin bloqueos.
        """
        self.estado_manager.inicializar()

    def ejecutar_pilote(self, pilote_id: str, tiempo_ejecucion: datetime) -> dict:
        """Marca un pilote como ejecutado y aplica restricciones.

        Pasos:
        1. Validar que pilote sea ejecutable
        2. Cambiar su estado a EJECUTADO
        3. Aplicar restricción R1 (bloquear vecinos)
        4. Registrar evento

        Args:
            pilote_id: ID del pilote a ejecutar.
            tiempo_ejecucion: Datetime de ejecución.

        Returns:
            Dict con información de la ejecución y bloqueos aplicados.

        Raises:
            ValueError: Si pilote no puede ejecutarse.
        """
        # Validar que sea ejecutable
        if pilote_id not in self.estado_manager.estados:
            raise ValueError(f"Pilote '{pilote_id}' no existe")

        estado = self.estado_manager.get_estado(pilote_id)
        if estado not in [EstadoPilote.PENDIENTE, EstadoPilote.DISPONIBLE]:
            raise ValueError(
                f"Pilote '{pilote_id}' no puede ejecutarse en estado {estado.value}"
            )

        # Cambiar a EJECUTADO
        self.estado_manager.set_estado(pilote_id, EstadoPilote.EJECUTADO, tiempo_ejecucion)

        # Aplicar restricción R1
        pilotes_bloqueados = aplicar_restriccion_r1(
            pilote_id,
            self.motor_geometrico,
            self.estado_manager,
            self.proyecto,
            tiempo_ejecucion,
        )

        # Registrar evento
        evento = {
            "tipo": "pilote_ejecutado",
            "pilote_id": pilote_id,
            "tiempo": tiempo_ejecucion,
            "pilotes_bloqueados": pilotes_bloqueados,
            "num_bloqueos": len(pilotes_bloqueados),
        }
        self.historico_restricciones.append(evento)

        return evento

    def actualizar_tiempo(self, tiempo_actual: datetime) -> List[str]:
        """Actualiza restricciones para un nuevo momento de tiempo.

        Desbloquea pilotes cuyos bloqueos han expirado.

        Args:
            tiempo_actual: Nuevo tiempo actual de simulación.

        Returns:
            Lista de IDs de pilotes desbloqueados.
        """
        # Liberar bloqueos expirados
        pilotes_liberados = self.estado_manager.liberar_bloqueos_expirados(tiempo_actual)

        # Cambiar estado a DISPONIBLE
        for pilote_id in pilotes_liberados:
            estado = self.estado_manager.get_estado(pilote_id)
            if estado == EstadoPilote.BLOQUEADO:
                self.estado_manager.set_estado(pilote_id, EstadoPilote.DISPONIBLE, tiempo_actual)

        # Registrar evento si hubo liberaciones
        if pilotes_liberados:
            evento = {
                "tipo": "pilotes_desbloqueados",
                "tiempo": tiempo_actual,
                "pilotes": pilotes_liberados,
                "num_liberados": len(pilotes_liberados),
            }
            self.historico_restricciones.append(evento)

        return pilotes_liberados

    # ========== Métodos de consulta ==========

    def get_pilotes_disponibles(self, tiempo_actual: datetime) -> List[str]:
        """Obtiene pilotes que pueden ejecutarse ahora.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Lista ordenada de IDs de pilotes disponibles.
        """
        return get_pilotes_disponibles(self.estado_manager, self.proyecto, tiempo_actual)

    def get_estado_pilote(self, pilote_id: str) -> EstadoPilote:
        """Obtiene estado de un pilote.

        Args:
            pilote_id: ID del pilote.

        Returns:
            EstadoPilote actual.

        Raises:
            KeyError: Si pilote no existe.
        """
        return self.estado_manager.get_estado(pilote_id)

    def get_bloqueos_pilote(
        self, pilote_id: str, tiempo_actual: datetime
    ) -> List[BloqueoGeotecnico]:
        """Obtiene bloqueos activos de un pilote.

        Args:
            pilote_id: ID del pilote.
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Lista de BloqueoGeotecnico activos.
        """
        return self.estado_manager.get_bloqueos_activos(pilote_id, tiempo_actual)

    def hay_pilotes_ejecutables(self, tiempo_actual: datetime) -> bool:
        """Verifica si hay pilotes disponibles para ejecutar.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            True si hay al menos un pilote disponible.
        """
        return hay_pilotes_ejecutables(self.estado_manager, self.proyecto, tiempo_actual)

    # ========== Métodos de estadísticas ==========

    def get_estadisticas_restricciones(self, tiempo_actual: datetime) -> dict:
        """Obtiene estadísticas completas de restricciones.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            Diccionario con estadísticas detalladas.
        """
        stats = self.estado_manager.get_estadisticas(tiempo_actual)

        # Agregar información adicional
        disponibles = self.get_pilotes_disponibles(tiempo_actual)
        ejecutados, total, porcentaje = progreso_ejecucion(self.estado_manager, self.proyecto)

        stats.update({
            "num_disponibles": len(disponibles),
            "ejecutados": ejecutados,
            "total": total,
            "porcentaje_completado": porcentaje,
            "hay_ejecutables": self.hay_pilotes_ejecutables(tiempo_actual),
        })

        return stats

    def get_informe_restricciones(self, tiempo_actual: datetime) -> str:
        """Genera informe legible de restricciones.

        Args:
            tiempo_actual: Tiempo actual de simulación.

        Returns:
            String con informe formateado.
        """
        stats = self.get_estadisticas_restricciones(tiempo_actual)

        informe = f"""
Estado de Restricciones - {tiempo_actual.strftime("%Y-%m-%d %H:%M:%S")}
{'=' * 60}
Pilotes por estado:
  • Pendientes:    {stats['pendientes']:3d}
  • Disponibles:   {stats['num_disponibles']:3d}
  • Asignados:     {stats['asignados']:3d}
  • Ejecutados:    {stats['ejecutados']:3d}
  • Bloqueados:    {stats['bloqueados']:3d}

Progreso: {stats['ejecutados']}/{stats['total']} ({stats['porcentaje_completado']:.1f}%)

Restricciones activas:
  • Bloqueos geotécnicos activos: {stats['total_bloqueos_activos']}
  • ¿Hay pilotes ejecutables?: {'Sí' if stats['hay_ejecutables'] else 'No'}
{'=' * 60}
"""
        return informe

    def get_pilotes_por_estado(self, estado: EstadoPilote) -> List[str]:
        """Obtiene todos los pilotes en un estado específico.

        Args:
            estado: EstadoPilote a buscar.

        Returns:
            Lista de IDs de pilotes en ese estado.
        """
        return get_pilotes_por_estado(self.estado_manager, self.proyecto, estado)

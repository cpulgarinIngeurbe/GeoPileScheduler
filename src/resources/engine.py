"""Motor de Recursos - Orquestador de gestión de equipos.

Responsabilidad: Encapsular toda la funcionalidad de recursos en interfaz integrada.
"""

from datetime import datetime
from typing import List

from src.core.models import Proyecto
from src.geometry.engine import MotorGeometrico
from src.resources.equipo_manager import EquipoManager
from src.resources.equipo_state import EstadoEquipo


class MotorRecursos:
    """Orquestador del motor de recursos (equipos de pilotaje).

    Encapsula gestión de equipos, asignación de trabajo, y cálculo de métricas.
    """

    def __init__(self, proyecto: Proyecto, motor_geometrico: MotorGeometrico):
        """Inicializa motor de recursos.

        Args:
            proyecto: Objeto Proyecto.
            motor_geometrico: MotorGeometrico con geometría calculada.

        Raises:
            RuntimeError: Si motor_geometrico no está calculado.
        """
        if motor_geometrico.distance_matrix is None:
            raise RuntimeError("MotorGeometrico debe estar calculado")

        self.proyecto = proyecto
        self.motor_geometrico = motor_geometrico
        self.equipo_manager = EquipoManager(proyecto, motor_geometrico)

    def inicializar(self) -> None:
        """Inicializa todos los equipos."""
        self.equipo_manager.inicializar()

    def asignar_trabajo(self, equipo_id: str, pilote_id: str, tiempo: datetime) -> dict:
        """Asigna trabajo a un equipo.

        Args:
            equipo_id: ID del equipo.
            pilote_id: ID del pilote a trabajar.
            tiempo: Datetime de asignación.

        Returns:
            Dict con información del evento de asignación.
        """
        evento = self.equipo_manager.asignar_pilote(equipo_id, pilote_id, tiempo)
        return {
            "tipo": "asignacion_trabajo",
            "equipo_id": equipo_id,
            "pilote_id": pilote_id,
            "tiempo_fin_estimado": evento.tiempo_estimado_finalizacion,
        }

    def finalizar_trabajo(self, equipo_id: str, tiempo: datetime) -> dict:
        """Equipo termina su trabajo actual.

        Args:
            equipo_id: ID del equipo.
            tiempo: Datetime de finalización.

        Returns:
            Dict con información del evento de finalización.
        """
        evento = self.equipo_manager.finalizar_pilote(equipo_id, tiempo)
        return {
            "tipo": "fin_trabajo",
            "equipo_id": equipo_id,
            "pilote_id": evento.pilote_id,
            "tiempo_ejecucion": evento.tiempo_ejecucion,
        }

    def cambiar_equipo_de_unidad(
        self, equipo_id: str, unidad_destino_id: str, tiempo: datetime
    ) -> dict:
        """Mueve equipo a otra unidad.

        Args:
            equipo_id: ID del equipo.
            unidad_destino_id: ID de unidad destino.
            tiempo: Datetime del cambio.

        Returns:
            Dict con información del evento de cambio.
        """
        evento = self.equipo_manager.cambiar_unidad(equipo_id, unidad_destino_id, tiempo)
        return {
            "tipo": "cambio_unidad",
            "equipo_id": equipo_id,
            "unidad_origen": evento.unidad_origen_id,
            "unidad_destino": evento.unidad_destino_id,
            "distancia_km": evento.distancia_desplazamiento,
            "tiempo_desplazamiento": evento.tiempo_desplazamiento,
        }

    # ========== Métodos de consulta ==========

    def get_equipos_disponibles(self, unidad_id: str | None = None) -> List[str]:
        """Equipos libres (opcionalmente en una unidad)."""
        return self.equipo_manager.get_equipos_disponibles(unidad_id)

    def get_estado_equipo(self, equipo_id: str) -> EstadoEquipo:
        """Estado actual de un equipo."""
        return self.equipo_manager.get_estado(equipo_id)

    def get_equipos_en_unidad(self, unidad_id: str) -> List[str]:
        """Todos los equipos presentes en una unidad."""
        return self.equipo_manager.get_equipos_en_unidad(unidad_id)

    def get_estadisticas_equipos(self) -> dict:
        """Métricas de rendimiento de todos los equipos."""
        return self.equipo_manager.get_estadisticas_equipos()

    def reset_diario(self) -> None:
        """Reinicia contadores para nueva jornada."""
        self.equipo_manager.reset_diario()

    def get_informe_equipos(self) -> str:
        """Genera informe legible del estado de equipos.

        Returns:
            String con informe formateado.
        """
        stats = self.get_estadisticas_equipos()

        informe = f"""
Estado de Equipos
{'=' * 60}
Resumen:
  • Total equipos: {stats['num_equipos']}
  • Equipos libres: {stats['equipos_libres']}
  • Equipos ocupados: {stats['equipos_ocupados']}

Productividad:
  • Pilotes ejecutados (total): {stats['total_pilotes_ejecutados']}
  • Distancia recorrida: {stats['distancia_total_recorrida']:.2f} km
  • Utilización promedio: {stats['utilization_promedio']:.1f}%

Equipos:
"""
        for equipo_id in sorted(self.equipo_manager.estados.keys()):
            estado = self.get_estado_equipo(equipo_id)
            estado_str = "LIBRE" if estado.esta_libre else f"OCUPADO ({estado.pilote_actual_id})"
            informe += f"  • {estado.nombre} ({equipo_id}): {estado_str}\n"
            informe += f"    - Unidad: {estado.unidad_actual_id}\n"
            informe += f"    - Hoy: {estado.pilotes_ejecutados_hoy} pilotes, {estado.horas_trabajo_hoy():.1f}h trabajo\n"

        informe += "=" * 60 + "\n"
        return informe

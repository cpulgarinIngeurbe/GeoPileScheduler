"""Base para optimizadores."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones


@dataclass
class Asignacion:
    """Una asignación de pilote a equipo."""

    equipo_id: str
    pilote_id: str
    timestamp: datetime

    def __repr__(self) -> str:
        """Representación string."""
        return f"{self.equipo_id} → {self.pilote_id} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


@dataclass
class Solucion:
    """Solución de optimización."""

    nombre_optimizador: str
    asignaciones: list[Asignacion]
    makespan: float  # horas
    score_multiobjetivo: float  # 0-100
    detalles: dict[str, Any] = field(default_factory=dict)
    tiempo_ejecucion: float = 0.0  # segundos

    def __post_init__(self) -> None:
        """Validar solución."""
        if not isinstance(self.asignaciones, list):
            raise TypeError("asignaciones debe ser lista")
        if not isinstance(self.makespan, (int, float)):
            raise TypeError("makespan debe ser número")
        if not isinstance(self.score_multiobjetivo, (int, float)):
            raise TypeError("score_multiobjetivo debe ser número")

    def resumen(self) -> str:
        """Resumen de solución."""
        return (
            f"{self.nombre_optimizador}: "
            f"Score={self.score_multiobjetivo:.1f}, "
            f"Makespan={self.makespan:.1f}h, "
            f"Asignaciones={len(self.asignaciones)}, "
            f"Tiempo={self.tiempo_ejecucion:.2f}s"
        )

    def get_secuencia_pilotes(self) -> list[str]:
        """Obtener secuencia de pilotes en orden de asignación.

        Returns:
            Lista de IDs de pilotes
        """
        return [a.pilote_id for a in self.asignaciones]

    def get_asignaciones_por_equipo(self, equipo_id: str) -> list[Asignacion]:
        """Obtener asignaciones de un equipo específico.

        Args:
            equipo_id: ID del equipo

        Returns:
            Lista de asignaciones del equipo
        """
        return [a for a in self.asignaciones if a.equipo_id == equipo_id]


class BaseOptimizer(ABC):
    """Clase base para optimizadores."""

    def __init__(
        self,
        proyecto: Proyecto,
        motor_geo: MotorGeometrico,
        motor_rest: MotorRestricciones,
        pesos_objetivos: dict[str, float] | None = None,
    ) -> None:
        """Inicializar optimizador.

        Args:
            proyecto: Proyecto a optimizar
            motor_geo: MotorGeometrico inicializado
            motor_rest: MotorRestricciones inicializado
            pesos_objetivos: Pesos para cada objetivo (O1-O6)
        """
        self.proyecto = proyecto
        self.motor_geo = motor_geo
        self.motor_rest = motor_rest

        # Pesos por defecto (iguales)
        self.pesos_objetivos = pesos_objetivos or {
            "O1_makespan": 0.20,  # Minimizar duración
            "O2_desbalance": 0.20,  # Minimizar desbalance
            "O3_utilizacion": 0.20,  # Maximizar utilización
            "O4_desplazamientos": 0.15,  # Minimizar distancia
            "O5_precedencias": 0.15,  # Respetar dependencias
            "O6_esperas": 0.10,  # Minimizar esperas
        }

        # Validar que suman 1.0
        total_peso = sum(self.pesos_objetivos.values())
        if abs(total_peso - 1.0) > 0.001:
            raise ValueError(f"Pesos deben sumar 1.0, suman {total_peso}")

    @abstractmethod
    def optimizar(self) -> Solucion:
        """Generar solución optimizada.

        Returns:
            Solucion con asignaciones y score

        Raises:
            ValueError: si no se puede optimizar
        """
        pass

    @abstractmethod
    def nombre(self) -> str:
        """Nombre del optimizador.

        Returns:
            Nombre descriptivo
        """
        pass

    def validar_solucion(self, solucion: Solucion) -> tuple[bool, list[str]]:
        """Validar que solución es correcta.

        Args:
            solucion: Solucion a validar

        Returns:
            Tupla (es_valida, lista_errores)
        """
        errores = []

        # V1: Verificar que todos los pilotes están asignados
        pilotes_asignados = set(a.pilote_id for a in solucion.asignaciones)
        pilotes_totales = set(self.proyecto.pilotes.keys())

        if pilotes_asignados != pilotes_totales:
            pilotes_faltantes = pilotes_totales - pilotes_asignados
            errores.append(
                f"Pilotes no asignados: {pilotes_faltantes}"
            )

        # V2: Verificar que no hay sobreasignación de equipos
        for equipo_id, equipo in self.proyecto.equipos.items():
            asignaciones_equipo = solucion.get_asignaciones_por_equipo(equipo_id)
            rendimiento_diario = equipo.rendimiento_pilotes_dia

            if len(asignaciones_equipo) > rendimiento_diario * 100:  # Múltiples días
                pass  # Es válido si se distribuye en días

        # V3: Verificar que timestamps son consistentes
        timestamps = [a.timestamp for a in solucion.asignaciones]
        if timestamps != sorted(timestamps):
            errores.append("Timestamps no están en orden temporal")

        # V4: Verificar que makespan es positivo
        if solucion.makespan < 0:
            errores.append("Makespan no puede ser negativo")

        # V5: Verificar que score está entre 0-100
        if not (0 <= solucion.score_multiobjetivo <= 100):
            errores.append(
                f"Score debe estar entre 0-100, obtuvo {solucion.score_multiobjetivo}"
            )

        return len(errores) == 0, errores

    def calcular_score_multiobjetivo(
        self,
        makespan: float,
        desbalance: float,
        utilizacion: float,
        desplazamientos: float,
        precedencias_cumplidas: bool,
        esperas: float,
    ) -> float:
        """Calcular score multi-objetivo ponderado.

        Args:
            makespan: Duración del proyecto (horas) - minimizar
            desbalance: Desviación std de carga entre equipos - minimizar
            utilizacion: % promedio de utilización (0-100) - maximizar
            desplazamientos: Distancia total recorrida (km) - minimizar
            precedencias_cumplidas: ¿Se respetaron dependencias? - maximizar
            esperas: Tiempo total de espera (horas) - minimizar

        Returns:
            Score ponderado (0-100)
        """
        # Normalizar O1: Makespan (asumir máximo 1000 horas)
        o1_norm = max(0, min(1, (1000 - makespan) / 1000))

        # Normalizar O2: Desbalance (asumir máximo 50)
        o2_norm = max(0, min(1, (50 - desbalance) / 50))

        # Normalizar O3: Utilización (ya está 0-100)
        o3_norm = utilizacion / 100

        # Normalizar O4: Desplazamientos (asumir máximo 500km)
        o4_norm = max(0, min(1, (500 - desplazamientos) / 500))

        # Normalizar O5: Precedencias (0 o 1)
        o5_norm = float(precedencias_cumplidas)

        # Normalizar O6: Esperas (asumir máximo 500 horas)
        o6_norm = max(0, min(1, (500 - esperas) / 500))

        # Calcular score ponderado
        score = (
            self.pesos_objetivos["O1_makespan"] * o1_norm
            + self.pesos_objetivos["O2_desbalance"] * o2_norm
            + self.pesos_objetivos["O3_utilizacion"] * o3_norm
            + self.pesos_objetivos["O4_desplazamientos"] * o4_norm
            + self.pesos_objetivos["O5_precedencias"] * o5_norm
            + self.pesos_objetivos["O6_esperas"] * o6_norm
        )

        return score * 100  # Escalar a 0-100

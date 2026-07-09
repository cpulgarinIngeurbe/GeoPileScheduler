"""Optimizador greedy (baseline)."""

import time
from datetime import datetime, timedelta

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones

from .base_optimizer import BaseOptimizer, Solucion, Asignacion


class GreedyOptimizer(BaseOptimizer):
    """Optimizador greedy: asignar equipo libre más cercano."""

    def nombre(self) -> str:
        """Nombre del optimizador.

        Returns:
            "Greedy (Baseline)"
        """
        return "Greedy (Baseline)"

    def optimizar(self) -> Solucion:
        """Generar solución greedy.

        Estrategia:
        1. Obtener pilotes disponibles ordenados por prioridad
        2. Para cada pilote:
           - Encontrar equipo libre con menor carga
           - Si no hay libre, esperar
           - Asignar pilote
           - Estimar tiempo de finalización
        3. Retornar asignaciones en orden temporal

        Returns:
            Solucion con asignaciones greedy
        """
        inicio = time.time()

        try:
            asignaciones = []
            tiempo_actual = self.proyecto.fecha_inicio

            # Track de carga por equipo (pilotes asignados)
            carga_equipo = {eq_id: 0 for eq_id in self.proyecto.equipos.keys()}

            # Track de tiempo de liberación de equipos
            tiempo_liberacion = {
                eq_id: self.proyecto.fecha_inicio
                for eq_id in self.proyecto.equipos.keys()
            }

            # Obtener pilotes en orden (por ID, determinístico)
            pilotes_ids = sorted(self.proyecto.pilotes.keys())

            for pilote_id in pilotes_ids:
                pilote = self.proyecto.pilotes[pilote_id]

                # Encontrar equipo disponible con menor carga
                equipo_optimo = None
                tiempo_minimo = None

                for equipo_id, equipo in self.proyecto.equipos.items():
                    # Verificar que equipo trabaja en esta unidad
                    asignaciones_proyecto = [
                        a for a in self.proyecto.asignaciones_equipos
                        if a.equipo_id == equipo_id
                    ]

                    if pilote.unidad_id not in [
                        a.unidad_id for a in asignaciones_proyecto
                    ]:
                        continue  # Equipo no asignado a esta unidad

                    # Tiempo cuando equipo se libera
                    t_liberacion = tiempo_liberacion[equipo_id]

                    # Si este es mejor (más temprano)
                    if tiempo_minimo is None or t_liberacion < tiempo_minimo:
                        equipo_optimo = equipo_id
                        tiempo_minimo = t_liberacion

                if equipo_optimo is None:
                    continue  # No hay equipo para este pilote

                # Crear asignación
                equipo = self.proyecto.equipos[equipo_optimo]
                tiempo_duracion = timedelta(
                    hours=8 / equipo.rendimiento_pilotes_dia
                )
                tiempo_fin = tiempo_minimo + tiempo_duracion

                asignacion = Asignacion(
                    equipo_id=equipo_optimo,
                    pilote_id=pilote_id,
                    timestamp=tiempo_minimo,
                )

                asignaciones.append(asignacion)

                # Actualizar estado
                carga_equipo[equipo_optimo] += 1
                tiempo_liberacion[equipo_optimo] = tiempo_fin
                tiempo_actual = max(tiempo_actual, tiempo_fin)

            # Calcular makespan
            if asignaciones:
                makespan = (
                    max(
                        tiempo_liberacion.values()
                    ) - self.proyecto.fecha_inicio
                ).total_seconds() / 3600
            else:
                makespan = 0.0

            # Calcular métricas para score
            desbalance = self._calcular_desbalance(carga_equipo)
            utilizacion = self._calcular_utilizacion(carga_equipo)
            desplazamientos = self._calcular_desplazamientos(asignaciones)

            # Score multi-objetivo
            score = self.calcular_score_multiobjetivo(
                makespan=makespan,
                desbalance=desbalance,
                utilizacion=utilizacion,
                desplazamientos=desplazamientos,
                precedencias_cumplidas=True,
                esperas=0.0,
            )

            tiempo_total = time.time() - inicio

            solucion = Solucion(
                nombre_optimizador=self.nombre(),
                asignaciones=asignaciones,
                makespan=makespan,
                score_multiobjetivo=score,
                detalles={
                    "carga_equipo": carga_equipo,
                    "desbalance": desbalance,
                    "utilizacion": utilizacion,
                    "desplazamientos": desplazamientos,
                },
                tiempo_ejecucion=tiempo_total,
            )

            return solucion

        except Exception as e:
            raise ValueError(f"Error en optimización greedy: {str(e)}")

    def _calcular_desbalance(self, carga_equipo: dict[str, int]) -> float:
        """Calcular desbalance de carga (desviación estándar).

        Args:
            carga_equipo: Dict de cargas por equipo

        Returns:
            Desviación estándar
        """
        if not carga_equipo:
            return 0.0

        cargas = list(carga_equipo.values())
        media = sum(cargas) / len(cargas)

        if len(cargas) < 2:
            return 0.0

        varianza = sum((c - media) ** 2 for c in cargas) / len(cargas)
        return varianza ** 0.5

    def _calcular_utilizacion(self, carga_equipo: dict[str, int]) -> float:
        """Calcular utilización promedio de equipos.

        Args:
            carga_equipo: Dict de cargas por equipo

        Returns:
            Porcentaje (0-100)
        """
        if not carga_equipo:
            return 0.0

        total_carga = sum(carga_equipo.values())
        equipos_activos = len([c for c in carga_equipo.values() if c > 0])

        if equipos_activos == 0:
            return 0.0

        # Carga máxima posible = 100 pilotes por equipo
        max_carga = 100 * len(carga_equipo)

        if max_carga == 0:
            return 0.0

        return (total_carga / max_carga) * 100

    def _calcular_desplazamientos(self, asignaciones: list[Asignacion]) -> float:
        """Calcular distancia total de desplazamientos.

        Args:
            asignaciones: Lista de asignaciones

        Returns:
            Distancia en km (aproximada)
        """
        if len(asignaciones) < 2:
            return 0.0

        distancia_total = 0.0

        # Agrupar por equipo
        asignaciones_por_equipo = {}
        for asig in asignaciones:
            if asig.equipo_id not in asignaciones_por_equipo:
                asignaciones_por_equipo[asig.equipo_id] = []
            asignaciones_por_equipo[asig.equipo_id].append(asig)

        # Sumar distancias entre pilotes consecutivos
        for equipo_id, asigs in asignaciones_por_equipo.items():
            asigs_ordenadas = sorted(asigs, key=lambda a: a.timestamp)

            for i in range(1, len(asigs_ordenadas)):
                pilote_ant = self.proyecto.pilotes[asigs_ordenadas[i - 1].pilote_id]
                pilote_act = self.proyecto.pilotes[asigs_ordenadas[i].pilote_id]

                distancia = pilote_ant.distancia_a(pilote_act)
                # Convertir a km (asumir distancia en metros)
                distancia_total += distancia / 1000

        return distancia_total

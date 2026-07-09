"""Optimizador usando Google OR-Tools."""

import time
from datetime import datetime, timedelta

from ortools.routing import enums
from ortools.routing import routing_index_manager
from ortools.routing import routing_model

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones

from .base_optimizer import BaseOptimizer, Solucion, Asignacion


class ORToolsOptimizer(BaseOptimizer):
    """Optimizador usando Google OR-Tools VRP."""

    def nombre(self) -> str:
        """Nombre del optimizador.

        Returns:
            "OR-Tools (Industrial)"
        """
        return "OR-Tools (Industrial)"

    def optimizar(self) -> Solucion:
        """Generar solución usando OR-Tools.

        Modelado como VRP:
        - Vehículos = Equipos
        - Nodos = Pilotes
        - Capacidad = Rendimiento diario
        - Costo = Distancia + Multi-objetivo

        Returns:
            Solucion con asignaciones optimizadas
        """
        inicio = time.time()

        try:
            # Obtener índices
            pilotes_ids = sorted(self.proyecto.pilotes.keys())
            equipos_ids = sorted(self.proyecto.equipos.keys())

            # Crear manager
            manager = routing_index_manager.RoutingIndexManager(
                len(pilotes_ids) + 1,  # +1 para depósito
                len(equipos_ids),
                list(range(len(equipos_ids))),  # starts
            )

            # Crear modelo
            routing = routing_model.RoutingModel(manager)

            # Callback para distancias
            def distancia_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)

                if from_node == len(pilotes_ids) or to_node == len(pilotes_ids):
                    return 0  # Depósito

                pilote_from = pilotes_ids[from_node]
                pilote_to = pilotes_ids[to_node]

                p1 = self.proyecto.pilotes[pilote_from]
                p2 = self.proyecto.pilotes[pilote_to]

                return int(p1.distancia_a(p2))

            transit_callback_index = routing.RegisterTransitCallback(distancia_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Añadir restricciones de capacidad
            def capacidad_callback(from_index):
                node = manager.IndexToNode(from_index)
                if node < len(pilotes_ids):
                    return 1  # 1 pilote por tarea
                return 0

            capacidad_callback_index = routing.RegisterUnaryTransitCallback(
                capacidad_callback
            )

            routing.AddDimensionWithVehicleCapacity(
                capacidad_callback_index,
                0,  # slack
                [int(self.proyecto.equipos[eq_id].rendimiento_pilotes_dia)
                 for eq_id in equipos_ids],  # capacidades
                True,
                "Capacidad",
            )

            # Configuración de búsqueda
            search_parameters = enums.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            routing.parameters.first_solution_strategy = search_parameters
            routing.parameters.log_search = False
            routing.parameters.time_limit.seconds = 5  # Máximo 5 segundos

            # Resolver
            solution = routing.SolveWithParameters(routing.parameters)

            if not solution:
                # Fallback a greedy si OR-Tools falla
                from .greedy_optimizer import GreedyOptimizer
                greedy = GreedyOptimizer(
                    self.proyecto,
                    self.motor_geo,
                    self.motor_rest,
                    self.pesos_objetivos,
                )
                return greedy.optimizar()

            # Extraer solución
            asignaciones = []
            tiempo_actual = self.proyecto.fecha_inicio
            carga_equipo = {eq_id: 0 for eq_id in equipos_ids}

            for vehicle_id in range(len(equipos_ids)):
                index = routing.Start(vehicle_id)
                tiempo_equipo = self.proyecto.fecha_inicio

                while not routing.IsEnd(index):
                    node_index = manager.IndexToNode(index)

                    if node_index < len(pilotes_ids):
                        pilote_id = pilotes_ids[node_index]
                        equipo_id = equipos_ids[vehicle_id]

                        equipo = self.proyecto.equipos[equipo_id]
                        duracion = timedelta(
                            hours=8 / equipo.rendimiento_pilotes_dia
                        )

                        asignacion = Asignacion(
                            equipo_id=equipo_id,
                            pilote_id=pilote_id,
                            timestamp=tiempo_equipo,
                        )

                        asignaciones.append(asignacion)
                        carga_equipo[equipo_id] += 1
                        tiempo_equipo += duracion
                        tiempo_actual = max(tiempo_actual, tiempo_equipo)

                    index = solution.Next(index)

            # Ordenar asignaciones por timestamp
            asignaciones.sort(key=lambda a: a.timestamp)

            # Calcular makespan
            makespan = (tiempo_actual - self.proyecto.fecha_inicio).total_seconds() / 3600

            # Calcular métricas
            desbalance = self._calcular_desbalance(carga_equipo)
            utilizacion = self._calcular_utilizacion(carga_equipo)
            desplazamientos = self._calcular_desplazamientos(asignaciones)

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
            raise ValueError(f"Error en optimización OR-Tools: {str(e)}")

    def _calcular_desbalance(self, carga_equipo: dict[str, int]) -> float:
        """Calcular desbalance de carga."""
        if not carga_equipo:
            return 0.0

        cargas = list(carga_equipo.values())
        media = sum(cargas) / len(cargas) if cargas else 0

        if len(cargas) < 2:
            return 0.0

        varianza = sum((c - media) ** 2 for c in cargas) / len(cargas)
        return varianza ** 0.5

    def _calcular_utilizacion(self, carga_equipo: dict[str, int]) -> float:
        """Calcular utilización promedio."""
        if not carga_equipo:
            return 0.0

        total_carga = sum(carga_equipo.values())
        max_carga = 100 * len(carga_equipo)

        if max_carga == 0:
            return 0.0

        return (total_carga / max_carga) * 100

    def _calcular_desplazamientos(self, asignaciones: list[Asignacion]) -> float:
        """Calcular distancia total."""
        if len(asignaciones) < 2:
            return 0.0

        distancia_total = 0.0
        asignaciones_por_equipo = {}

        for asig in asignaciones:
            if asig.equipo_id not in asignaciones_por_equipo:
                asignaciones_por_equipo[asig.equipo_id] = []
            asignaciones_por_equipo[asig.equipo_id].append(asig)

        for equipo_id, asigs in asignaciones_por_equipo.items():
            asigs_ordenadas = sorted(asigs, key=lambda a: a.timestamp)

            for i in range(1, len(asigs_ordenadas)):
                pilote_ant = self.proyecto.pilotes[asigs_ordenadas[i - 1].pilote_id]
                pilote_act = self.proyecto.pilotes[asigs_ordenadas[i].pilote_id]

                distancia = pilote_ant.distancia_a(pilote_act)
                distancia_total += distancia / 1000

        return distancia_total

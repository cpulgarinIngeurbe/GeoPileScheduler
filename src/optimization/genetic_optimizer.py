"""Optimizador genético usando DEAP."""

import random
import time
from datetime import datetime, timedelta
from typing import Any

from deap import base, creator, tools, algorithms

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones

from .base_optimizer import BaseOptimizer, Solucion, Asignacion


class GeneticOptimizer(BaseOptimizer):
    """Optimizador genético con DEAP."""

    def __init__(
        self,
        proyecto: Proyecto,
        motor_geo: MotorGeometrico,
        motor_rest: MotorRestricciones,
        pesos_objetivos: dict[str, float] | None = None,
        poblacion: int = 50,
        generaciones: int = 30,
        seed: int = 42,
    ) -> None:
        """Inicializar optimizador genético.

        Args:
            proyecto: Proyecto
            motor_geo: MotorGeometrico
            motor_rest: MotorRestricciones
            pesos_objetivos: Pesos para objetivos
            poblacion: Tamaño de población
            generaciones: Número de generaciones
            seed: Seed para reproducibilidad
        """
        super().__init__(proyecto, motor_geo, motor_rest, pesos_objetivos)
        self.poblacion_size = poblacion
        self.generaciones = generaciones
        self.seed = seed
        random.seed(seed)

    def nombre(self) -> str:
        """Nombre del optimizador.

        Returns:
            "Genético (DEAP)"
        """
        return "Genético (DEAP)"

    def optimizar(self) -> Solucion:
        """Generar solución usando algoritmo genético.

        Individuo = Permutación de asignaciones equipos → pilotes
        Fitness = Score multi-objetivo
        Operadores: Cruce OX, mutación shuffle

        Returns:
            Solucion optimizada
        """
        inicio = time.time()

        try:
            # Setup DEAP
            self._setup_deap()

            # Población inicial
            poblacion = self._generar_poblacion_inicial(self.poblacion_size)

            # Evaluación inicial
            fitnesses = [self._evaluar_individuo(ind) for ind in poblacion]
            for ind, fit in zip(poblacion, fitnesses):
                ind.fitness.values = fit

            # Algoritmo genético
            hof = tools.HallOfFame(1)
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", lambda x: sum(f[0] for f in x) / len(x))
            stats.register("max", lambda x: max(f[0] for f in x))

            poblacion, _ = algorithms.eaSimple(
                poblacion,
                self.toolbox,
                cxpb=0.7,
                mutpb=0.2,
                ngen=self.generaciones,
                stats=stats,
                halloffame=hof,
                verbose=False,
            )

            # Mejor solución
            mejor_individuo = hof[0]
            mejores_asignaciones = self._individuo_a_asignaciones(mejor_individuo)

            # Calcular makespan y métricas
            carga_equipo = self._calcular_carga(mejores_asignaciones)
            makespan = self._calcular_makespan(mejores_asignaciones)
            desbalance = self._calcular_desbalance(carga_equipo)
            utilizacion = self._calcular_utilizacion(carga_equipo)
            desplazamientos = self._calcular_desplazamientos(mejores_asignaciones)

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
                asignaciones=mejores_asignaciones,
                makespan=makespan,
                score_multiobjetivo=score,
                detalles={
                    "carga_equipo": carga_equipo,
                    "desbalance": desbalance,
                    "utilizacion": utilizacion,
                    "desplazamientos": desplazamientos,
                    "generaciones_ejecutadas": self.generaciones,
                },
                tiempo_ejecucion=tiempo_total,
            )

            return solucion

        except Exception as e:
            raise ValueError(f"Error en optimización genética: {str(e)}")

    def _setup_deap(self) -> None:
        """Configurar tipos y toolbox de DEAP."""
        # Limpiar tipos previos
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual

        # Crear tipos
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create(
            "Individual",
            list,
            fitness=creator.FitnessMax,
        )

        self.toolbox = base.Toolbox()

        # Atributos: lista de índices de equipos (uno por pilote)
        equipos_ids = list(self.proyecto.equipos.keys())

        def gen_individuo():
            """Generar individuo: asignación de equipos a pilotes."""
            n_pilotes = len(self.proyecto.pilotes)
            n_equipos = len(equipos_ids)
            # Asignar equipos de forma uniforme
            return [i % n_equipos for i in range(n_pilotes)]

        self.toolbox.register(
            "individual",
            tools.initIterate,
            creator.Individual,
            gen_individuo,
        )
        self.toolbox.register(
            "population",
            tools.initRepeat,
            list,
            self.toolbox.individual,
        )

        # Operadores genéticos
        self.toolbox.register("evaluate", self._evaluar_individuo)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def _generar_poblacion_inicial(self, size: int) -> list:
        """Generar población inicial con diversidad."""
        poblacion = self.toolbox.population(n=size)

        # Mutar individuos para diversidad
        for ind in poblacion[1:]:  # Excepto el primero (greedy)
            tools.mutShuffleIndexes(ind, indpb=0.5)

        return poblacion

    def _evaluar_individuo(self, individuo: list[int]) -> tuple[float]:
        """Evaluar fitness de un individuo.

        Args:
            individuo: Lista de índices de equipos

        Returns:
            Tupla (fitness,)
        """
        try:
            asignaciones = self._individuo_a_asignaciones(individuo)

            carga_equipo = self._calcular_carga(asignaciones)
            makespan = self._calcular_makespan(asignaciones)
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

            return (score / 100.0,)  # Tupla requerida por DEAP

        except Exception as e:
            return (0.0,)  # Penalizar errores

    def _individuo_a_asignaciones(self, individuo: list[int]) -> list[Asignacion]:
        """Convertir individuo (índices) a asignaciones.

        Args:
            individuo: Lista de índices de equipos

        Returns:
            Lista de Asignacion
        """
        asignaciones = []
        pilotes_ids = sorted(self.proyecto.pilotes.keys())
        equipos_ids = sorted(self.proyecto.equipos.keys())

        tiempo_equipo = {eq_id: self.proyecto.fecha_inicio for eq_id in equipos_ids}

        for pilote_idx, equipo_idx in enumerate(individuo):
            if pilote_idx >= len(pilotes_ids):
                break

            pilote_id = pilotes_ids[pilote_idx]
            equipo_id = equipos_ids[equipo_idx % len(equipos_ids)]

            equipo = self.proyecto.equipos[equipo_id]
            duracion = timedelta(hours=8 / equipo.rendimiento_pilotes_dia)

            asignacion = Asignacion(
                equipo_id=equipo_id,
                pilote_id=pilote_id,
                timestamp=tiempo_equipo[equipo_id],
            )

            asignaciones.append(asignacion)
            tiempo_equipo[equipo_id] += duracion

        return asignaciones

    def _calcular_carga(self, asignaciones: list[Asignacion]) -> dict[str, int]:
        """Calcular carga por equipo."""
        carga = {eq_id: 0 for eq_id in self.proyecto.equipos.keys()}
        for asig in asignaciones:
            carga[asig.equipo_id] += 1
        return carga

    def _calcular_makespan(self, asignaciones: list[Asignacion]) -> float:
        """Calcular makespan."""
        if not asignaciones:
            return 0.0

        equipos_ids = sorted(self.proyecto.equipos.keys())
        tiempo_fin = {eq_id: self.proyecto.fecha_inicio for eq_id in equipos_ids}

        for asig in asignaciones:
            equipo = self.proyecto.equipos[asig.equipo_id]
            duracion = timedelta(hours=8 / equipo.rendimiento_pilotes_dia)
            tiempo_fin[asig.equipo_id] = asig.timestamp + duracion

        return (max(tiempo_fin.values()) - self.proyecto.fecha_inicio).total_seconds() / 3600

    def _calcular_desbalance(self, carga_equipo: dict[str, int]) -> float:
        """Calcular desbalance."""
        if not carga_equipo or len(carga_equipo) < 2:
            return 0.0

        cargas = list(carga_equipo.values())
        media = sum(cargas) / len(cargas)
        varianza = sum((c - media) ** 2 for c in cargas) / len(cargas)
        return varianza ** 0.5

    def _calcular_utilizacion(self, carga_equipo: dict[str, int]) -> float:
        """Calcular utilización."""
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

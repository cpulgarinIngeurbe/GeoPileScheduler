"""Comparador de múltiples optimizadores."""

from dataclasses import dataclass, field
from typing import Optional

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones

from .base_optimizer import Solucion
from .greedy_optimizer import GreedyOptimizer
from .ortools_optimizer import ORToolsOptimizer
from .genetic_optimizer import GeneticOptimizer


@dataclass
class ComparacionOptimizadores:
    """Comparación de múltiples soluciones."""

    soluciones: list[Solucion] = field(default_factory=list)
    mejor_solucion: Optional[Solucion] = None

    def agregar_solucion(self, solucion: Solucion) -> None:
        """Agregar solución a la comparación.

        Args:
            solucion: Solucion a agregar
        """
        self.soluciones.append(solucion)

        # Actualizar mejor
        if self.mejor_solucion is None or \
           solucion.score_multiobjetivo > self.mejor_solucion.score_multiobjetivo:
            self.mejor_solucion = solucion

    def get_mejor_solucion(self) -> Optional[Solucion]:
        """Obtener mejor solución.

        Returns:
            Solucion con mayor score
        """
        return self.mejor_solucion

    def get_estadisticas(self) -> dict:
        """Obtener estadísticas de comparación.

        Returns:
            Dict con métricas agregadas
        """
        if not self.soluciones:
            return {}

        scores = [s.score_multiobjetivo for s in self.soluciones]
        makespans = [s.makespan for s in self.soluciones]
        tiempos = [s.tiempo_ejecucion for s in self.soluciones]

        return {
            "cantidad_optimizadores": len(self.soluciones),
            "score_promedio": sum(scores) / len(scores),
            "score_maximo": max(scores),
            "score_minimo": min(scores),
            "makespan_promedio": sum(makespans) / len(makespans),
            "makespan_minimo": min(makespans),
            "makespan_maximo": max(makespans),
            "tiempo_promedio": sum(tiempos) / len(tiempos),
            "tiempo_total": sum(tiempos),
        }

    def generar_reporte_comparativo(self) -> str:
        """Generar reporte string de comparación.

        Returns:
            Reporte formateado
        """
        if not self.soluciones:
            return "No hay soluciones para comparar"

        reporte = "\n" + "=" * 80 + "\n"
        reporte += "COMPARACIÓN DE OPTIMIZADORES\n"
        reporte += "=" * 80 + "\n\n"

        # Tabla de resultados
        reporte += f"{'Optimizador':<25} {'Score':<10} {'Makespan':<12} {'Tiempo':<10}\n"
        reporte += "-" * 80 + "\n"

        for solucion in sorted(
            self.soluciones,
            key=lambda s: s.score_multiobjetivo,
            reverse=True
        ):
            reporte += (
                f"{solucion.nombre_optimizador:<25} "
                f"{solucion.score_multiobjetivo:>8.1f}  "
                f"{solucion.makespan:>10.1f}h  "
                f"{solucion.tiempo_ejecucion:>8.2f}s\n"
            )

        # Mejor solución
        if self.mejor_solucion:
            reporte += "\n" + "-" * 80 + "\n"
            reporte += f"🏆 MEJOR SOLUCIÓN: {self.mejor_solucion.nombre_optimizador}\n"
            reporte += f"   Score: {self.mejor_solucion.score_multiobjetivo:.1f}\n"
            reporte += f"   Makespan: {self.mejor_solucion.makespan:.1f} horas\n"
            reporte += f"   Tiempo: {self.mejor_solucion.tiempo_ejecucion:.2f} segundos\n"

        # Estadísticas
        stats = self.get_estadisticas()
        reporte += "\n" + "-" * 80 + "\n"
        reporte += "ESTADÍSTICAS AGREGADAS:\n"
        reporte += f"   • Score promedio: {stats['score_promedio']:.1f}\n"
        reporte += f"   • Makespan promedio: {stats['makespan_promedio']:.1f}h\n"
        reporte += f"   • Tiempo promedio: {stats['tiempo_promedio']:.2f}s\n"
        reporte += f"   • Tiempo total: {stats['tiempo_total']:.2f}s\n"

        reporte += "\n" + "=" * 80 + "\n"

        return reporte

    def imprimir_reporte(self) -> None:
        """Imprimir reporte a stdout."""
        print(self.generar_reporte_comparativo())


class ComparadorOptimizadores:
    """Comparador que ejecuta múltiples optimizadores."""

    def __init__(
        self,
        proyecto: Proyecto,
        motor_geo: MotorGeometrico,
        motor_rest: MotorRestricciones,
        pesos_objetivos: dict | None = None,
    ) -> None:
        """Inicializar comparador.

        Args:
            proyecto: Proyecto
            motor_geo: MotorGeometrico
            motor_rest: MotorRestricciones
            pesos_objetivos: Pesos para objetivos (opcional)
        """
        self.proyecto = proyecto
        self.motor_geo = motor_geo
        self.motor_rest = motor_rest
        self.pesos_objetivos = pesos_objetivos

    def ejecutar_todos(self) -> ComparacionOptimizadores:
        """Ejecutar todos los optimizadores disponibles.

        Returns:
            ComparacionOptimizadores con todas las soluciones
        """
        comparacion = ComparacionOptimizadores()

        # Greedy
        print("Ejecutando Greedy...")
        try:
            greedy = GreedyOptimizer(
                self.proyecto,
                self.motor_geo,
                self.motor_rest,
                self.pesos_objetivos,
            )
            solucion_greedy = greedy.optimizar()
            comparacion.agregar_solucion(solucion_greedy)
            print(f"✅ {solucion_greedy.resumen()}")
        except Exception as e:
            print(f"❌ Error Greedy: {str(e)}")

        # OR-Tools
        print("Ejecutando OR-Tools...")
        try:
            ortools = ORToolsOptimizer(
                self.proyecto,
                self.motor_geo,
                self.motor_rest,
                self.pesos_objetivos,
            )
            solucion_ortools = ortools.optimizar()
            comparacion.agregar_solucion(solucion_ortools)
            print(f"✅ {solucion_ortools.resumen()}")
        except Exception as e:
            print(f"❌ Error OR-Tools: {str(e)}")

        # Genético
        print("Ejecutando Genético...")
        try:
            genetico = GeneticOptimizer(
                self.proyecto,
                self.motor_geo,
                self.motor_rest,
                self.pesos_objetivos,
                poblacion=30,
                generaciones=20,
            )
            solucion_genetico = genetico.optimizar()
            comparacion.agregar_solucion(solucion_genetico)
            print(f"✅ {solucion_genetico.resumen()}")
        except Exception as e:
            print(f"❌ Error Genético: {str(e)}")

        return comparacion

    def ejecutar_optimizador(self, nombre: str) -> Optional[Solucion]:
        """Ejecutar un optimizador específico.

        Args:
            nombre: "greedy", "ortools" o "genetic"

        Returns:
            Solucion o None si error
        """
        try:
            if nombre.lower() == "greedy":
                optimizer = GreedyOptimizer(
                    self.proyecto,
                    self.motor_geo,
                    self.motor_rest,
                    self.pesos_objetivos,
                )
            elif nombre.lower() == "ortools":
                optimizer = ORToolsOptimizer(
                    self.proyecto,
                    self.motor_geo,
                    self.motor_rest,
                    self.pesos_objetivos,
                )
            elif nombre.lower() == "genetic":
                optimizer = GeneticOptimizer(
                    self.proyecto,
                    self.motor_geo,
                    self.motor_rest,
                    self.pesos_objetivos,
                )
            else:
                raise ValueError(f"Optimizador desconocido: {nombre}")

            return optimizer.optimizar()

        except Exception as e:
            print(f"❌ Error ejecutando {nombre}: {str(e)}")
            return None

"""Visualizaciones de simulación."""

from datetime import datetime
from typing import Optional

import plotly.graph_objects as go
import plotly.subplots as sp

from src.core.models import Proyecto

from .engine import MotorSimulacion
from .event_model import EventoSimulacion, TipoEvento
from .statistics import calcular_secuencia_ejecucion, calcular_utilization_equipos


def plot_timeline(
    motor_sim: MotorSimulacion,
    output_path: str = "output/timeline.html",
) -> Optional[str]:
    """Generar gráfico de línea temporal de eventos.

    Args:
        motor_sim: MotorSimulacion con historial
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        eventos = motor_sim.historial_eventos
        if not eventos:
            return None

        # Agrupar eventos por tipo
        tipos = list(set(e.tipo for e in eventos))
        colores = {t: i for i, t in enumerate(tipos)}

        fig = go.Figure()

        for evento in eventos:
            fig.add_trace(
                go.Scatter(
                    x=[evento.timestamp],
                    y=[evento.tipo.value],
                    mode="markers",
                    marker=dict(size=8, color=colores[evento.tipo]),
                    name=evento.tipo.value,
                    text=f"{evento.entidad_id}<br>{evento.datos}",
                    hovertemplate="%{text}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Timeline de Eventos de Simulación",
            xaxis_title="Tiempo",
            yaxis_title="Tipo de Evento",
            height=600,
            hovermode="closest",
        )

        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando timeline: {str(e)}")
        return None


def plot_gantt(
    motor_sim: MotorSimulacion,
    proyecto: Proyecto,
    output_path: str = "output/gantt.html",
) -> Optional[str]:
    """Generar diagrama Gantt de equipos.

    Args:
        motor_sim: MotorSimulacion con historial
        proyecto: Proyecto
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        eventos_ejecucion = [
            e
            for e in motor_sim.historial_eventos
            if e.tipo == TipoEvento.FIN_EJECUCION
        ]

        if not eventos_ejecucion:
            return None

        # Construir timeline de cada equipo
        equipos_dict = {}
        for evento in eventos_ejecucion:
            equipo_id = evento.datos.get("equipo_id")
            pilote_id = evento.datos.get("pilote_id")

            if equipo_id:
                if equipo_id not in equipos_dict:
                    equipos_dict[equipo_id] = []
                equipos_dict[equipo_id].append(
                    {
                        "pilote": pilote_id,
                        "fin": evento.timestamp,
                    }
                )

        # Calcular inicio de cada tarea (fin anterior + pequeño gap)
        from datetime import timedelta

        fig = go.Figure()

        for equipo_id, tareas in equipos_dict.items():
            tiempo_inicio = motor_sim.tiempo_actual

            for i, tarea in enumerate(tareas):
                duracion = timedelta(hours=4)  # Asumiendo 4h por pilote
                tiempo_fin = tarea["fin"]
                tiempo_inicio_tarea = tiempo_fin - duracion

                fig.add_trace(
                    go.Bar(
                        x=[duracion],
                        y=[equipo_id],
                        orientation="h",
                        name=tarea["pilote"],
                        text=tarea["pilote"],
                        textposition="auto",
                        marker=dict(
                            color=hash(tarea["pilote"]) % 360,
                            colorscale="Viridis",
                        ),
                        base=tiempo_inicio_tarea,
                    )
                )

        fig.update_layout(
            title="Diagrama Gantt de Equipos",
            xaxis_title="Tiempo",
            yaxis_title="Equipo",
            barmode="overlay",
            height=400,
            hovermode="closest",
        )

        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando Gantt: {str(e)}")
        return None


def plot_progression(
    motor_sim: MotorSimulacion,
    output_path: str = "output/progression.html",
) -> Optional[str]:
    """Generar gráfico de progreso de ejecución.

    Args:
        motor_sim: MotorSimulacion con historial
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        eventos_ejecucion = [
            e
            for e in motor_sim.historial_eventos
            if e.tipo == TipoEvento.FIN_EJECUCION
        ]

        if not eventos_ejecucion:
            return None

        # Calcular progreso acumulado
        tiempos = []
        progreso = []
        pilotes_ejecutados = 0

        for evento in eventos_ejecucion:
            tiempos.append(evento.timestamp)
            pilotes_ejecutados += 1
            progreso.append(pilotes_ejecutados)

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=tiempos,
                y=progreso,
                mode="lines+markers",
                name="Pilotes Ejecutados",
                fill="tozeroy",
                line=dict(color="rgb(0, 100, 200)", width=3),
                marker=dict(size=6),
            )
        )

        fig.update_layout(
            title="Progreso de Ejecución",
            xaxis_title="Tiempo",
            yaxis_title="Pilotes Ejecutados",
            height=500,
            hovermode="x unified",
        )

        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando progreso: {str(e)}")
        return None


def plot_equipment_utilization(
    motor_sim: MotorSimulacion,
    output_path: str = "output/utilization.html",
) -> Optional[str]:
    """Generar gráfico de utilización de equipos.

    Args:
        motor_sim: MotorSimulacion con historial
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        utilization = calcular_utilization_equipos(motor_sim)

        if not utilization:
            return None

        equipos = list(utilization.keys())
        pilotes_ejecutados = list(utilization.values())

        fig = go.Figure(
            data=[
                go.Bar(
                    x=equipos,
                    y=pilotes_ejecutados,
                    marker=dict(color="lightblue"),
                    text=pilotes_ejecutados,
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Utilización de Equipos",
            xaxis_title="Equipo",
            yaxis_title="Pilotes Ejecutados",
            height=400,
        )

        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando utilización: {str(e)}")
        return None


def plot_event_histogram(
    motor_sim: MotorSimulacion,
    output_path: str = "output/event_histogram.html",
) -> Optional[str]:
    """Generar histograma de distribución de eventos.

    Args:
        motor_sim: MotorSimulacion con historial
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        eventos = motor_sim.historial_eventos

        if not eventos:
            return None

        # Contar por tipo
        tipo_counts = {}
        for evento in eventos:
            tipo = evento.tipo.value
            tipo_counts[tipo] = tipo_counts.get(tipo, 0) + 1

        tipos = list(tipo_counts.keys())
        counts = list(tipo_counts.values())

        fig = go.Figure(
            data=[
                go.Bar(
                    x=tipos,
                    y=counts,
                    marker=dict(color="coral"),
                    text=counts,
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Distribución de Tipos de Evento",
            xaxis_title="Tipo de Evento",
            yaxis_title="Cantidad",
            height=400,
            xaxis_tickangle=-45,
        )

        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando histograma: {str(e)}")
        return None


def generar_dashboard_simulacion(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
    output_path: str = "output/dashboard_simulacion.html",
) -> Optional[str]:
    """Generar dashboard completo de simulación.

    Args:
        proyecto: Proyecto
        motor_sim: MotorSimulacion con historial
        output_path: Ruta de salida HTML

    Returns:
        Ruta del archivo creado o None si error
    """
    try:
        # Crear subplots
        fig = sp.make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Progreso de Ejecución",
                "Utilización de Equipos",
                "Distribución de Eventos",
                "Timeline",
            ),
        )

        # Progreso
        eventos_ejecucion = [
            e
            for e in motor_sim.historial_eventos
            if e.tipo == TipoEvento.FIN_EJECUCION
        ]
        tiempos = [e.timestamp for e in eventos_ejecucion]
        progreso_vals = list(range(1, len(tiempos) + 1))

        fig.add_trace(
            go.Scatter(
                x=tiempos,
                y=progreso_vals,
                mode="lines+markers",
                name="Progreso",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )

        # Utilización
        utilization = calcular_utilization_equipos(motor_sim)
        if utilization:
            fig.add_trace(
                go.Bar(
                    x=list(utilization.keys()),
                    y=list(utilization.values()),
                    name="Utilización",
                    marker=dict(color="green"),
                ),
                row=1,
                col=2,
            )

        # Histograma
        tipo_counts = {}
        for evento in motor_sim.historial_eventos:
            tipo = evento.tipo.value
            tipo_counts[tipo] = tipo_counts.get(tipo, 0) + 1

        fig.add_trace(
            go.Bar(
                x=list(tipo_counts.keys()),
                y=list(tipo_counts.values()),
                name="Eventos",
                marker=dict(color="orange"),
            ),
            row=2,
            col=1,
        )

        # Timeline
        for tipo in set(e.tipo for e in motor_sim.historial_eventos):
            eventos_tipo = [e for e in motor_sim.historial_eventos if e.tipo == tipo]
            fig.add_trace(
                go.Scatter(
                    x=[e.timestamp for e in eventos_tipo],
                    y=[tipo.value for _ in eventos_tipo],
                    mode="markers",
                    name=tipo.value,
                    marker=dict(size=5),
                ),
                row=2,
                col=2,
            )

        fig.update_layout(height=800, title_text="Dashboard de Simulación")
        fig.write_html(output_path)
        return output_path

    except Exception as e:
        print(f"❌ Error generando dashboard: {str(e)}")
        return None

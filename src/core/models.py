"""Modelos de datos para GeoPile Scheduler.

Define todas las estructuras de datos internas del sistema.
Cada clase representa una entidad del modelo de datos del proyecto.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from src.core.enums import ModoInicio, ModoFin, EstadoPilote


@dataclass
class Pilote:
    """Representa un pilote individual en el proyecto.

    Atributos:
        id: Identificador único del pilote (PiloteID del Excel).
        unidad_id: ID de la unidad estructural a la que pertenece.
        x: Coordenada X (metros) desde el modelo BIM.
        y: Coordenada Y (metros) desde el modelo BIM.
        estado: Estado actual del pilote (PENDIENTE al iniciar).

    Raises:
        ValueError: Si id está vacío o coordenadas son negativas.
    """

    id: str
    unidad_id: str
    x: float
    y: float
    estado: EstadoPilote = field(default=EstadoPilote.PENDIENTE)

    def __post_init__(self) -> None:
        """Valida los datos del pilote."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError(f"Pilote id debe ser string no vacío, recibido: {self.id}")

        if not isinstance(self.x, (int, float)) or not isinstance(self.y, (int, float)):
            raise ValueError(
                f"Coordenadas deben ser numéricas. Recibido: x={self.x}, y={self.y}"
            )

        if self.x < 0 or self.y < 0:
            raise ValueError(
                f"Coordenadas no pueden ser negativas. Recibido: x={self.x}, y={self.y}"
            )

    def distancia_a(self, otro: "Pilote") -> float:
        """Calcula distancia euclidiana a otro pilote.

        Args:
            otro: Otro pilote.

        Returns:
            Distancia en metros.
        """
        return ((self.x - otro.x) ** 2 + (self.y - otro.y) ** 2) ** 0.5


@dataclass
class UnidadEstructural:
    """Representa una unidad estructural del proyecto (torre, podio, etc).

    Atributos:
        id: Identificador único (UnidadID del Excel).
        nombre: Nombre descriptivo (Torre 1, Podio, etc).
        pilotes: Diccionario de pilotes en esta unidad {id_pilote: Pilote}.

    Raises:
        ValueError: Si id está vacío.
    """

    id: str
    nombre: str
    pilotes: Dict[str, Pilote] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida los datos de la unidad."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError(f"UnidadID debe ser string no vacío, recibido: {self.id}")

        if not self.nombre or not isinstance(self.nombre, str):
            raise ValueError(f"Nombre debe ser string no vacío, recibido: {self.nombre}")

    def agregar_pilote(self, pilote: Pilote) -> None:
        """Añade un pilote a esta unidad.

        Args:
            pilote: Pilote a añadir.

        Raises:
            ValueError: Si ya existe un pilote con ese ID.
        """
        if pilote.id in self.pilotes:
            raise ValueError(
                f"Pilote {pilote.id} ya existe en unidad {self.id}"
            )
        self.pilotes[pilote.id] = pilote

    @property
    def num_pilotes(self) -> int:
        """Retorna cantidad de pilotes en esta unidad."""
        return len(self.pilotes)


@dataclass
class Equipo:
    """Representa una piloteadora (equipo de construcción).

    Atributos:
        id: Identificador único (EquipoID del Excel).
        nombre: Nombre descriptivo.
        rendimiento_pilotes_dia: Cantidad de pilotes que ejecuta por día.
        modo_inicio: AUTO o MANUAL (ver ModoInicio).
        pilote_inicio: ID del pilote de inicio (solo si modo_inicio=MANUAL).
        modo_fin: AUTO o MANUAL (ver ModoFin).
        pilote_fin: ID del pilote de fin (solo si modo_fin=MANUAL).

    Raises:
        ValueError: Si datos son inválidos.
    """

    id: str
    nombre: str
    rendimiento_pilotes_dia: int
    modo_inicio: ModoInicio
    pilote_inicio: Optional[str] = None
    modo_fin: ModoFin = field(default=ModoFin.AUTO)
    pilote_fin: Optional[str] = None

    def __post_init__(self) -> None:
        """Valida los datos del equipo."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError(f"EquipoID debe ser string no vacío, recibido: {self.id}")

        if not self.nombre or not isinstance(self.nombre, str):
            raise ValueError(f"Nombre debe ser string no vacío, recibido: {self.nombre}")

        if not isinstance(self.rendimiento_pilotes_dia, int) or self.rendimiento_pilotes_dia <= 0:
            raise ValueError(
                f"Rendimiento debe ser entero > 0, recibido: {self.rendimiento_pilotes_dia}"
            )

        if self.modo_inicio == ModoInicio.MANUAL and not self.pilote_inicio:
            raise ValueError(
                f"Equipo {self.id} tiene modo_inicio=MANUAL pero pilote_inicio está vacío"
            )

        if self.modo_fin == ModoFin.MANUAL and not self.pilote_fin:
            raise ValueError(
                f"Equipo {self.id} tiene modo_fin=MANUAL pero pilote_fin está vacío"
            )


@dataclass
class AsignacionEquipo:
    """Representa la relación entre un equipo y una unidad estructural.

    Atributos:
        equipo_id: ID del equipo.
        unidad_id: ID de la unidad estructural.
        prioridad: Valor de prioridad inicial (entero). Mayor = más prioritario.

    Raises:
        ValueError: Si prioridad no es entero.
    """

    equipo_id: str
    unidad_id: str
    prioridad: int

    def __post_init__(self) -> None:
        """Valida los datos de la asignación."""
        if not isinstance(self.prioridad, int):
            raise ValueError(
                f"Prioridad debe ser entero, recibido: {self.prioridad} ({type(self.prioridad)})"
            )


@dataclass
class Proyecto:
    """Representa el proyecto completo de pilotaje.

    Este es el contenedor principal que agrupa todas las entidades del sistema.
    Inicialmente se carga desde un archivo Excel.

    Atributos:
        nombre: Nombre del proyecto.
        fecha_inicio: Fecha de inicio de la simulación.
        radio_critico_m: Radio crítico (metros). Distancia mínima entre excavaciones.
        tiempo_restriccion_h: Tiempo mínimo (horas) entre excavaciones cercanas.
        unidades: Diccionario de unidades {id: UnidadEstructural}.
        equipos: Diccionario de equipos {id: Equipo}.
        asignaciones: Lista de asignaciones equipo-unidad.

    Raises:
        ValueError: Si datos son inválidos.

    Nota:
        La información calculada (matriz de distancias, grafo, eventos, etc)
        es generada por otros módulos, NO forma parte de este modelo.
    """

    nombre: str
    fecha_inicio: datetime
    radio_critico_m: float
    tiempo_restriccion_h: float
    unidades_estructurales: Dict[str, UnidadEstructural] = field(default_factory=dict)
    equipos: Dict[str, Equipo] = field(default_factory=dict)
    asignaciones_equipos: List[AsignacionEquipo] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Valida los datos del proyecto."""
        if not self.nombre or not isinstance(self.nombre, str):
            raise ValueError(f"Nombre debe ser string no vacío, recibido: {self.nombre}")

        if not isinstance(self.fecha_inicio, datetime):
            raise ValueError(
                f"fecha_inicio debe ser datetime, recibido: {type(self.fecha_inicio)}"
            )

        if not isinstance(self.radio_critico_m, (int, float)) or self.radio_critico_m <= 0:
            raise ValueError(
                f"radio_critico_m debe ser número > 0, recibido: {self.radio_critico_m}"
            )

        if not isinstance(self.tiempo_restriccion_h, (int, float)) or self.tiempo_restriccion_h < 0:
            raise ValueError(
                f"tiempo_restriccion_h debe ser número >= 0, recibido: {self.tiempo_restriccion_h}"
            )

    @property
    def pilotes(self) -> Dict[str, Pilote]:
        """Obtener todos los pilotes del proyecto.

        Returns:
            Diccionario combinado de todos los pilotes {id: Pilote}
        """
        pilotes_totales = {}
        for unidad in self.unidades_estructurales.values():
            pilotes_totales.update(unidad.pilotes)
        return pilotes_totales

    @property
    def unidades(self) -> Dict[str, UnidadEstructural]:
        """Acceso compatible a unidades_estructurales.

        Returns:
            Diccionario de unidades
        """
        return self.unidades_estructurales

    @property
    def asignaciones(self) -> List[AsignacionEquipo]:
        """Acceso compatible a asignaciones_equipos.

        Returns:
            Lista de asignaciones
        """
        return self.asignaciones_equipos

    def agregar_unidad(self, unidad: UnidadEstructural) -> None:
        """Añade una unidad estructural al proyecto.

        Args:
            unidad: UnidadEstructural a añadir.

        Raises:
            ValueError: Si ya existe una unidad con ese ID.
        """
        if unidad.id in self.unidades_estructurales:
            raise ValueError(f"Unidad {unidad.id} ya existe en el proyecto")
        self.unidades[unidad.id] = unidad

    def agregar_equipo(self, equipo: Equipo) -> None:
        """Añade un equipo al proyecto.

        Args:
            equipo: Equipo a añadir.

        Raises:
            ValueError: Si ya existe un equipo con ese ID.
        """
        if equipo.id in self.equipos:
            raise ValueError(f"Equipo {equipo.id} ya existe en el proyecto")
        self.equipos[equipo.id] = equipo

    def agregar_asignacion(self, asignacion: AsignacionEquipo) -> None:
        """Añade una asignación equipo-unidad.

        Args:
            asignacion: AsignacionEquipo a añadir.
        """
        self.asignaciones.append(asignacion)

    @property
    def num_unidades(self) -> int:
        """Retorna cantidad de unidades estructurales."""
        return len(self.unidades)

    @property
    def num_equipos(self) -> int:
        """Retorna cantidad de equipos."""
        return len(self.equipos)

    @property
    def num_pilotes(self) -> int:
        """Retorna cantidad total de pilotes en todas las unidades."""
        return sum(u.num_pilotes for u in self.unidades.values())

    def obtener_pilote(self, pilote_id: str) -> Optional[Pilote]:
        """Busca un pilote por ID en todas las unidades.

        Args:
            pilote_id: ID del pilote a buscar.

        Returns:
            Pilote si existe, None en caso contrario.
        """
        for unidad in self.unidades.values():
            if pilote_id in unidad.pilotes:
                return unidad.pilotes[pilote_id]
        return None

    def obtener_unidad_pilote(self, pilote_id: str) -> Optional[UnidadEstructural]:
        """Obtiene la unidad a la que pertenece un pilote.

        Args:
            pilote_id: ID del pilote.

        Returns:
            UnidadEstructural si existe, None en caso contrario.
        """
        for unidad in self.unidades.values():
            if pilote_id in unidad.pilotes:
                return unidad
        return None

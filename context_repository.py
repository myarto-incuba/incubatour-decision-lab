import json
import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path("data/capacidad_turistica.db")


def get_connection() -> sqlite3.Connection:
    """
    Abre una conexión con la misma base SQLite
    utilizada por el resto de la aplicación.
    """

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_context_table() -> None:
    """
    Crea la tabla de contexto cualitativo.
    Cada destino tendrá un único registro.
    """

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS destination_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination_id INTEGER NOT NULL UNIQUE,

                relacion_residentes_visitantes TEXT,
                conflictos_turisticos TEXT,
                preocupaciones_sociales TEXT,
                participacion_ciudadana TEXT,

                estrategia_turistica TEXT,
                observatorio_turistico TEXT,
                equipo_tecnico TEXT,
                coordinacion_publico_privada TEXT,

                posicionamiento_destino TEXT,
                reputacion_actual TEXT,
                eventos_reputacionales TEXT,
                recuperacion_imagen TEXT,

                plan_crisis TEXT,
                diversificacion_mercados TEXT,
                dependencia_estacional TEXT,
                capacidad_redistribucion TEXT,

                notas_contexto TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(destination_id)
                REFERENCES destinations(id)
                ON DELETE CASCADE
            )
            """
        )


def save_context(
    destination_id: int,
    data: dict[str, Any],
) -> None:
    """
    Crea o actualiza el contexto cualitativo
    asociado a un destino.
    """

    fields = {
        "relacion_residentes_visitantes": data.get(
            "relacion_residentes_visitantes",
            "",
        ),
        "conflictos_turisticos": data.get(
            "conflictos_turisticos",
            "",
        ),
        "preocupaciones_sociales": json.dumps(
            data.get("preocupaciones_sociales", []),
            ensure_ascii=False,
        ),
        "participacion_ciudadana": data.get(
            "participacion_ciudadana",
            "",
        ),
        "estrategia_turistica": data.get(
            "estrategia_turistica",
            "",
        ),
        "observatorio_turistico": data.get(
            "observatorio_turistico",
            "",
        ),
        "equipo_tecnico": data.get(
            "equipo_tecnico",
            "",
        ),
        "coordinacion_publico_privada": data.get(
            "coordinacion_publico_privada",
            "",
        ),
        "posicionamiento_destino": data.get(
            "posicionamiento_destino",
            "",
        ),
        "reputacion_actual": data.get(
            "reputacion_actual",
            "",
        ),
        "eventos_reputacionales": json.dumps(
            data.get("eventos_reputacionales", []),
            ensure_ascii=False,
        ),
        "recuperacion_imagen": data.get(
            "recuperacion_imagen",
            "",
        ),
        "plan_crisis": data.get(
            "plan_crisis",
            "",
        ),
        "diversificacion_mercados": data.get(
            "diversificacion_mercados",
            "",
        ),
        "dependencia_estacional": data.get(
            "dependencia_estacional",
            "",
        ),
        "capacidad_redistribucion": data.get(
            "capacidad_redistribucion",
            "",
        ),
        "notas_contexto": data.get(
            "notas_contexto",
            "",
        ).strip(),
    }

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM destination_context
            WHERE destination_id = ?
            """,
            (destination_id,),
        ).fetchone()

        if existing:
            assignments = ", ".join(
                f"{field} = ?"
                for field in fields
            )

            connection.execute(
                f"""
                UPDATE destination_context
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE destination_id = ?
                """,
                list(fields.values())
                + [destination_id],
            )

        else:
            columns = ", ".join(
                ["destination_id"]
                + list(fields.keys())
            )

            placeholders = ", ".join(
                "?"
                for _ in range(
                    len(fields) + 1
                )
            )

            connection.execute(
                f"""
                INSERT INTO destination_context (
                    {columns}
                )
                VALUES ({placeholders})
                """,
                [destination_id]
                + list(fields.values()),
            )


def get_context(
    destination_id: int,
) -> dict[str, Any] | None:
    """
    Recupera el contexto cualitativo de un destino.
    """

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM destination_context
            WHERE destination_id = ?
            """,
            (destination_id,),
        ).fetchone()

    if row is None:
        return None

    context = dict(row)

    for field in (
        "preocupaciones_sociales",
        "eventos_reputacionales",
    ):
        value = context.get(field)

        try:
            context[field] = (
                json.loads(value)
                if value
                else []
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            context[field] = []

    return context


def calculate_context_completeness(
    context: dict[str, Any] | None,
) -> int:
    """
    Calcula la completitud de las preguntas cualitativas.
    """

    if not context:
        return 0

    fields = [
        "relacion_residentes_visitantes",
        "conflictos_turisticos",
        "participacion_ciudadana",
        "estrategia_turistica",
        "observatorio_turistico",
        "equipo_tecnico",
        "coordinacion_publico_privada",
        "posicionamiento_destino",
        "reputacion_actual",
        "recuperacion_imagen",
        "plan_crisis",
        "diversificacion_mercados",
        "dependencia_estacional",
        "capacidad_redistribucion",
    ]

    completed = sum(
        bool(context.get(field))
        and context.get(field) != "Sin evaluar"
        for field in fields
    )

    return round(
        completed / len(fields) * 100
    )
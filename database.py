import json
import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path("data/capacidad_turistica.db")


def get_connection() -> sqlite3.Connection:
    """Abre una conexión a la base de datos SQLite."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db() -> None:
    """Crea las tablas principales del sistema."""

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                municipio TEXT NOT NULL,
                provincia TEXT,
                comunidad_autonoma TEXT,
                pais TEXT DEFAULT 'España',
                anio_referencia INTEGER,

                tipologias TEXT,
                propuesta_valor TEXT,

                poblacion_residente INTEGER DEFAULT 0,
                visitantes_anuales INTEGER DEFAULT 0,
                excursionistas_anuales INTEGER DEFAULT 0,
                pernoctaciones_anuales INTEGER DEFAULT 0,
                plazas_alojamiento INTEGER DEFAULT 0,
                meses_temporada_alta TEXT,

                infraestructura TEXT,
                fragilidad_ambiental TEXT,
                aceptacion_social TEXT,
                gestion_flujos TEXT,
                viviendas_turisticas TEXT,
                impactos TEXT,

                fuente_datos TEXT,
                observaciones TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination_id INTEGER NOT NULL,

                nombre TEXT NOT NULL,
                tipo_zona TEXT,
                referencia TEXT,

                latitud REAL,
                longitud REAL,

                presion TEXT,
                fragilidad TEXT,
                infraestructura TEXT,

                impactos TEXT,
                evidencia TEXT,

                prioridad_score INTEGER DEFAULT 0,
                prioridad_nivel TEXT,
                recomendacion TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(destination_id)
                REFERENCES destinations(id)
                ON DELETE CASCADE
            )
            """
        )


# =========================================================
# DESTINOS
# =========================================================

def save_destination(
    data: dict[str, Any],
    destination_id: int | None = None,
) -> int:
    """Crea un destino nuevo o actualiza uno existente."""

    fields = {
        "municipio": data.get("municipio", "").strip(),
        "provincia": data.get("provincia", "").strip(),
        "comunidad_autonoma": data.get(
            "comunidad_autonoma",
            "",
        ).strip(),
        "pais": data.get("pais", "España").strip(),
        "anio_referencia": data.get("anio_referencia"),
        "tipologias": json.dumps(
            data.get("tipologias", []),
            ensure_ascii=False,
        ),
        "propuesta_valor": data.get(
            "propuesta_valor",
            "",
        ).strip(),
        "poblacion_residente": data.get(
            "poblacion_residente",
            0,
        ),
        "visitantes_anuales": data.get(
            "visitantes_anuales",
            0,
        ),
        "excursionistas_anuales": data.get(
            "excursionistas_anuales",
            0,
        ),
        "pernoctaciones_anuales": data.get(
            "pernoctaciones_anuales",
            0,
        ),
        "plazas_alojamiento": data.get(
            "plazas_alojamiento",
            0,
        ),
        "meses_temporada_alta": json.dumps(
            data.get("meses_temporada_alta", []),
            ensure_ascii=False,
        ),
        "infraestructura": data.get(
            "infraestructura",
            "",
        ),
        "fragilidad_ambiental": data.get(
            "fragilidad_ambiental",
            "",
        ),
        "aceptacion_social": data.get(
            "aceptacion_social",
            "",
        ),
        "gestion_flujos": data.get(
            "gestion_flujos",
            "",
        ),
        "viviendas_turisticas": data.get(
            "viviendas_turisticas",
            "",
        ),
        "impactos": json.dumps(
            data.get("impactos", []),
            ensure_ascii=False,
        ),
        "fuente_datos": data.get(
            "fuente_datos",
            "",
        ).strip(),
        "observaciones": data.get(
            "observaciones",
            "",
        ).strip(),
    }

    with get_connection() as connection:

        if destination_id:
            assignments = ", ".join(
                f"{field} = ?"
                for field in fields
            )

            values = list(fields.values()) + [
                destination_id
            ]

            connection.execute(
                f"""
                UPDATE destinations
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                values,
            )

            return destination_id

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(
            "?"
            for _ in fields
        )

        cursor = connection.execute(
            f"""
            INSERT INTO destinations ({columns})
            VALUES ({placeholders})
            """,
            list(fields.values()),
        )

        return int(cursor.lastrowid)


def list_destinations() -> list[dict[str, Any]]:
    """Devuelve todos los destinos guardados."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM destinations
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [
        _deserialize_destination(dict(row))
        for row in rows
    ]


def get_destination(
    destination_id: int,
) -> dict[str, Any] | None:
    """Recupera un destino por su ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM destinations
            WHERE id = ?
            """,
            (destination_id,),
        ).fetchone()

    if row is None:
        return None

    return _deserialize_destination(dict(row))


def delete_destination(destination_id: int) -> None:
    """Elimina un destino y sus zonas."""

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM zones
            WHERE destination_id = ?
            """,
            (destination_id,),
        )

        connection.execute(
            """
            DELETE FROM destinations
            WHERE id = ?
            """,
            (destination_id,),
        )


def _deserialize_destination(
    destination: dict[str, Any],
) -> dict[str, Any]:
    """Convierte campos JSON en listas."""

    json_fields = [
        "tipologias",
        "meses_temporada_alta",
        "impactos",
    ]

    for field in json_fields:
        value = destination.get(field)

        try:
            destination[field] = (
                json.loads(value)
                if value
                else []
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            destination[field] = []

    return destination


# =========================================================
# ZONAS
# =========================================================

def save_zone(
    data: dict[str, Any],
    zone_id: int | None = None,
) -> int:
    """Crea o actualiza una zona turística."""

    fields = {
        "destination_id": data["destination_id"],
        "nombre": data.get("nombre", "").strip(),
        "tipo_zona": data.get(
            "tipo_zona",
            "",
        ).strip(),
        "referencia": data.get(
            "referencia",
            "",
        ).strip(),
        "latitud": data.get("latitud"),
        "longitud": data.get("longitud"),
        "presion": data.get("presion", ""),
        "fragilidad": data.get(
            "fragilidad",
            "",
        ),
        "infraestructura": data.get(
            "infraestructura",
            "",
        ),
        "impactos": json.dumps(
            data.get("impactos", []),
            ensure_ascii=False,
        ),
        "evidencia": data.get(
            "evidencia",
            "",
        ).strip(),
        "prioridad_score": data.get(
            "prioridad_score",
            0,
        ),
        "prioridad_nivel": data.get(
            "prioridad_nivel",
            "",
        ),
        "recomendacion": data.get(
            "recomendacion",
            "",
        ).strip(),
    }

    with get_connection() as connection:

        if zone_id:
            assignments = ", ".join(
                f"{field} = ?"
                for field in fields
            )

            values = list(fields.values()) + [
                zone_id
            ]

            connection.execute(
                f"""
                UPDATE zones
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                values,
            )

            return zone_id

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(
            "?"
            for _ in fields
        )

        cursor = connection.execute(
            f"""
            INSERT INTO zones ({columns})
            VALUES ({placeholders})
            """,
            list(fields.values()),
        )

        return int(cursor.lastrowid)


def list_zones(
    destination_id: int,
) -> list[dict[str, Any]]:
    """Devuelve las zonas de un destino."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM zones
            WHERE destination_id = ?
            ORDER BY prioridad_score DESC,
                     updated_at DESC
            """,
            (destination_id,),
        ).fetchall()

    return [
        _deserialize_zone(dict(row))
        for row in rows
    ]


def get_zone(
    zone_id: int,
) -> dict[str, Any] | None:
    """Recupera una zona por su ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM zones
            WHERE id = ?
            """,
            (zone_id,),
        ).fetchone()

    if row is None:
        return None

    return _deserialize_zone(dict(row))


def delete_zone(zone_id: int) -> None:
    """Elimina una zona."""

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM zones
            WHERE id = ?
            """,
            (zone_id,),
        )


def count_zones(destination_id: int) -> int:
    """Cuenta las zonas de un destino."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM zones
            WHERE destination_id = ?
            """,
            (destination_id,),
        ).fetchone()

    return int(row["total"] if row else 0)


def _deserialize_zone(
    zone: dict[str, Any],
) -> dict[str, Any]:
    """Convierte campos JSON de una zona."""

    value = zone.get("impactos")

    try:
        zone["impactos"] = (
            json.loads(value)
            if value
            else []
        )
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        zone["impactos"] = []

    return zone
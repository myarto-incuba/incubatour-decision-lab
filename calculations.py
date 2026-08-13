from typing import Any


# =========================================================
# COMPLETITUD DEL EXPEDIENTE
# =========================================================

REQUIRED_FIELDS = [
    "municipio",
    "poblacion_residente",
    "visitantes_anuales",
    "pernoctaciones_anuales",
    "plazas_alojamiento",
    "meses_temporada_alta",
    "infraestructura",
    "fragilidad_ambiental",
    "aceptacion_social",
    "gestion_flujos",
]


FIELD_LABELS = {
    "municipio": "Municipio",
    "poblacion_residente": "Población residente",
    "visitantes_anuales": "Visitantes anuales",
    "pernoctaciones_anuales": "Pernoctaciones anuales",
    "plazas_alojamiento": "Plazas de alojamiento",
    "meses_temporada_alta": "Meses de mayor afluencia",
    "infraestructura": "Capacidad de infraestructura",
    "fragilidad_ambiental": "Fragilidad ambiental",
    "aceptacion_social": "Aceptación social",
    "gestion_flujos": "Gestión de visitantes",
}


def is_missing_value(value: Any) -> bool:
    """
    Comprueba de manera segura si un valor está vacío.
    Se revisa primero el tipo para evitar comparar listas
    dentro de conjuntos.
    """

    if value is None:
        return True

    if isinstance(value, list):
        return len(value) == 0

    if isinstance(value, tuple):
        return len(value) == 0

    if isinstance(value, dict):
        return len(value) == 0

    if isinstance(value, str):
        normalized_value = value.strip().lower()

        return normalized_value in {
            "",
            "no evaluada",
            "sin información",
        }

    if isinstance(value, bool):
        return False

    if isinstance(value, (int, float)):
        return value == 0

    return False


def calculate_completeness(
    destination: dict[str, Any],
) -> tuple[int, list[str]]:
    """
    Devuelve:
    - porcentaje de completitud
    - lista de campos pendientes
    """

    missing_fields: list[str] = []
    completed_fields = 0

    for field in REQUIRED_FIELDS:
        value = destination.get(field)

        if is_missing_value(value):
            missing_fields.append(
                FIELD_LABELS.get(field, field)
            )
        else:
            completed_fields += 1

    total_fields = len(REQUIRED_FIELDS)

    if total_fields == 0:
        return 0, []

    percentage = round(
        completed_fields / total_fields * 100
    )

    return percentage, missing_fields


# =========================================================
# PRIORIDAD TERRITORIAL
# =========================================================

PRESSURE_SCORES = {
    "Baja": 20,
    "Media": 55,
    "Alta": 85,
    "Crítica": 100,
}


FRAGILITY_SCORES = {
    "Baja": 20,
    "Media": 60,
    "Alta": 100,
}


INFRASTRUCTURE_SCORES = {
    "Alta": 20,
    "Media": 60,
    "Baja": 100,
}


def calculate_zone_priority(
    presion: str,
    fragilidad: str,
    infraestructura: str,
    impacts: list[str] | None,
) -> tuple[int, str]:
    """
    Calcula la prioridad territorial de una zona,
    expresada en una escala de 0 a 100.
    """

    impacts = impacts or []

    pressure_score = PRESSURE_SCORES.get(
        presion,
        0,
    )

    fragility_score = FRAGILITY_SCORES.get(
        fragilidad,
        0,
    )

    infrastructure_score = INFRASTRUCTURE_SCORES.get(
        infraestructura,
        0,
    )

    impact_score = min(
        len(impacts) * 8,
        40,
    )

    score = round(
        pressure_score * 0.38
        + fragility_score * 0.24
        + infrastructure_score * 0.23
        + impact_score * 0.15
    )

    score = max(
        0,
        min(score, 100),
    )

    if score >= 80:
        level = "Crítica"
    elif score >= 60:
        level = "Alta"
    elif score >= 40:
        level = "Media"
    else:
        level = "Baja"

    return score, level


def generate_zone_recommendation(
    presion: str,
    fragilidad: str,
    infraestructura: str,
    impacts: list[str] | None,
) -> str:
    """
    Genera una recomendación inicial
    mediante reglas transparentes.
    """

    impacts = impacts or []
    actions: list[str] = []

    if presion in {"Alta", "Crítica"}:
        actions.append(
            "gestionar y redistribuir los flujos de visitantes"
        )

    if fragilidad == "Alta":
        actions.append(
            "establecer límites de uso y monitoreo ambiental"
        )

    if infraestructura == "Baja":
        actions.append(
            "reforzar servicios, movilidad y capacidad operativa"
        )

    if "Presión sobre la vivienda" in impacts:
        actions.append(
            "evaluar medidas sobre vivienda de uso turístico"
        )

    if (
        "Conflicto entre usos turísticos y residenciales"
        in impacts
    ):
        actions.append(
            "incorporar mecanismos de participación vecinal"
        )

    if "Ruido y molestias vecinales" in impacts:
        actions.append(
            "establecer medidas de convivencia y control de ruido"
        )

    if "Movilidad insuficiente" in impacts:
        actions.append(
            "reorganizar accesos, transporte y señalización"
        )

    if "Residuos y suciedad" in impacts:
        actions.append(
            "reforzar limpieza, recogida y gestión de residuos"
        )

    if "Erosión o deterioro ambiental" in impacts:
        actions.append(
            "proteger áreas sensibles y controlar la intensidad de uso"
        )

    if "Saturación de servicios" in impacts:
        actions.append(
            "ampliar la capacidad operativa en periodos críticos"
        )

    if not actions:
        return (
            "Mantener monitoreo periódico y reforzar "
            "la recopilación de evidencia territorial."
        )

    unique_actions = list(
        dict.fromkeys(actions)
    )

    if len(unique_actions) == 1:
        return f"Se recomienda {unique_actions[0]}."

    return (
        "Se recomienda "
        + ", ".join(unique_actions[:-1])
        + " y "
        + unique_actions[-1]
        + "."
    )


def priority_color(level: str) -> str:
    """
    Devuelve el color asociado al nivel de prioridad.
    """

    colors = {
        "Baja": "#16835A",
        "Media": "#E7A21A",
        "Alta": "#E36C2D",
        "Crítica": "#C83E4D",
    }

    return colors.get(
        level,
        "#667085",
    )
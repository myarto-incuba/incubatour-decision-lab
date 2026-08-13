from statistics import mean
from typing import Any


# =========================================================
# UTILIDADES
# =========================================================

def clamp(value: float, minimum: float = 0, maximum: float = 100) -> int:
    """
    Limita un valor a una escala de 0 a 100.
    """
    return round(max(minimum, min(value, maximum)))


def safe_divide(
    numerator: float | int | None,
    denominator: float | int | None,
) -> float:
    """
    Divide dos valores sin provocar errores.
    """
    try:
        numerator_value = float(numerator or 0)
        denominator_value = float(denominator or 0)

        if denominator_value == 0:
            return 0.0

        return numerator_value / denominator_value

    except (TypeError, ValueError):
        return 0.0


def classify_health(score: int) -> str:
    """
    Clasifica un score de salud: cuanto más alto, mejor.
    """
    if score >= 80:
        return "Sólido"

    if score >= 65:
        return "Estable"

    if score >= 50:
        return "Vulnerable"

    if score >= 35:
        return "En tensión"

    return "Crítico"


def classify_risk(score: int) -> str:
    """
    Clasifica un score de riesgo: cuanto más alto, peor.
    """
    if score >= 80:
        return "Crítico"

    if score >= 60:
        return "Alto"

    if score >= 40:
        return "Medio"

    if score >= 20:
        return "Bajo"

    return "Muy bajo"


# =========================================================
# CAPITAL TURÍSTICO
# =========================================================

def calculate_tourism_capital(
    destination: dict[str, Any],
) -> dict[str, Any]:
    """
    Calcula la presión y salud turística del destino.
    """

    population = destination.get("poblacion_residente", 0)
    visitors = destination.get("visitantes_anuales", 0)
    excursionists = destination.get("excursionistas_anuales", 0)
    overnight_stays = destination.get("pernoctaciones_anuales", 0)
    accommodation_places = destination.get("plazas_alojamiento", 0)
    peak_months = destination.get("meses_temporada_alta", []) or []

    visitors_per_resident = safe_divide(
        visitors,
        population,
    )

    total_pressure_per_resident = safe_divide(
        visitors + excursionists,
        population,
    )

    overnight_stays_per_resident = safe_divide(
        overnight_stays,
        population,
    )

    accommodation_places_per_resident = safe_divide(
        accommodation_places,
        population,
    )

    average_stay = safe_divide(
        overnight_stays,
        visitors,
    )

    peak_month_count = len(peak_months)

    # -----------------------------------------------------
    # INTENSIDAD
    # -----------------------------------------------------

    if total_pressure_per_resident >= 20:
        intensity_risk = 100
    elif total_pressure_per_resident >= 12:
        intensity_risk = 80
    elif total_pressure_per_resident >= 6:
        intensity_risk = 60
    elif total_pressure_per_resident >= 2:
        intensity_risk = 40
    else:
        intensity_risk = 20

    # -----------------------------------------------------
    # PRESIÓN ALOJATIVA
    # -----------------------------------------------------

    if accommodation_places_per_resident >= 0.20:
        accommodation_risk = 100
    elif accommodation_places_per_resident >= 0.12:
        accommodation_risk = 80
    elif accommodation_places_per_resident >= 0.06:
        accommodation_risk = 60
    elif accommodation_places_per_resident >= 0.02:
        accommodation_risk = 40
    else:
        accommodation_risk = 20

    # -----------------------------------------------------
    # CONCENTRACIÓN ESTACIONAL
    #
    # Pocos meses pico implican mayor concentración.
    # -----------------------------------------------------

    if peak_month_count == 0:
        seasonality_risk = 50
    elif peak_month_count <= 2:
        seasonality_risk = 100
    elif peak_month_count <= 4:
        seasonality_risk = 75
    elif peak_month_count <= 6:
        seasonality_risk = 50
    elif peak_month_count <= 9:
        seasonality_risk = 30
    else:
        seasonality_risk = 15

    pressure_score = clamp(
        intensity_risk * 0.55
        + accommodation_risk * 0.25
        + seasonality_risk * 0.20
    )

    health_score = clamp(
        100 - pressure_score
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if total_pressure_per_resident >= 12:
        findings.append(
            "La presión turística total es elevada en relación "
            "con la población residente."
        )

        risks.append(
            {
                "name": "Intensidad turística elevada",
                "score": intensity_risk,
                "level": classify_risk(intensity_risk),
                "evidence": (
                    f"{total_pressure_per_resident:.2f} visitantes "
                    "y excursionistas por residente."
                ),
            }
        )

    elif total_pressure_per_resident >= 6:
        findings.append(
            "La intensidad turística es significativa para el tamaño "
            "del municipio."
        )
    else:
        findings.append(
            "La intensidad turística general se mantiene en niveles moderados."
        )

    if 0 < peak_month_count <= 4:
        findings.append(
            "La demanda presenta una concentración estacional relevante."
        )

        risks.append(
            {
                "name": "Concentración estacional",
                "score": seasonality_risk,
                "level": classify_risk(seasonality_risk),
                "evidence": (
                    f"La temporada alta se concentra en "
                    f"{peak_month_count} meses."
                ),
            }
        )

        opportunities.append(
            "Desarrollar productos y eventos capaces de activar "
            "la temporada media y baja."
        )

    if accommodation_places_per_resident >= 0.06:
        findings.append(
            "La capacidad alojativa tiene un peso relevante "
            "sobre la estructura urbana del destino."
        )

    if visitors > 0 and average_stay < 2:
        findings.append(
            "La estancia media es reducida y puede estar generando "
            "alta rotación de visitantes."
        )

        opportunities.append(
            "Incrementar la estancia media mediante productos combinados "
            "y experiencias de mayor duración."
        )

    return {
        "name": "Capital turístico",
        "health_score": health_score,
        "pressure_score": pressure_score,
        "status": classify_health(health_score),
        "risk_level": classify_risk(pressure_score),
        "metrics": {
            "visitors_per_resident": round(visitors_per_resident, 2),
            "total_pressure_per_resident": round(
                total_pressure_per_resident,
                2,
            ),
            "overnight_stays_per_resident": round(
                overnight_stays_per_resident,
                2,
            ),
            "accommodation_places_per_resident": round(
                accommodation_places_per_resident,
                3,
            ),
            "average_stay": round(average_stay, 2),
            "peak_month_count": peak_month_count,
        },
        "findings": findings,
        "risks": risks,
        "opportunities": opportunities,
    }


# =========================================================
# CAPITAL TERRITORIAL
# =========================================================

def calculate_territorial_capital(
    zones: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula salud, riesgo y concentración territorial
    a partir de las zonas registradas.
    """

    if not zones:
        return {
            "name": "Capital territorial",
            "health_score": None,
            "pressure_score": None,
            "status": "Sin evaluar",
            "risk_level": "Sin evaluar",
            "metrics": {
                "total_zones": 0,
                "critical_zones": 0,
                "high_priority_zones": 0,
                "average_priority": 0,
                "territorial_concentration": 0,
            },
            "findings": [
                "Todavía no existen zonas suficientes para evaluar "
                "la dimensión territorial."
            ],
            "risks": [],
            "opportunities": [],
        }

    priority_scores = [
        int(zone.get("prioridad_score", 0) or 0)
        for zone in zones
    ]

    total_zones = len(zones)

    critical_zones = sum(
        zone.get("prioridad_nivel") == "Crítica"
        for zone in zones
    )

    high_priority_zones = sum(
        zone.get("prioridad_nivel") in {"Alta", "Crítica"}
        for zone in zones
    )

    average_priority = round(
        mean(priority_scores)
    ) if priority_scores else 0

    territorial_concentration = round(
        high_priority_zones / total_zones * 100
    )

    pressure_score = clamp(
        average_priority * 0.65
        + territorial_concentration * 0.35
    )

    health_score = clamp(
        100 - pressure_score
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if critical_zones > 0:
        findings.append(
            f"Se identificaron {critical_zones} zonas con prioridad crítica."
        )

        risks.append(
            {
                "name": "Zonas críticas",
                "score": min(100, 70 + critical_zones * 10),
                "level": "Crítico",
                "evidence": (
                    f"{critical_zones} de {total_zones} zonas "
                    "requieren intervención prioritaria."
                ),
            }
        )

    if territorial_concentration >= 60:
        findings.append(
            "La presión turística se concentra en una proporción elevada "
            "de las zonas analizadas."
        )
    elif territorial_concentration >= 30:
        findings.append(
            "La presión no es homogénea y se concentra en determinadas zonas."
        )
    else:
        findings.append(
            "La presión territorial se encuentra relativamente distribuida."
        )

    if high_priority_zones > 0:
        opportunities.append(
            "Redistribuir flujos hacia zonas con menor intensidad "
            "y capacidad disponible."
        )

    low_pressure_zones = [
        zone.get("nombre", "")
        for zone in zones
        if zone.get("prioridad_nivel") == "Baja"
    ]

    if low_pressure_zones:
        opportunities.append(
            "Evaluar productos y recorridos alternativos en "
            + ", ".join(low_pressure_zones[:3])
            + "."
        )

    return {
        "name": "Capital territorial",
        "health_score": health_score,
        "pressure_score": pressure_score,
        "status": classify_health(health_score),
        "risk_level": classify_risk(pressure_score),
        "metrics": {
            "total_zones": total_zones,
            "critical_zones": critical_zones,
            "high_priority_zones": high_priority_zones,
            "average_priority": average_priority,
            "territorial_concentration": territorial_concentration,
        },
        "findings": findings,
        "risks": risks,
        "opportunities": opportunities,
    }
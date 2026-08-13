from typing import Any

from context_repository import (
    calculate_context_completeness,
    get_context,
)
from engine.capitals import (
    calculate_territorial_capital,
    calculate_tourism_capital,
)
from engine.context_capitals import (
    calculate_context_capitals,
)


# =========================================================
# UTILIDADES
# =========================================================

def clamp(
    value: float,
    minimum: float = 0,
    maximum: float = 100,
) -> int:
    """
    Limita un valor a una escala de 0 a 100.
    """

    return round(
        max(
            minimum,
            min(value, maximum),
        )
    )


def has_value(value: Any) -> bool:
    """
    Comprueba si un dato puede considerarse disponible.
    """

    if value is None:
        return False

    if isinstance(value, str):
        return bool(
            value.strip()
            and value.strip() != "Sin evaluar"
        )

    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0

    if isinstance(value, (int, float)):
        return value != 0

    return True


def classify_risk(
    score: int,
) -> str:
    """
    Clasifica un índice de riesgo.
    Cuanto más alto, mayor riesgo.
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
# CONFIANZA DEL DIAGNÓSTICO
# =========================================================

def calculate_confidence(
    destination: dict[str, Any],
    zones: list[dict[str, Any]],
    context: dict[str, Any] | None,
) -> int:
    """
    Calcula el nivel de confianza del diagnóstico.

    La confianza depende de:
    - datos cuantitativos disponibles;
    - trazabilidad de las fuentes;
    - contexto cualitativo completado;
    - zonas territoriales registradas.
    """

    quantitative_fields = [
        "poblacion_residente",
        "visitantes_anuales",
        "pernoctaciones_anuales",
        "plazas_alojamiento",
        "meses_temporada_alta",
    ]

    quantitative_available = sum(
        has_value(
            destination.get(field)
        )
        for field in quantitative_fields
    )

    quantitative_score = (
        quantitative_available
        / len(quantitative_fields)
        * 45
    )

    source_fields = [
        "fuente_datos",
        "evidencia_inicial",
    ]

    source_available = sum(
        has_value(
            destination.get(field)
        )
        for field in source_fields
    )

    source_score = (
        source_available
        / len(source_fields)
        * 15
    )

    context_completeness = (
        calculate_context_completeness(
            context
        )
    )

    context_score = (
        context_completeness
        / 100
        * 25
    )

    zone_score = min(
        len(zones) * 5,
        15,
    )

    return clamp(
        quantitative_score
        + source_score
        + context_score
        + zone_score
    )


# =========================================================
# ETAPA DEL DESTINO
# =========================================================

def classify_destination_stage(
    health_score: int,
    risk_score: int,
) -> str:
    """
    Clasifica el estado estratégico del destino.
    """

    if health_score >= 80 and risk_score < 30:
        return "Destino equilibrado"

    if health_score >= 65 and risk_score < 50:
        return "Destino consolidado"

    if health_score >= 50:
        return "Destino consolidado con tensiones"

    if health_score >= 35:
        return "Destino en tensión"

    return "Destino crítico"


# =========================================================
# CONSOLIDACIÓN DE RIESGOS
# =========================================================

def build_main_risks(
    capitals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Consolida los riesgos generados por todos los capitales.
    """

    risks: list[dict[str, Any]] = []

    for capital in capitals:
        for risk in capital.get(
            "risks",
            [],
        ):
            risks.append(
                {
                    **risk,
                    "capital": capital.get(
                        "name",
                        "Capital sin identificar",
                    ),
                }
            )

    unique_risks: dict[str, dict[str, Any]] = {}

    for risk in risks:
        risk_name = risk.get(
            "name",
            "Riesgo",
        )

        existing = unique_risks.get(
            risk_name
        )

        if (
            existing is None
            or risk.get("score", 0)
            > existing.get("score", 0)
        ):
            unique_risks[
                risk_name
            ] = risk

    return sorted(
        unique_risks.values(),
        key=lambda risk: risk.get(
            "score",
            0,
        ),
        reverse=True,
    )


# =========================================================
# CONSOLIDACIÓN DE OPORTUNIDADES
# =========================================================

def build_main_opportunities(
    capitals: list[dict[str, Any]],
) -> list[str]:
    """
    Consolida oportunidades sin duplicarlas.
    """

    opportunities: list[str] = []

    for capital in capitals:
        opportunities.extend(
            capital.get(
                "opportunities",
                [],
            )
        )

    return list(
        dict.fromkeys(
            opportunities
        )
    )


# =========================================================
# FORTALEZAS
# =========================================================

def build_main_strengths(
    capitals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Identifica los capitales mejor posicionados.
    """

    strengths: list[dict[str, Any]] = []

    for capital in capitals:
        health_score = capital.get(
            "health_score"
        )

        if (
            health_score is not None
            and health_score >= 65
        ):
            strengths.append(
                {
                    "name": capital.get(
                        "name",
                        "Capital",
                    ),
                    "score": health_score,
                    "status": capital.get(
                        "status",
                        "Estable",
                    ),
                    "evidence": (
                        capital.get(
                            "findings",
                            [],
                        )[0]
                        if capital.get(
                            "findings"
                        )
                        else (
                            "La dimensión presenta "
                            "una valoración favorable."
                        )
                    ),
                }
            )

    return sorted(
        strengths,
        key=lambda strength: strength[
            "score"
        ],
        reverse=True,
    )


# =========================================================
# PÓKER DE AS
# =========================================================

def build_poker_as(
    capitals: list[dict[str, Any]],
    main_risks: list[dict[str, Any]],
    main_opportunities: list[str],
) -> dict[str, list[str]]:
    """
    Genera la primera interpretación automática
    de Analiza, Aprende, Adapta y Actúa.
    """

    analiza: list[str] = []

    for capital in capitals:
        analiza.extend(
            capital.get(
                "findings",
                [],
            )
        )

    analiza = list(
        dict.fromkeys(
            analiza
        )
    )[:6]

    aprende: list[str] = []

    high_pressure_capitals = [
        capital
        for capital in capitals
        if (
            capital.get(
                "pressure_score"
            )
            is not None
            and capital[
                "pressure_score"
            ] >= 60
        )
    ]

    if len(high_pressure_capitals) >= 2:
        capital_names = ", ".join(
            capital["name"]
            .replace(
                "Capital ",
                "",
            )
            .lower()
            for capital
            in high_pressure_capitals[:3]
        )

        aprende.append(
            "La presión no responde a una sola causa: "
            f"se combinan factores de carácter {capital_names}."
        )

    tourism = next(
        (
            capital
            for capital in capitals
            if capital.get("name")
            == "Capital turístico"
        ),
        None,
    )

    territorial = next(
        (
            capital
            for capital in capitals
            if capital.get("name")
            == "Capital territorial"
        ),
        None,
    )

    social = next(
        (
            capital
            for capital in capitals
            if capital.get("name")
            == "Capital social"
        ),
        None,
    )

    institutional = next(
        (
            capital
            for capital in capitals
            if capital.get("name")
            == "Capital institucional"
        ),
        None,
    )

    if (
        tourism
        and tourism.get(
            "pressure_score",
            0,
        ) >= 60
    ):
        aprende.append(
            "El volumen y la concentración temporal "
            "de la demanda generan una presión significativa "
            "para el tamaño del municipio."
        )

    if (
        territorial
        and territorial.get(
            "metrics",
            {},
        ).get(
            "territorial_concentration",
            0,
        ) >= 30
    ):
        aprende.append(
            "La presión no se distribuye de forma homogénea: "
            "existen focos que requieren medidas diferenciadas."
        )

    if (
        social
        and social.get(
            "pressure_score"
        )
        is not None
        and social[
            "pressure_score"
        ] >= 60
    ):
        aprende.append(
            "Las tensiones sociales pueden convertirse "
            "en una limitación estratégica si no se incorporan "
            "mecanismos de participación y convivencia."
        )

    if (
        institutional
        and institutional.get(
            "health_score"
        )
        is not None
        and institutional[
            "health_score"
        ] >= 70
    ):
        aprende.append(
            "El destino dispone de capacidad institucional "
            "para implementar medidas correctivas y monitorear resultados."
        )

    adapta = main_opportunities[:6]

    actua: list[str] = []

    for risk in main_risks[:5]:
        actua.append(
            f"Atender {risk.get('name', 'el riesgo').lower()}: "
            f"{risk.get('evidence', 'requiere validación técnica')}."
        )

    if not actua:
        actua.append(
            "Completar las dimensiones pendientes "
            "y mantener monitoreo periódico."
        )

    return {
        "analiza": analiza,
        "aprende": aprende[:5],
        "adapta": adapta,
        "actua": actua,
    }


# =========================================================
# RESUMEN EJECUTIVO
# =========================================================

def build_executive_summary(
    destination_name: str,
    health_score: int,
    risk_level: str,
    strongest_capital: dict[str, Any] | None,
    weakest_capital: dict[str, Any] | None,
) -> str:
    """
    Genera una lectura ejecutiva general.
    """

    if weakest_capital:
        weakness = weakest_capital[
            "name"
        ].replace(
            "Capital ",
            "",
        ).lower()
    else:
        weakness = "información pendiente"

    if strongest_capital:
        strength = strongest_capital[
            "name"
        ].replace(
            "Capital ",
            "",
        ).lower()
    else:
        strength = "capacidad todavía no evaluada"

    return (
        f"{destination_name} presenta una salud global de "
        f"{health_score}/100 y un nivel de riesgo {risk_level.lower()}. "
        f"La principal fortaleza se encuentra en el ámbito {strength}, "
        f"mientras que la dimensión que requiere mayor atención "
        f"es la relacionada con {weakness}. "
        "La prioridad debe centrarse en reducir los factores de presión "
        "sin debilitar las capacidades que actualmente sostienen al destino."
    )


# =========================================================
# FUNCIÓN CENTRAL
# =========================================================

def analyze_destination(
    destination: dict[str, Any],
    zones: list[dict[str, Any]] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Función central del Incubatour Decision Lab.

    Integra:
    - Capital turístico.
    - Capital territorial.
    - Capital social.
    - Capital institucional.
    - Capital reputacional.
    - Capital de resiliencia.
    """

    zones = zones or []

    destination_id = destination.get(
        "id"
    )

    if (
        context is None
        and destination_id is not None
    ):
        context = get_context(
            int(destination_id)
        )

    tourism_capital = (
        calculate_tourism_capital(
            destination
        )
    )

    territorial_capital = (
        calculate_territorial_capital(
            zones
        )
    )

    context_capitals = (
        calculate_context_capitals(
            context
        )
    )

    social_capital = context_capitals[
        "social_capital"
    ]

    institutional_capital = (
        context_capitals[
            "institutional_capital"
        ]
    )

    reputational_capital = (
        context_capitals[
            "reputational_capital"
        ]
    )

    resilience_capital = (
        context_capitals[
            "resilience_capital"
        ]
    )

    all_capitals = [
        tourism_capital,
        territorial_capital,
        social_capital,
        institutional_capital,
        reputational_capital,
        resilience_capital,
    ]

    evaluated_capitals = [
        capital
        for capital in all_capitals
        if capital.get(
            "health_score"
        )
        is not None
    ]

    health_scores = [
        capital[
            "health_score"
        ]
        for capital in evaluated_capitals
    ]

    pressure_scores = [
        capital[
            "pressure_score"
        ]
        for capital in evaluated_capitals
        if capital.get(
            "pressure_score"
        )
        is not None
    ]

    destination_health = (
        round(
            sum(health_scores)
            / len(health_scores)
        )
        if health_scores
        else 0
    )

    global_risk_score = (
        round(
            sum(pressure_scores)
            / len(pressure_scores)
        )
        if pressure_scores
        else 0
    )

    risk_level = classify_risk(
        global_risk_score
    )

    stage = classify_destination_stage(
        destination_health,
        global_risk_score,
    )

    confidence = calculate_confidence(
        destination,
        zones,
        context,
    )

    main_risks = build_main_risks(
        evaluated_capitals
    )

    main_opportunities = (
        build_main_opportunities(
            evaluated_capitals
        )
    )

    main_strengths = build_main_strengths(
        evaluated_capitals
    )

    ordered_capitals = sorted(
        evaluated_capitals,
        key=lambda capital: capital[
            "health_score"
        ],
        reverse=True,
    )

    strongest_capital = (
        ordered_capitals[0]
        if ordered_capitals
        else None
    )

    weakest_capital = (
        ordered_capitals[-1]
        if ordered_capitals
        else None
    )

    poker_as = build_poker_as(
        evaluated_capitals,
        main_risks,
        main_opportunities,
    )

    destination_name = destination.get(
        "municipio",
        "El destino",
    )

    executive_summary = (
        build_executive_summary(
            destination_name,
            destination_health,
            risk_level,
            strongest_capital,
            weakest_capital,
        )
    )

    return {
        "destination_health": destination_health,
        "global_risk_score": global_risk_score,
        "stage": stage,
        "risk_level": risk_level,
        "confidence": confidence,

        "capitals_evaluated": len(
            evaluated_capitals
        ),
        "capitals_total": 6,

        "tourism_capital": tourism_capital,
        "territorial_capital": territorial_capital,
        "social_capital": social_capital,
        "institutional_capital": institutional_capital,
        "reputational_capital": reputational_capital,
        "resilience_capital": resilience_capital,

        "capitals": {
            "tourism": tourism_capital,
            "territorial": territorial_capital,
            "social": social_capital,
            "institutional": institutional_capital,
            "reputational": reputational_capital,
            "resilience": resilience_capital,
        },

        "main_risks": main_risks,
        "main_opportunities": main_opportunities,
        "main_strengths": main_strengths,

        "strongest_capital": strongest_capital,
        "weakest_capital": weakest_capital,

        "poker_as": poker_as,
        "executive_summary": executive_summary,
    }
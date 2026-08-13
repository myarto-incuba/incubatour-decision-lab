from typing import Any


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


def classify_health(score: int | None) -> str:
    """
    Clasifica un score de salud.
    Cuanto más alto, mejor.
    """

    if score is None:
        return "Sin evaluar"

    if score >= 80:
        return "Sólido"

    if score >= 65:
        return "Estable"

    if score >= 50:
        return "Vulnerable"

    if score >= 35:
        return "En tensión"

    return "Crítico"


def classify_risk(score: int | None) -> str:
    """
    Clasifica un score de riesgo.
    Cuanto más alto, peor.
    """

    if score is None:
        return "Sin evaluar"

    if score >= 80:
        return "Crítico"

    if score >= 60:
        return "Alto"

    if score >= 40:
        return "Medio"

    if score >= 20:
        return "Bajo"

    return "Muy bajo"


def is_evaluated(value: Any) -> bool:
    """
    Comprueba si una respuesta cualitativa fue evaluada.
    """

    if value is None:
        return False

    if isinstance(value, str):
        return bool(
            value.strip()
            and value.strip() != "Sin evaluar"
        )

    if isinstance(value, list):
        return len(value) > 0

    return True


def average_scores(
    values: list[int | None],
) -> int | None:
    """
    Calcula el promedio únicamente con valores evaluados.
    """

    valid_values = [
        value
        for value in values
        if value is not None
    ]

    if not valid_values:
        return None

    return clamp(
        sum(valid_values)
        / len(valid_values)
    )


def build_capital_result(
    name: str,
    health_score: int | None,
    metrics: dict[str, Any],
    findings: list[str],
    risks: list[dict[str, Any]],
    opportunities: list[str],
    evaluated_variables: int,
    total_variables: int,
) -> dict[str, Any]:
    """
    Construye una salida homogénea para cada capital.
    """

    pressure_score = (
        None
        if health_score is None
        else clamp(100 - health_score)
    )

    completeness = round(
        evaluated_variables
        / total_variables
        * 100
    )

    return {
        "name": name,
        "health_score": health_score,
        "pressure_score": pressure_score,
        "status": classify_health(health_score),
        "risk_level": classify_risk(pressure_score),
        "completeness": completeness,
        "metrics": metrics,
        "findings": findings,
        "risks": risks,
        "opportunities": opportunities,
    }


# =========================================================
# CAPITAL SOCIAL
# =========================================================

SOCIAL_RELATION_SCORES = {
    "Muy positiva": 100,
    "Positiva": 82,
    "Neutral": 62,
    "Tensa": 35,
    "Muy conflictiva": 12,
}

SOCIAL_CONFLICT_SCORES = {
    "No existen conflictos visibles": 100,
    "Existen casos aislados": 75,
    "Existen tensiones recurrentes": 38,
    "Existen protestas o conflictos organizados": 10,
}

SOCIAL_PARTICIPATION_SCORES = {
    "Alta y permanente": 100,
    "Existe, pero es puntual": 72,
    "Limitada": 42,
    "Inexistente": 12,
}

SOCIAL_IMPACT_WEIGHTS = {
    "Acceso y precio de la vivienda": 18,
    "Ruido y convivencia": 12,
    "Congestión del espacio público": 12,
    "Pérdida del comercio local": 10,
    "Aumento del coste de vida": 12,
    "Pérdida de identidad": 12,
    "Empleo precario o estacional": 8,
    "Distribución desigual de beneficios": 10,
    "Presión ambiental": 10,
}


def calculate_social_capital(
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Evalúa convivencia, aceptación social y participación.
    """

    context = context or {}

    relation = context.get(
        "relacion_residentes_visitantes"
    )

    conflicts = context.get(
        "conflictos_turisticos"
    )

    participation = context.get(
        "participacion_ciudadana"
    )

    concerns = context.get(
        "preocupaciones_sociales",
        [],
    ) or []

    relation_score = SOCIAL_RELATION_SCORES.get(
        relation
    )

    conflict_score = SOCIAL_CONFLICT_SCORES.get(
        conflicts
    )

    participation_score = SOCIAL_PARTICIPATION_SCORES.get(
        participation
    )

    relevant_concerns = [
        concern
        for concern in concerns
        if concern
        != "No se identifican preocupaciones relevantes"
    ]

    if not concerns:
        concern_score = None
    elif not relevant_concerns:
        concern_score = 100
    else:
        concern_pressure = min(
            100,
            sum(
                SOCIAL_IMPACT_WEIGHTS.get(
                    concern,
                    8,
                )
                for concern in relevant_concerns
            ),
        )

        concern_score = clamp(
            100 - concern_pressure
        )

    health_score = average_scores(
        [
            relation_score,
            conflict_score,
            participation_score,
            concern_score,
        ]
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if relation in {
        "Tensa",
        "Muy conflictiva",
    }:
        findings.append(
            "La relación entre residentes y visitantes "
            "presenta señales claras de tensión."
        )

        risks.append(
            {
                "name": "Deterioro de la convivencia",
                "score": clamp(
                    100
                    - (
                        relation_score
                        or 0
                    )
                ),
                "level": classify_risk(
                    clamp(
                        100
                        - (
                            relation_score
                            or 0
                        )
                    )
                ),
                "evidence": (
                    "La relación residentes–visitantes "
                    f"fue valorada como {relation.lower()}."
                ),
            }
        )

    elif relation in {
        "Muy positiva",
        "Positiva",
    }:
        findings.append(
            "La relación entre residentes y visitantes "
            "constituye una fortaleza del destino."
        )

    if conflicts in {
        "Existen tensiones recurrentes",
        "Existen protestas o conflictos organizados",
    }:
        findings.append(
            "Existen conflictos sociales vinculados "
            "con la actividad turística."
        )

    if (
        "Acceso y precio de la vivienda"
        in relevant_concerns
    ):
        risks.append(
            {
                "name": "Presión social sobre la vivienda",
                "score": 82,
                "level": "Crítico",
                "evidence": (
                    "La vivienda aparece como una de "
                    "las principales preocupaciones ciudadanas."
                ),
            }
        )

    if participation in {
        "Limitada",
        "Inexistente",
    }:
        risks.append(
            {
                "name": "Baja participación ciudadana",
                "score": (
                    60
                    if participation == "Limitada"
                    else 85
                ),
                "level": (
                    "Alto"
                    if participation == "Limitada"
                    else "Crítico"
                ),
                "evidence": (
                    "La participación ciudadana en las "
                    "decisiones turísticas es insuficiente."
                ),
            }
        )

        opportunities.append(
            "Crear mecanismos permanentes de escucha, "
            "participación y devolución de resultados."
        )

    if relevant_concerns:
        findings.append(
            f"Se identificaron {len(relevant_concerns)} "
            "preocupaciones sociales relevantes."
        )

    if (
        participation_score is not None
        and participation_score >= 70
    ):
        opportunities.append(
            "Aprovechar los mecanismos de participación "
            "existentes para validar medidas de gestión."
        )

    evaluated_variables = sum(
        [
            is_evaluated(relation),
            is_evaluated(conflicts),
            is_evaluated(participation),
            bool(concerns),
        ]
    )

    return build_capital_result(
        name="Capital social",
        health_score=health_score,
        metrics={
            "relationship": relation or "Sin evaluar",
            "conflict_level": conflicts or "Sin evaluar",
            "participation": participation or "Sin evaluar",
            "concerns_count": len(
                relevant_concerns
            ),
        },
        findings=findings,
        risks=risks,
        opportunities=opportunities,
        evaluated_variables=evaluated_variables,
        total_variables=4,
    )


# =========================================================
# CAPITAL INSTITUCIONAL
# =========================================================

YES_NO_HEALTH_SCORES = {
    "Sí": 100,
    "Parcialmente": 58,
    "No": 12,
}

TEAM_HEALTH_SCORES = {
    "Equipo consolidado y especializado": 100,
    "Equipo suficiente, pero limitado": 72,
    "Equipo reducido": 38,
    "No existe un equipo específico": 10,
}

COORDINATION_HEALTH_SCORES = {
    "Alta y estructurada": 100,
    "Frecuente, pero informal": 72,
    "Puntual": 42,
    "Inexistente": 10,
}


def calculate_institutional_capital(
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Evalúa planificación, datos, equipo y gobernanza.
    """

    context = context or {}

    strategy = context.get(
        "estrategia_turistica"
    )

    observatory = context.get(
        "observatorio_turistico"
    )

    team = context.get(
        "equipo_tecnico"
    )

    coordination = context.get(
        "coordinacion_publico_privada"
    )

    strategy_score = YES_NO_HEALTH_SCORES.get(
        strategy
    )

    observatory_score = YES_NO_HEALTH_SCORES.get(
        observatory
    )

    team_score = TEAM_HEALTH_SCORES.get(
        team
    )

    coordination_score = COORDINATION_HEALTH_SCORES.get(
        coordination
    )

    health_score = average_scores(
        [
            strategy_score,
            observatory_score,
            team_score,
            coordination_score,
        ]
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if strategy == "Sí":
        findings.append(
            "El destino dispone de una estrategia turística vigente."
        )
    elif strategy == "No":
        risks.append(
            {
                "name": "Ausencia de estrategia turística",
                "score": 88,
                "level": "Crítico",
                "evidence": (
                    "El destino no dispone de una estrategia "
                    "turística vigente."
                ),
            }
        )

        opportunities.append(
            "Diseñar una estrategia turística con objetivos, "
            "indicadores, responsables y calendario."
        )

    if observatory == "Sí":
        findings.append(
            "Existe capacidad estable para monitorear "
            "la evolución de la actividad turística."
        )
    elif observatory in {
        "Parcialmente",
        "No",
    }:
        risks.append(
            {
                "name": "Debilidad del sistema de datos",
                "score": (
                    55
                    if observatory == "Parcialmente"
                    else 82
                ),
                "level": (
                    "Medio"
                    if observatory == "Parcialmente"
                    else "Crítico"
                ),
                "evidence": (
                    "El sistema de indicadores u observatorio "
                    "es insuficiente para una gestión continua."
                ),
            }
        )

        opportunities.append(
            "Implantar un sistema estable de indicadores "
            "y protocolos de actualización."
        )

    if team in {
        "Equipo reducido",
        "No existe un equipo específico",
    }:
        risks.append(
            {
                "name": "Capacidad técnica limitada",
                "score": (
                    65
                    if team == "Equipo reducido"
                    else 90
                ),
                "level": (
                    "Alto"
                    if team == "Equipo reducido"
                    else "Crítico"
                ),
                "evidence": (
                    "El equipo disponible puede no ser "
                    "suficiente para ejecutar las medidas."
                ),
            }
        )

    if coordination in {
        "Puntual",
        "Inexistente",
    }:
        findings.append(
            "La coordinación público-privada requiere fortalecimiento."
        )

        opportunities.append(
            "Formalizar una mesa de gobernanza público-privada "
            "con seguimiento periódico."
        )

    if (
        health_score is not None
        and health_score >= 75
    ):
        findings.append(
            "El destino dispone de una base institucional "
            "favorable para implementar medidas correctivas."
        )

    evaluated_variables = sum(
        [
            is_evaluated(strategy),
            is_evaluated(observatory),
            is_evaluated(team),
            is_evaluated(coordination),
        ]
    )

    return build_capital_result(
        name="Capital institucional",
        health_score=health_score,
        metrics={
            "strategy": strategy or "Sin evaluar",
            "observatory": observatory or "Sin evaluar",
            "technical_team": team or "Sin evaluar",
            "coordination": coordination or "Sin evaluar",
        },
        findings=findings,
        risks=risks,
        opportunities=opportunities,
        evaluated_variables=evaluated_variables,
        total_variables=4,
    )


# =========================================================
# CAPITAL REPUTACIONAL
# =========================================================

REPUTATION_HEALTH_SCORES = {
    "Muy positiva": 100,
    "Positiva": 82,
    "Mixta": 58,
    "Deteriorada": 30,
    "En crisis": 8,
}

RECOVERY_HEALTH_SCORES = {
    "Muy alta": 100,
    "Alta": 82,
    "Media": 58,
    "Baja": 30,
    "Muy baja": 10,
}

POSITIONING_HEALTH_SCORES = {
    "Emergente": 68,
    "En crecimiento": 78,
    "Consolidado": 88,
    "Premium": 92,
    "Masificado": 32,
    "En recuperación": 52,
    "En reposicionamiento": 62,
}

REPUTATIONAL_EVENT_WEIGHTS = {
    "Desastres naturales": 18,
    "Incendios": 16,
    "Inundaciones": 16,
    "Sequía o falta de agua": 16,
    "Crisis sanitaria": 15,
    "Inseguridad": 22,
    "Accidentes relevantes": 14,
    "Protestas ciudadanas": 18,
    "Cobertura mediática negativa": 18,
    "Crisis política o institucional": 16,
    "Saturación o masificación": 20,
}


def calculate_reputational_capital(
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Evalúa imagen, posicionamiento y capacidad de recuperación.
    """

    context = context or {}

    positioning = context.get(
        "posicionamiento_destino"
    )

    reputation = context.get(
        "reputacion_actual"
    )

    recovery = context.get(
        "recuperacion_imagen"
    )

    events = context.get(
        "eventos_reputacionales",
        [],
    ) or []

    positioning_score = POSITIONING_HEALTH_SCORES.get(
        positioning
    )

    reputation_score = REPUTATION_HEALTH_SCORES.get(
        reputation
    )

    recovery_score = RECOVERY_HEALTH_SCORES.get(
        recovery
    )

    relevant_events = [
        event
        for event in events
        if event != "Ninguno"
    ]

    if not events:
        event_score = None
    elif not relevant_events:
        event_score = 100
    else:
        event_pressure = min(
            100,
            sum(
                REPUTATIONAL_EVENT_WEIGHTS.get(
                    event,
                    12,
                )
                for event in relevant_events
            ),
        )

        event_score = clamp(
            100 - event_pressure
        )

    health_score = average_scores(
        [
            positioning_score,
            reputation_score,
            recovery_score,
            event_score,
        ]
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if reputation in {
        "Muy positiva",
        "Positiva",
    }:
        findings.append(
            "El destino mantiene una reputación turística favorable."
        )

    if positioning == "Masificado":
        risks.append(
            {
                "name": "Posicionamiento asociado a masificación",
                "score": 82,
                "level": "Crítico",
                "evidence": (
                    "El destino se percibe actualmente "
                    "como un destino masificado."
                ),
            }
        )

        opportunities.append(
            "Reposicionar la comunicación hacia calidad, "
            "dispersión territorial y experiencias responsables."
        )

    if reputation in {
        "Deteriorada",
        "En crisis",
    }:
        risks.append(
            {
                "name": "Deterioro reputacional",
                "score": (
                    72
                    if reputation == "Deteriorada"
                    else 95
                ),
                "level": (
                    "Alto"
                    if reputation == "Deteriorada"
                    else "Crítico"
                ),
                "evidence": (
                    f"La reputación actual fue valorada como "
                    f"{reputation.lower()}."
                ),
            }
        )

    if relevant_events:
        findings.append(
            f"Se registraron {len(relevant_events)} acontecimientos "
            "con potencial impacto reputacional."
        )

    if (
        recovery_score is not None
        and recovery_score >= 80
    ):
        findings.append(
            "El destino muestra una capacidad elevada "
            "para proteger o recuperar su imagen."
        )

        opportunities.append(
            "Aprovechar la fortaleza de marca para comunicar "
            "las medidas de gestión y sostenibilidad."
        )

    if recovery in {
        "Baja",
        "Muy baja",
    }:
        risks.append(
            {
                "name": "Baja capacidad de recuperación de imagen",
                "score": (
                    70
                    if recovery == "Baja"
                    else 90
                ),
                "level": (
                    "Alto"
                    if recovery == "Baja"
                    else "Crítico"
                ),
                "evidence": (
                    "La capacidad de respuesta ante una crisis "
                    "reputacional es limitada."
                ),
            }
        )

    evaluated_variables = sum(
        [
            is_evaluated(positioning),
            is_evaluated(reputation),
            is_evaluated(recovery),
            bool(events),
        ]
    )

    return build_capital_result(
        name="Capital reputacional",
        health_score=health_score,
        metrics={
            "positioning": positioning or "Sin evaluar",
            "reputation": reputation or "Sin evaluar",
            "recovery_capacity": recovery or "Sin evaluar",
            "events_count": len(
                relevant_events
            ),
        },
        findings=findings,
        risks=risks,
        opportunities=opportunities,
        evaluated_variables=evaluated_variables,
        total_variables=4,
    )


# =========================================================
# CAPITAL DE RESILIENCIA
# =========================================================

DIVERSIFICATION_HEALTH_SCORES = {
    "Muy diversificada": 100,
    "Diversificada": 82,
    "Moderadamente concentrada": 52,
    "Muy dependiente de pocos mercados": 18,
}

DEPENDENCY_HEALTH_SCORES = {
    "Baja": 100,
    "Media": 68,
    "Alta": 35,
    "Muy alta": 12,
}

REDISTRIBUTION_HEALTH_SCORES = {
    "Alta": 100,
    "Media": 65,
    "Baja": 30,
    "Inexistente": 8,
}


def calculate_resilience_capital(
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Evalúa preparación, diversificación y adaptabilidad.
    """

    context = context or {}

    crisis_plan = context.get(
        "plan_crisis"
    )

    diversification = context.get(
        "diversificacion_mercados"
    )

    seasonal_dependency = context.get(
        "dependencia_estacional"
    )

    redistribution = context.get(
        "capacidad_redistribucion"
    )

    crisis_score = YES_NO_HEALTH_SCORES.get(
        crisis_plan
    )

    diversification_score = DIVERSIFICATION_HEALTH_SCORES.get(
        diversification
    )

    dependency_score = DEPENDENCY_HEALTH_SCORES.get(
        seasonal_dependency
    )

    redistribution_score = REDISTRIBUTION_HEALTH_SCORES.get(
        redistribution
    )

    health_score = average_scores(
        [
            crisis_score,
            diversification_score,
            dependency_score,
            redistribution_score,
        ]
    )

    findings: list[str] = []
    risks: list[dict[str, Any]] = []
    opportunities: list[str] = []

    if crisis_plan == "Sí":
        findings.append(
            "El destino dispone de un plan formal "
            "de crisis o contingencia turística."
        )
    elif crisis_plan in {
        "Parcialmente",
        "No",
    }:
        risks.append(
            {
                "name": "Preparación insuficiente ante crisis",
                "score": (
                    55
                    if crisis_plan == "Parcialmente"
                    else 88
                ),
                "level": (
                    "Medio"
                    if crisis_plan == "Parcialmente"
                    else "Crítico"
                ),
                "evidence": (
                    "El plan de contingencia turística "
                    "es incompleto o inexistente."
                ),
            }
        )

        opportunities.append(
            "Diseñar un protocolo de crisis con responsables, "
            "escenarios, comunicación y recuperación."
        )

    if diversification in {
        "Moderadamente concentrada",
        "Muy dependiente de pocos mercados",
    }:
        risks.append(
            {
                "name": "Dependencia de mercados o segmentos",
                "score": (
                    58
                    if diversification
                    == "Moderadamente concentrada"
                    else 88
                ),
                "level": (
                    "Medio"
                    if diversification
                    == "Moderadamente concentrada"
                    else "Crítico"
                ),
                "evidence": (
                    "La estructura de demanda presenta "
                    "una diversificación insuficiente."
                ),
            }
        )

        opportunities.append(
            "Diversificar mercados, segmentos y canales "
            "para reducir la exposición a cambios externos."
        )

    if seasonal_dependency in {
        "Alta",
        "Muy alta",
    }:
        findings.append(
            "La elevada dependencia estacional reduce "
            "la capacidad de adaptación del destino."
        )

        risks.append(
            {
                "name": "Alta dependencia estacional",
                "score": (
                    68
                    if seasonal_dependency == "Alta"
                    else 90
                ),
                "level": (
                    "Alto"
                    if seasonal_dependency == "Alta"
                    else "Crítico"
                ),
                "evidence": (
                    "La actividad depende en gran medida "
                    "de los periodos de temporada alta."
                ),
            }
        )

        opportunities.append(
            "Fortalecer productos, eventos y segmentos "
            "capaces de activar la temporada media y baja."
        )

    if redistribution in {
        "Baja",
        "Inexistente",
    }:
        risks.append(
            {
                "name": "Baja capacidad de redistribución",
                "score": (
                    72
                    if redistribution == "Baja"
                    else 94
                ),
                "level": (
                    "Alto"
                    if redistribution == "Baja"
                    else "Crítico"
                ),
                "evidence": (
                    "El destino dispone de pocas alternativas "
                    "para distribuir visitantes entre zonas o periodos."
                ),
            }
        )

    if (
        health_score is not None
        and health_score >= 75
    ):
        findings.append(
            "El destino cuenta con una capacidad favorable "
            "para adaptarse a cambios y contingencias."
        )

    evaluated_variables = sum(
        [
            is_evaluated(crisis_plan),
            is_evaluated(diversification),
            is_evaluated(seasonal_dependency),
            is_evaluated(redistribution),
        ]
    )

    return build_capital_result(
        name="Capital de resiliencia",
        health_score=health_score,
        metrics={
            "crisis_plan": crisis_plan or "Sin evaluar",
            "market_diversification": (
                diversification
                or "Sin evaluar"
            ),
            "seasonal_dependency": (
                seasonal_dependency
                or "Sin evaluar"
            ),
            "redistribution_capacity": (
                redistribution
                or "Sin evaluar"
            ),
        },
        findings=findings,
        risks=risks,
        opportunities=opportunities,
        evaluated_variables=evaluated_variables,
        total_variables=4,
    )


# =========================================================
# CÁLCULO CONJUNTO
# =========================================================

def calculate_context_capitals(
    context: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """
    Calcula los cuatro capitales cualitativos.
    """

    return {
        "social_capital": calculate_social_capital(
            context
        ),
        "institutional_capital": calculate_institutional_capital(
            context
        ),
        "reputational_capital": calculate_reputational_capital(
            context
        ),
        "resilience_capital": calculate_resilience_capital(
            context
        ),
    }
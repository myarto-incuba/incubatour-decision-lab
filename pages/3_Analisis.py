import streamlit as st

from database import (
    get_destination,
    init_db,
    list_destinations,
    list_zones,
)
from engine.diagnosis_engine import analyze_destination
from styles import apply_incubatour_theme


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Análisis automático",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_incubatour_theme()
init_db()


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def format_decimal(
    value: float | int | None,
    decimals: int = 2,
) -> str:
    """
    Formatea valores numéricos con seguridad.
    """
    try:
        return f"{float(value or 0):.{decimals}f}"
    except (TypeError, ValueError):
        return "0.00"


def risk_message(
    risk_level: str,
) -> tuple[str, str]:
    """
    Devuelve una lectura ejecutiva según el nivel de riesgo.
    """

    messages = {
        "Crítico": (
            "Riesgo crítico",
            (
                "El destino presenta una combinación de presiones que "
                "requiere intervención prioritaria y validación inmediata."
            ),
        ),
        "Alto": (
            "Riesgo alto",
            (
                "La presión turística es elevada y debe completarse con "
                "la lectura territorial, social e institucional."
            ),
        ),
        "Medio": (
            "Riesgo medio",
            (
                "Existen señales de tensión que todavía pueden gestionarse "
                "mediante medidas preventivas."
            ),
        ),
        "Bajo": (
            "Riesgo bajo",
            (
                "La presión general es moderada, aunque pueden existir "
                "focos territoriales o riesgos cualitativos."
            ),
        ),
    }

    return messages.get(
        risk_level,
        (
            "Resultado preliminar",
            (
                "El diagnóstico necesita más información para emitir "
                "una lectura integral."
            ),
        ),
    )


# =========================================================
# DESTINOS
# =========================================================

destinations = list_destinations()

if not destinations:
    st.warning(
        "Primero debes crear un expediente de destino."
    )

    if st.button(
        "Crear expediente",
        type="primary",
    ):
        st.switch_page(
            "pages/2_Diagnostico.py"
        )

    st.stop()


destination_labels = {
    (
        f"{destination['municipio']} · "
        f"{destination.get('provincia', '')}"
    ): destination["id"]
    for destination in destinations
}

active_destination_id = st.session_state.get(
    "active_destination_id"
)

default_index = 0

if active_destination_id in destination_labels.values():
    default_index = list(
        destination_labels.values()
    ).index(active_destination_id)


# =========================================================
# SELECCIÓN
# =========================================================

st.caption("ANALIZA · RESULTADO AUTOMÁTICO")

st.title("Análisis del destino")

st.write(
    "El sistema transforma los datos del expediente en indicadores, "
    "hallazgos, riesgos y oportunidades preliminares."
)

selected_destination_label = st.selectbox(
    "Destino",
    options=list(destination_labels.keys()),
    index=default_index,
)

destination_id = destination_labels[
    selected_destination_label
]

st.session_state[
    "active_destination_id"
] = destination_id

destination = get_destination(
    destination_id
)

zones = list_zones(
    destination_id
)

analysis = analyze_destination(
    destination,
    zones,
)

tourism = analysis["tourism_capital"]
territorial = analysis.get("territorial_capital")

risk_title, risk_copy = risk_message(
    analysis["risk_level"]
)


# =========================================================
# FICHA DEL DESTINO
# =========================================================

with st.container(border=True):
    st.subheader(
        destination.get(
            "municipio",
            "Destino sin nombre",
        )
    )

    location = " · ".join(
        value
        for value in [
            destination.get("provincia", ""),
            destination.get(
                "comunidad_autonoma",
                "",
            ),
        ]
        if value
    )

    if location:
        st.caption(location)

    st.info(
        f"Capitales evaluados: "
        f"{analysis.get('capitals_evaluated', 1)} "
        f"de {analysis.get('capitals_total', 6)}. "
        "La lectura se actualizará conforme se complete "
        "Contexto y Territorio."
    )


# =========================================================
# PANORAMA
# =========================================================

st.header("Panorama preliminar")

with st.container(border=True):
    title_col, confidence_col = st.columns(
        [3, 1]
    )

    with title_col:
        st.subheader("Estado actual")
        st.write(
            f"## {analysis['stage']}"
        )
        st.write(risk_copy)

    with confidence_col:
        st.metric(
            "Confianza",
            f"{analysis['confidence']} %",
        )

    health_score = int(
        analysis.get(
            "destination_health",
            0,
        )
        or 0
    )

    st.progress(
        max(
            0.0,
            min(
                health_score / 100,
                1.0,
            ),
        )
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Salud preliminar",
        f"{health_score} / 100",
    )

    metric2.metric(
        "Riesgo global",
        f"{analysis.get('global_risk_score', tourism['pressure_score'])} / 100",
    )

    metric3.metric(
        "Nivel de riesgo",
        risk_title,
    )


# =========================================================
# CAPITALES EVALUADOS
# =========================================================

st.header("Capitales evaluados")

capital_col1, capital_col2 = st.columns(2)

with capital_col1:
    with st.container(border=True):
        st.subheader("Capital turístico")

        tourism_health = tourism.get(
            "health_score",
            tourism.get("score", 0),
        )

        st.metric(
            "Salud",
            f"{tourism_health} / 100",
        )

        st.metric(
            "Presión",
            f"{tourism.get('pressure_score', 0)} / 100",
        )

        st.write(
            f"**Estado:** "
            f"{tourism.get('status', tourism.get('level', 'Sin evaluar'))}"
        )

with capital_col2:
    with st.container(border=True):
        st.subheader("Capital territorial")

        if (
            territorial
            and territorial.get("health_score") is not None
        ):
            st.metric(
                "Salud",
                f"{territorial['health_score']} / 100",
            )

            st.metric(
                "Presión",
                f"{territorial['pressure_score']} / 100",
            )

            st.write(
                f"**Estado:** "
                f"{territorial.get('status', 'Sin evaluar')}"
            )
        else:
            st.metric(
                "Salud",
                "Pendiente",
            )

            st.write(
                "Registra zonas en Territorio para completar "
                "esta dimensión."
            )


# =========================================================
# INDICADORES
# =========================================================

st.header("Indicadores calculados")

metrics = tourism.get(
    "metrics",
    {},
)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        "Visitantes por residente",
        format_decimal(
            metrics.get(
                "visitors_per_resident",
                0,
            )
        ),
    )

    st.metric(
        "Presión total por residente",
        format_decimal(
            metrics.get(
                "total_pressure_per_resident",
                0,
            )
        ),
    )

with metric_col2:
    st.metric(
        "Pernoctaciones por residente",
        format_decimal(
            metrics.get(
                "overnight_stays_per_resident",
                0,
            )
        ),
    )

    st.metric(
        "Estancia media",
        (
            f"{format_decimal(metrics.get('average_stay', 0))} "
            "noches"
        ),
    )

with metric_col3:
    st.metric(
        "Plazas por residente",
        format_decimal(
            metrics.get(
                "accommodation_places_per_resident",
                0,
            ),
            3,
        ),
    )

    st.metric(
        "Meses de temporada alta",
        int(
            metrics.get(
                "peak_month_count",
                0,
            )
            or 0
        ),
    )


# =========================================================
# HALLAZGOS
# =========================================================

st.header("Qué detectamos")

findings = tourism.get(
    "findings",
    [],
)

if territorial:
    findings = (
        findings
        + territorial.get(
            "findings",
            [],
        )
    )

if findings:
    for finding in findings[:6]:
        with st.container(border=True):
            st.write(finding)
else:
    st.info(
        "Todavía no existen hallazgos suficientes."
    )


# =========================================================
# RIESGOS
# =========================================================

st.header("Riesgos prioritarios")

main_risks = analysis.get(
    "main_risks",
    [],
)

if main_risks:
    risk_columns = st.columns(
        min(
            3,
            len(main_risks),
        )
    )

    for column, risk in zip(
        risk_columns,
        main_risks[:3],
    ):
        with column:
            with st.container(border=True):
                st.subheader(
                    risk.get(
                        "name",
                        "Riesgo",
                    )
                )

                st.metric(
                    "Nivel",
                    risk.get(
                        "level",
                        "Sin evaluar",
                    ),
                )

                st.write(
                    risk.get(
                        "evidence",
                        "Sin evidencia disponible.",
                    )
                )
else:
    st.info(
        "No se han identificado riesgos estructurados todavía."
    )


# =========================================================
# OPORTUNIDADES
# =========================================================

st.header("Oportunidades detectadas")

opportunities = analysis.get(
    "main_opportunities",
    [],
)

if opportunities:
    for opportunity in opportunities[:5]:
        st.success(opportunity)
else:
    st.info(
        "Las oportunidades se completarán al incorporar "
        "Contexto y Territorio."
    )


# =========================================================
# LECTURA EJECUTIVA
# =========================================================

with st.container(border=True):
    st.header("Lectura ejecutiva")

    risk_level = analysis.get(
        "risk_level",
        "Sin evaluar",
    )

    if risk_level in {
        "Crítico",
        "Alto",
    }:
        st.warning(
            "La prioridad no debería ser aumentar la promoción "
            "de forma indiscriminada. Primero debe identificarse "
            "dónde se concentra la presión, qué impactos genera "
            "y qué capacidad de respuesta tiene el destino."
        )

    elif risk_level == "Medio":
        st.info(
            "El destino presenta señales que todavía pueden "
            "gestionarse preventivamente mediante monitoreo, "
            "diversificación y redistribución de flujos."
        )

    else:
        st.success(
            "La presión general es moderada. El análisis debe "
            "centrarse en oportunidades de desarrollo equilibrado "
            "y prevención de futuras concentraciones."
        )


# =========================================================
# INFORMACIÓN PENDIENTE
# =========================================================

st.header("Qué falta para completar el diagnóstico")

pending1, pending2, pending3 = st.columns(3)

with pending1:
    with st.container(border=True):
        st.subheader("Contexto")

        st.write(
            "Completar percepción social, capacidad institucional, "
            "reputación y resiliencia."
        )

with pending2:
    with st.container(border=True):
        st.subheader("Territorio")

        st.write(
            "Identificar zonas críticas, concentración espacial "
            "y capacidad de respuesta local."
        )

with pending3:
    with st.container(border=True):
        st.subheader("Validación")

        st.write(
            "Contrastar los resultados automáticos con fuentes, "
            "entrevistas y criterio técnico."
        )


# =========================================================
# NAVEGACIÓN
# =========================================================

action1, action2, action3 = st.columns(
    [1.2, 1, 1]
)

with action1:
    if st.button(
        "Continuar a Contexto",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/4_Contexto.py"
        )

with action2:
    if st.button(
        "Continuar a Territorio",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/5_Territorio.py"
        )

with action3:
    if st.button(
        "Volver al expediente",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/2_Diagnostico.py"
        )
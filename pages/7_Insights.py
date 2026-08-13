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
    page_title="Insights estratégicos",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_incubatour_theme()
init_db()


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def safe_int(value: object) -> int:
    try:
        return int(round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def normalize_list(value: object) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def capital_label(key: str) -> str:
    labels = {
        "tourism": "Turístico",
        "territorial": "Territorial",
        "social": "Social",
        "institutional": "Institucional",
        "reputational": "Reputacional",
        "resilience": "Resiliencia",
    }

    return labels.get(
        key,
        key.title(),
    )


def health_status(score: int | None) -> str:
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


def render_insight_list(
    items: list,
    empty_message: str,
) -> None:
    if not items:
        st.info(empty_message)
        return

    for position, item in enumerate(
        items,
        start=1,
    ):
        with st.container(border=True):
            if isinstance(item, dict):
                title = (
                    item.get("name")
                    or item.get("title")
                    or f"Insight {position}"
                )

                description = (
                    item.get("evidence")
                    or item.get("description")
                    or item.get("text")
                    or ""
                )

                st.subheader(
                    f"{position}. {title}"
                )

                if description:
                    st.write(description)

            else:
                st.write(
                    f"**{position}.** {item}"
                )


# =========================================================
# ENCABEZADO
# =========================================================

st.caption("INCUBATOUR DECISION LAB")

st.title("Insights estratégicos")

st.write(
    "Interpreta el diagnóstico mediante la metodología "
    "Póker de As: Analiza, Aprende, Adapta y Actúa."
)


# =========================================================
# SELECCIÓN DEL DESTINO
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


destination_labels = {}

for destination_item in destinations:
    municipality = destination_item.get(
        "municipio",
        "Destino sin nombre",
    )

    province = destination_item.get(
        "provincia",
        "",
    )

    label = municipality

    if province:
        label = f"{municipality} · {province}"

    destination_labels[label] = destination_item["id"]


destination_ids = list(
    destination_labels.values()
)

active_destination_id = st.session_state.get(
    "active_destination_id"
)

default_index = 0

if active_destination_id in destination_ids:
    default_index = destination_ids.index(
        active_destination_id
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


# =========================================================
# VARIABLES
# =========================================================

health_score = safe_int(
    analysis.get(
        "destination_health"
    )
)

risk_score = safe_int(
    analysis.get(
        "global_risk_score"
    )
)

risk_level = analysis.get(
    "risk_level",
    "Sin evaluar",
)

confidence = safe_int(
    analysis.get(
        "confidence"
    )
)

stage = analysis.get(
    "stage",
    "Sin clasificación",
)

executive_summary = analysis.get(
    "executive_summary",
    "",
)

capitals = analysis.get(
    "capitals"
) or {}

main_risks = normalize_list(
    analysis.get(
        "main_risks"
    )
)

main_strengths = normalize_list(
    analysis.get(
        "main_strengths"
    )
)

main_opportunities = normalize_list(
    analysis.get(
        "main_opportunities"
    )
)

poker_as = analysis.get(
    "poker_as"
) or {}

analiza = normalize_list(
    poker_as.get(
        "analiza"
    )
)

aprende = normalize_list(
    poker_as.get(
        "aprende"
    )
)

adapta = normalize_list(
    poker_as.get(
        "adapta"
    )
)

actua = normalize_list(
    poker_as.get(
        "actua"
    )
)


# =========================================================
# ESTADO GENERAL
# =========================================================

with st.container(border=True):
    title_column, stage_column = st.columns(
        [3, 1]
    )

    with title_column:
        st.subheader(
            destination.get(
                "municipio",
                "Destino sin nombre",
            )
        )

        location = " · ".join(
            value
            for value in [
                destination.get(
                    "provincia",
                    "",
                ),
                destination.get(
                    "comunidad_autonoma",
                    "",
                ),
            ]
            if value
        )

        if location:
            st.caption(location)

    with stage_column:
        st.metric(
            "Estado estratégico",
            stage,
        )


metric_1, metric_2, metric_3 = st.columns(
    3
)

with metric_1:
    st.metric(
        "Salud global",
        f"{health_score}/100",
    )

with metric_2:
    st.metric(
        "Riesgo",
        f"{risk_score}/100",
        risk_level,
    )

with metric_3:
    st.metric(
        "Confianza",
        f"{confidence} %",
    )


# =========================================================
# LECTURA EJECUTIVA
# =========================================================

st.header("Lectura ejecutiva")

with st.container(border=True):
    if executive_summary:
        st.write(executive_summary)

    else:
        st.info(
            "Todavía no existe información suficiente "
            "para generar una lectura ejecutiva."
        )


# =========================================================
# PÓKER DE AS
# =========================================================

st.header("Póker de As")

st.write(
    "La metodología convierte los datos en una secuencia de "
    "interpretación y decisión."
)

tab_analiza, tab_aprende, tab_adapta, tab_actua = st.tabs(
    [
        "Analiza",
        "Aprende",
        "Adapta",
        "Actúa",
    ]
)


with tab_analiza:
    st.subheader("Analiza")

    st.write(
        "¿Qué está ocurriendo actualmente en el destino?"
    )

    render_insight_list(
        analiza,
        (
            "Todavía no existen hallazgos suficientes. "
            "Completa Diagnóstico, Contexto y Territorio."
        ),
    )


with tab_aprende:
    st.subheader("Aprende")

    st.write(
        "¿Por qué ocurre y qué relaciones existen entre los datos?"
    )

    render_insight_list(
        aprende,
        (
            "Todavía no existen relaciones estratégicas suficientes "
            "para generar aprendizaje."
        ),
    )


with tab_adapta:
    st.subheader("Adapta")

    st.write(
        "¿Qué oportunidades de ajuste tiene el destino?"
    )

    render_insight_list(
        adapta,
        (
            "Las oportunidades aparecerán cuando exista "
            "información suficiente en los seis capitales."
        ),
    )


with tab_actua:
    st.subheader("Actúa")

    st.write(
        "¿Qué decisiones deben priorizarse?"
    )

    if actua:
        for position, action in enumerate(
            actua[:6],
            start=1,
        ):
            with st.container(border=True):
                action_column, priority_column = st.columns(
                    [4, 1]
                )

                with action_column:
                    st.subheader(
                        f"{position}. {action}"
                    )

                with priority_column:
                    if position == 1:
                        st.error(
                            "Inmediata"
                        )

                    elif position <= 3:
                        st.warning(
                            "Alta"
                        )

                    else:
                        st.info(
                            "Media"
                        )

    else:
        st.info(
            "Todavía no existen acciones automáticas suficientes."
        )


# =========================================================
# MAPA DE CAPITALES
# =========================================================

st.header("Lectura de los seis capitales")

capital_order = [
    "tourism",
    "territorial",
    "social",
    "institutional",
    "reputational",
    "resilience",
]

capital_columns = st.columns(3)

for index, capital_key in enumerate(
    capital_order
):
    capital = capitals.get(
        capital_key
    ) or {}

    score = capital.get(
        "health_score"
    )

    pressure = capital.get(
        "pressure_score"
    )

    findings = normalize_list(
        capital.get(
            "findings"
        )
    )

    current_column = capital_columns[
        index % 3
    ]

    with current_column:
        with st.container(border=True):
            st.subheader(
                capital_label(
                    capital_key
                )
            )

            if score is None:
                st.metric(
                    "Salud",
                    "Pendiente",
                )

                st.write(
                    "Esta dimensión todavía no tiene "
                    "información suficiente."
                )

                continue

            score_value = safe_int(
                score
            )

            pressure_value = safe_int(
                pressure
            )

            st.metric(
                "Salud",
                f"{score_value}/100",
            )

            st.progress(
                max(
                    0.0,
                    min(
                        score_value / 100,
                        1.0,
                    ),
                )
            )

            st.write(
                f"**Estado:** "
                f"{health_status(score_value)}"
            )

            st.write(
                f"**Presión:** "
                f"{pressure_value}/100"
            )

            if findings:
                st.caption(
                    findings[0]
                )


# =========================================================
# PRINCIPALES RIESGOS
# =========================================================

st.header("Qué puede comprometer al destino")

if main_risks:
    risk_columns = st.columns(2)

    for index, risk in enumerate(
        main_risks[:6]
    ):
        current_column = risk_columns[
            index % 2
        ]

        with current_column:
            with st.container(border=True):
                if isinstance(risk, dict):
                    st.subheader(
                        risk.get(
                            "name",
                            "Riesgo",
                        )
                    )

                    risk_metric_column, capital_column = st.columns(
                        2
                    )

                    with risk_metric_column:
                        st.metric(
                            "Score",
                            (
                                f"{safe_int(risk.get('score'))}"
                                "/100"
                            ),
                        )

                    with capital_column:
                        st.metric(
                            "Nivel",
                            risk.get(
                                "level",
                                "Sin evaluar",
                            ),
                        )

                    evidence = risk.get(
                        "evidence",
                        "",
                    )

                    if evidence:
                        st.write(evidence)

                    capital_name = risk.get(
                        "capital"
                    )

                    if capital_name:
                        st.caption(
                            capital_name
                        )

                else:
                    st.write(str(risk))

else:
    st.success(
        "No se han identificado riesgos prioritarios "
        "con la información actual."
    )


# =========================================================
# FORTALEZAS Y OPORTUNIDADES
# =========================================================

strength_column, opportunity_column = st.columns(
    2
)

with strength_column:
    st.header("Qué sostiene al destino")

    if main_strengths:
        for strength in main_strengths[:5]:
            with st.container(border=True):
                if isinstance(strength, dict):
                    st.subheader(
                        strength.get(
                            "name",
                            "Fortaleza",
                        )
                    )

                    st.write(
                        f"**Score:** "
                        f"{safe_int(strength.get('score'))}/100"
                    )

                    evidence = strength.get(
                        "evidence",
                        "",
                    )

                    if evidence:
                        st.write(evidence)

                else:
                    st.write(str(strength))

    else:
        st.info(
            "Todavía no existen fortalezas consolidadas."
        )


with opportunity_column:
    st.header("Dónde puede adaptarse")

    if main_opportunities:
        for opportunity in main_opportunities[:6]:
            if isinstance(opportunity, dict):
                text = (
                    opportunity.get("name")
                    or opportunity.get("description")
                    or str(opportunity)
                )
            else:
                text = str(opportunity)

            st.success(text)

    else:
        st.info(
            "Todavía no existen oportunidades automáticas."
        )


# =========================================================
# COBERTURA
# =========================================================

st.header("Cobertura del análisis")

coverage_1, coverage_2, coverage_3 = st.columns(
    3
)

with coverage_1:
    st.metric(
        "Capitales evaluados",
        (
            f"{safe_int(analysis.get('capitals_evaluated'))}"
            f"/{safe_int(analysis.get('capitals_total', 6))}"
        ),
    )

with coverage_2:
    st.metric(
        "Confianza",
        f"{confidence} %",
    )

with coverage_3:
    st.metric(
        "Zonas territoriales",
        len(zones),
    )


if confidence < 60:
    st.warning(
        "Los insights deben considerarse preliminares. "
        "Completa fuentes, Contexto y Territorio."
    )

elif confidence < 80:
    st.info(
        "Los insights cuentan con una base suficiente, "
        "aunque todavía requieren validación."
    )

else:
    st.success(
        "Los insights cuentan con una base sólida "
        "para orientar decisiones."
    )


# =========================================================
# NAVEGACIÓN
# =========================================================

st.write("")

navigation_1, navigation_2, navigation_3 = st.columns(
    3
)

with navigation_1:
    if st.button(
        "Volver al Dashboard",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Dashboard.py"
        )

with navigation_2:
    if st.button(
        "Editar Contexto",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/4_Contexto.py"
        )

with navigation_3:
    if st.button(
        "Crear informe",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/8_Informe.py"
        )
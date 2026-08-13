import pandas as pd
import streamlit as st
import html

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
    page_title="Dashboard ejecutivo",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_incubatour_theme()
init_db()

st.markdown(
    """
    <style>
    .dashboard-status-card {
        height: 100%;
        min-height: 132px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 1.15rem 1.25rem;
        background: #FFFFFF;
        border: 1px solid #E7E7E4;
        border-radius: 18px;
        box-shadow: 0 7px 24px rgba(24, 24, 27, 0.035);
    }

    .dashboard-status-label {
        margin-bottom: 0.45rem;
        color: #667085;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .dashboard-status-value {
        color: #18181B;
        font-size: clamp(1.15rem, 2vw, 1.65rem);
        font-weight: 800;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .dashboard-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.85rem;
    }

    .dashboard-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.38rem 0.68rem;
        border: 1px solid rgba(245, 47, 139, 0.16);
        border-radius: 999px;
        background: #FCE8F2;
        color: #A71960;
        font-size: 0.78rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .priority-badge {
        width: 100%;
        min-height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.65rem 0.8rem;
        border-radius: 12px;
        text-align: center;
        font-size: 0.86rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .priority-immediate {
        background: #FDE8E8;
        border: 1px solid #F4B8B8;
        color: #9F1D1D;
    }

    .priority-high {
        background: #FFF3B0;
        border: 1px solid #E9D878;
        color: #624B00;
    }

    .priority-medium {
        background: #EAF1FF;
        border: 1px solid #C9D8F5;
        color: #244A88;
    }

    .health-warning-card {
        width: 100%;
        padding: 1rem 1.15rem;
        border: 1px solid #E4D277;
        border-radius: 14px;
        background: #FFF4B5;
        color: #5F4500 !important;
        font-size: 0.96rem;
        font-weight: 650;
        line-height: 1.55;
    }

    .health-warning-card span,
    .health-warning-card p,
    .health-warning-card strong {
        color: #5F4500 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def safe_int(value: object) -> int:
    try:
        return int(round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def format_number(value: object) -> str:
    try:
        number = int(float(value or 0))
        return f"{number:,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def capital_label(key: str) -> str:
    labels = {
        "tourism": "Turístico",
        "territorial": "Territorial",
        "social": "Social",
        "institutional": "Institucional",
        "reputational": "Reputacional",
        "resilience": "Resiliencia",
    }

    return labels.get(key, key.title())


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


def risk_status(score: int | None) -> str:
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


def normalize_list(value: object) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def render_health_message(
    health_score: int,
    risk_level: str,
) -> None:
    if health_score >= 80:
        st.success(
            "El destino presenta una estructura sólida. "
            "La prioridad es conservar el equilibrio y anticipar riesgos."
        )

    elif health_score >= 65:
        st.info(
            "El destino se mantiene estable, aunque existen variables "
            "que requieren monitoreo y gestión preventiva."
        )

    elif health_score >= 50:
        st.markdown(
            """
            <div class="health-warning-card">
                El destino presenta vulnerabilidades que pueden evolucionar
                hacia tensiones mayores si no se interviene.
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif health_score >= 35:
        st.markdown(
            """
            <div class="health-warning-card">
                El destino se encuentra en tensión. Es necesario priorizar
                medidas correctivas y fortalecer su capacidad de respuesta.
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.error(
            "El destino presenta una situación crítica. Se requiere "
            "intervención prioritaria, validación técnica y seguimiento."
        )

    st.caption(
        f"Nivel de riesgo consolidado: {risk_level}."
    )


# =========================================================
# ENCABEZADO
# =========================================================

st.caption("INCUBATOUR DECISION LAB")

st.title("Dashboard ejecutivo")

st.write(
    "Visualiza la situación actual del destino, los seis capitales, "
    "los riesgos principales y las decisiones que deben priorizarse."
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


active_destination_id = st.session_state.get(
    "active_destination_id"
)

destination_ids = list(
    destination_labels.values()
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
# DATOS DEL ANÁLISIS
# =========================================================

health_score = safe_int(
    analysis.get(
        "destination_health"
    )
)

global_risk_score = safe_int(
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

capitals = analysis.get(
    "capitals"
) or {}

main_risks = normalize_list(
    analysis.get(
        "main_risks"
    )
)

main_opportunities = normalize_list(
    analysis.get(
        "main_opportunities"
    )
)

main_strengths = normalize_list(
    analysis.get(
        "main_strengths"
    )
)

executive_summary = analysis.get(
    "executive_summary",
    "",
)

poker_as = analysis.get(
    "poker_as"
) or {}


# =========================================================
# IDENTIFICACIÓN
# =========================================================

with st.container(border=True):
    title_column, status_column = st.columns(
        [2.55, 1.45],
        vertical_alignment="center",
    )

    with title_column:
        st.subheader(
            destination.get(
                "municipio",
                "Destino sin nombre",
            )
        )

        location_values = [
            destination.get(
                "provincia",
                "",
            ),
            destination.get(
                "comunidad_autonoma",
                "",
            ),
        ]

        location = " · ".join(
            value
            for value in location_values
            if value
        )

        if location:
            st.caption(location)

        typologies = destination.get(
            "tipologias"
        )

        if isinstance(typologies, str):
            typologies = [
                item.strip()
                for item in typologies.split(",")
                if item.strip()
            ]

        if typologies:
            chips = "".join(
                (
                    '<span class="dashboard-chip">'
                    + html.escape(str(item))
                    + "</span>"
                )
                for item in typologies
            )

            st.markdown(
                (
                    '<div class="dashboard-chip-row">'
                    + chips
                    + "</div>"
                ),
                unsafe_allow_html=True,
            )

    with status_column:
        st.markdown(
            (
                '<div class="dashboard-status-card">'
                '<div class="dashboard-status-label">Estado</div>'
                '<div class="dashboard-status-value">'
                + html.escape(str(stage))
                + "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


# =========================================================
# SITUACIÓN ACTUAL
# =========================================================

st.header("Situación actual")

with st.container(border=True):
    health_column, metrics_column = st.columns(
        [2, 1]
    )

    with health_column:
        st.subheader(
            f"Salud global: {health_score}/100"
        )

        render_health_message(
            health_score,
            risk_level,
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

    with metrics_column:
        st.metric(
            "Riesgo global",
            f"{global_risk_score}/100",
        )

        st.metric(
            "Nivel de riesgo",
            risk_level,
        )

        st.metric(
            "Confianza",
            f"{confidence} %",
        )


# =========================================================
# PANORAMA
# =========================================================

st.header("Panorama del destino")

metric_1, metric_2, metric_3, metric_4 = st.columns(
    4
)

with metric_1:
    st.metric(
        "Población",
        format_number(
            destination.get(
                "poblacion_residente"
            )
        ),
    )

with metric_2:
    st.metric(
        "Visitantes",
        format_number(
            destination.get(
                "visitantes_anuales"
            )
        ),
    )

with metric_3:
    st.metric(
        "Pernoctaciones",
        format_number(
            destination.get(
                "pernoctaciones_anuales"
            )
        ),
    )

with metric_4:
    st.metric(
        "Zonas analizadas",
        len(zones),
    )


# =========================================================
# SEIS CAPITALES
# =========================================================

st.header("Los seis capitales")

capital_order = [
    "tourism",
    "territorial",
    "social",
    "institutional",
    "reputational",
    "resilience",
]

capital_rows = []

for capital_key in capital_order:
    capital = capitals.get(
        capital_key
    ) or {}

    health = capital.get(
        "health_score"
    )

    pressure = capital.get(
        "pressure_score"
    )

    evaluated = health is not None

    capital_rows.append(
        {
            "Capital": capital_label(
                capital_key
            ),
            "Salud": (
                safe_int(health)
                if evaluated
                else 0
            ),
            "Presión": (
                safe_int(pressure)
                if pressure is not None
                else 0
            ),
            "Estado": health_status(
                health
            ),
            "Riesgo": risk_status(
                pressure
            ),
            "Evaluado": (
                "Sí"
                if evaluated
                else "No"
            ),
        }
    )


capital_df = pd.DataFrame(
    capital_rows,
    columns=[
        "Capital",
        "Salud",
        "Presión",
        "Estado",
        "Riesgo",
        "Evaluado",
    ],
)

evaluated_capital_df = capital_df[
    capital_df["Evaluado"] == "Sí"
].copy()


if not evaluated_capital_df.empty:
    chart_df = evaluated_capital_df[
        [
            "Capital",
            "Salud",
        ]
    ].set_index(
        "Capital"
    )

    st.bar_chart(
        chart_df,
        horizontal=True,
        use_container_width=True,
        height=350,
    )

else:
    st.info(
        "Todavía no existen capitales suficientes "
        "para mostrar el gráfico."
    )


capital_columns = st.columns(3)

for index, row in capital_df.iterrows():
    current_column = capital_columns[
        index % 3
    ]

    with current_column:
        with st.container(border=True):
            st.subheader(
                row["Capital"]
            )

            if row["Evaluado"] == "Sí":
                st.metric(
                    "Salud",
                    f"{row['Salud']}/100",
                )

                st.progress(
                    max(
                        0.0,
                        min(
                            row["Salud"] / 100,
                            1.0,
                        ),
                    )
                )

                st.write(
                    f"**Estado:** {row['Estado']}"
                )

                st.write(
                    f"**Riesgo:** {row['Riesgo']}"
                )

                st.caption(
                    f"Presión: {row['Presión']}/100"
                )

            else:
                st.metric(
                    "Salud",
                    "Pendiente",
                )

                st.write(
                    "Completa la información de esta dimensión "
                    "para obtener una evaluación."
                )


# =========================================================
# RESUMEN EJECUTIVO
# =========================================================

st.header("Lectura ejecutiva")

with st.container(border=True):
    if executive_summary:
        st.write(
            executive_summary
        )

    else:
        st.info(
            "Todavía no existe información suficiente "
            "para generar un resumen ejecutivo."
        )


# =========================================================
# RIESGOS
# =========================================================

st.header("Riesgos prioritarios")

if main_risks:
    risk_columns = st.columns(3)

    for index, risk in enumerate(
        main_risks[:6]
    ):
        current_column = risk_columns[
            index % 3
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

                    st.metric(
                        "Prioridad",
                        risk.get(
                            "level",
                            "Sin evaluar",
                        ),
                    )

                    st.write(
                        f"**Score:** "
                        f"{safe_int(risk.get('score'))}/100"
                    )

                    evidence = risk.get(
                        "evidence",
                        "Sin evidencia disponible.",
                    )

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
        "No se identificaron riesgos prioritarios "
        "con la información disponible."
    )


# =========================================================
# FORTALEZAS Y OPORTUNIDADES
# =========================================================

strength_column, opportunity_column = st.columns(
    2
)

with strength_column:
    st.header("Fortalezas")

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
            "Todavía no existen fortalezas consolidadas "
            "o falta completar el diagnóstico."
        )


with opportunity_column:
    st.header("Oportunidades")

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
            "Las oportunidades se generarán al completar "
            "las dimensiones pendientes."
        )


# =========================================================
# ACCIONES
# =========================================================

st.header("Qué debe hacer el destino ahora")

actions = normalize_list(
    poker_as.get(
        "actua"
    )
)

if actions:
    for position, action in enumerate(
        actions[:5],
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
                    priority_class = "priority-immediate"
                    priority_text = "Prioridad inmediata"

                elif position <= 3:
                    priority_class = "priority-high"
                    priority_text = "Prioridad alta"

                else:
                    priority_class = "priority-medium"
                    priority_text = "Prioridad media"

                st.markdown(
                    (
                        '<div class="priority-badge '
                        + priority_class
                        + '">'
                        + priority_text
                        + "</div>"
                    ),
                    unsafe_allow_html=True,
                )

else:
    st.info(
        "Completa Contexto y Territorio para generar "
        "acciones prioritarias."
    )


# =========================================================
# CALIDAD DEL ANÁLISIS
# =========================================================

st.header("Calidad y cobertura")

quality_1, quality_2, quality_3 = st.columns(
    3
)

capitals_evaluated = safe_int(
    analysis.get(
        "capitals_evaluated"
    )
)

capitals_total = safe_int(
    analysis.get(
        "capitals_total",
        6,
    )
)

context_capitals_complete = sum(
    1
    for key in [
        "social",
        "institutional",
        "reputational",
        "resilience",
    ]
    if capitals.get(
        key,
        {},
    ).get(
        "health_score"
    )
    is not None
)

with quality_1:
    st.metric(
        "Capitales evaluados",
        f"{capitals_evaluated}/{capitals_total}",
    )

with quality_2:
    st.metric(
        "Confianza",
        f"{confidence} %",
    )

with quality_3:
    st.metric(
        "Capitales cualitativos",
        f"{context_capitals_complete}/4",
    )


if confidence < 60:
    st.warning(
        "El nivel de confianza todavía es limitado. "
        "Completa fuentes, Contexto y zonas territoriales."
    )

elif confidence < 80:
    st.info(
        "El diagnóstico tiene una base suficiente, "
        "aunque todavía puede mejorar."
    )

else:
    st.success(
        "El diagnóstico cuenta con una base sólida "
        "para orientar decisiones estratégicas."
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
        "Ver Insights",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/7_Insights.py"
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
        "Editar Territorio",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/5_Territorio.py"
        )
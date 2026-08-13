import os
from typing import Any

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
    page_title="Centro de Control | Incubatour Decision Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
apply_incubatour_theme()


# =========================================================
# CSS
# Solo se utiliza para estilizar componentes nativos.
# No se usa HTML para construir contenido.
# =========================================================

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        height: 0;
        min-height: 0;
        background: transparent;
    }

    div[data-testid="stToolbar"] {
        display: none;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    /* Tipografía */

    h1 {
        font-size: 3.25rem !important;
        font-weight: 850 !important;
        line-height: 1.02 !important;
        letter-spacing: -0.055em !important;
    }

    h2 {
        font-weight: 820 !important;
        letter-spacing: -0.035em !important;
    }

    h3 {
        font-weight: 780 !important;
        letter-spacing: -0.025em !important;
    }

    /* Contenedores con borde */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
        border-color: rgba(128, 128, 128, 0.18);
        box-shadow: 0 10px 35px rgba(20, 20, 35, 0.035);
    }

    /* Métricas */

    div[data-testid="stMetric"] {
        min-height: 128px;
        padding: 1.1rem 1.15rem;
        border: 1px solid rgba(128, 128, 128, 0.16);
        border-radius: 17px;
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.07),
                rgba(128, 128, 128, 0.018)
            );
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.73rem;
        font-weight: 750;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        opacity: 0.65;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 850;
        letter-spacing: -0.045em;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.76rem;
    }

    /* Botones */

    div[data-testid="stButton"] > button {
        min-height: 44px;
        border-radius: 11px;
        font-weight: 720;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    div[data-testid="stButton"] > button:hover {
        transform: translateY(-1px);
    }

    button[kind="primary"] {
        border: none;
        background:
            linear-gradient(
                90deg,
                #f42c86,
                #ff4c55
            );
        box-shadow:
            0 8px 22px rgba(244, 44, 134, 0.18);
    }

    /* Selectbox */

    div[data-testid="stSelectbox"] label {
        font-size: 0.75rem;
        font-weight: 750;
    }

    /* Progress */

    div[data-testid="stProgress"] > div > div > div {
        background:
            linear-gradient(
                90deg,
                #f42c86,
                #ff4c55,
                #8c4dff
            );
    }

    /* Captions */

    div[data-testid="stCaptionContainer"] {
        opacity: 0.68;
    }

    /* Alertas */

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* Separadores */

    hr {
        margin-top: 1.35rem;
        margin-bottom: 1.35rem;
        border-color: rgba(128, 128, 128, 0.13);
    }

    @media (max-width: 900px) {
        .block-container {
            padding-top: 1rem;
        }

        h1 {
            font-size: 2.4rem !important;
        }

        div[data-testid="stMetric"] {
            min-height: 105px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def safe_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    result = str(value).strip()

    return result or default


def find_logo() -> str | None:
    possible_paths = [
        "assets/logo_incubatour.png",
        "assets/logo.png",
        "logo_incubatour.png",
        "logo.png",
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            return path

    return None


def switch_page(page_path: str) -> None:
    st.switch_page(page_path)


def start_new_diagnosis() -> None:
    st.session_state.pop(
        "active_destination_id",
        None,
    )

    switch_page(
        "pages/2_Diagnostico.py"
    )


def section_header(
    eyebrow: str,
    title: str,
    description: str | None = None,
) -> None:
    st.caption(
        eyebrow.upper()
    )

    st.subheader(
        title
    )

    if description:
        st.write(
            description
        )


def action_card(
    title: str,
    description: str,
    status: str,
    button_label: str,
    page_path: str,
    key: str,
    icon: str,
    primary: bool = False,
) -> None:
    with st.container(border=True):
        icon_column, title_column = st.columns(
            [0.22, 1.6],
            vertical_alignment="center",
        )

        with icon_column:
            st.markdown(
                f"### {icon}"
            )

        with title_column:
            st.markdown(
                f"#### {title}"
            )

        st.write(
            description
        )

        st.caption(
            status.upper()
        )

        if st.button(
            button_label,
            key=key,
            type=(
                "primary"
                if primary
                else "secondary"
            ),
            use_container_width=True,
        ):
            switch_page(
                page_path
            )


def calculate_completion(
    destination: dict,
    zones: list,
    analysis: dict,
) -> tuple[int, list[str]]:
    completed_sections = 0
    total_sections = 6
    pending_items: list[str] = []

    basic_values = [
        destination.get("municipio"),
        destination.get("poblacion_residente"),
        destination.get("visitantes_anuales"),
        destination.get("pernoctaciones_anuales"),
    ]

    completed_basic_values = sum(
        bool(value)
        for value in basic_values
    )

    if completed_basic_values >= 3:
        completed_sections += 1
    else:
        pending_items.append(
            "Completar los datos básicos del destino."
        )

    capitals = (
        analysis.get("capitals")
        or {}
    )

    tourism_capital = (
        capitals.get("tourism")
        or {}
    )

    if tourism_capital.get("health_score") is not None:
        completed_sections += 1
    else:
        pending_items.append(
            "Completar la información turística."
        )

    context_capitals = [
        "social",
        "institutional",
        "reputational",
        "resilience",
    ]

    completed_context = sum(
        1
        for capital_name in context_capitals
        if (
            capitals.get(capital_name)
            or {}
        ).get("health_score") is not None
    )

    if completed_context >= 3:
        completed_sections += 1
    else:
        pending_items.append(
            "Completar la información de Contexto."
        )

    territorial_capital = (
        capitals.get("territorial")
        or {}
    )

    if (
        zones
        and territorial_capital.get("health_score")
        is not None
    ):
        completed_sections += 1
    else:
        pending_items.append(
            "Registrar zonas y presiones territoriales."
        )

    confidence = safe_int(
        analysis.get("confidence")
    )

    if confidence >= 60:
        completed_sections += 1
    else:
        pending_items.append(
            "Aumentar la cobertura y calidad de los datos."
        )

    if (
        analysis.get("executive_summary")
        and analysis.get("main_risks")
    ):
        completed_sections += 1
    else:
        pending_items.append(
            "Completar la lectura estratégica."
        )

    completion = round(
        completed_sections
        / total_sections
        * 100
    )

    return completion, pending_items


# =========================================================
# CARGA DE DATOS
# =========================================================

logo_path = find_logo()

destinations = (
    list_destinations()
    or []
)

valid_destinations = [
    destination
    for destination in destinations
    if destination.get("id") is not None
]

destination_ids = [
    destination["id"]
    for destination in valid_destinations
]

active_destination = None
active_destination_id = None

if destination_ids:
    active_destination_id = st.session_state.get(
        "active_destination_id"
    )

    if active_destination_id not in destination_ids:
        active_destination_id = destination_ids[0]

        st.session_state[
            "active_destination_id"
        ] = active_destination_id

    active_destination = get_destination(
        active_destination_id
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    if logo_path:
        st.image(
            logo_path,
            use_container_width=True,
        )
    else:
        st.title(
            "Incubatour"
        )

        st.caption(
            "DECISION LAB"
        )

    st.caption(
        "Inteligencia estratégica para destinos turísticos."
    )

    st.divider()

    if active_destination:
        st.caption(
            "DESTINO ACTIVO"
        )

        st.markdown(
            f"**{safe_text(active_destination.get('municipio'), 'Sin nombre')}**"
        )

        province_sidebar = safe_text(
            active_destination.get("provincia")
        )

        if province_sidebar:
            st.caption(
                province_sidebar
            )

        if st.button(
            "Ver portafolio",
            key="sidebar_portfolio",
            use_container_width=True,
        ):
            switch_page(
                "pages/1_Destinos.py"
            )

    st.divider()

    if st.button(
        "+ Nuevo diagnóstico",
        key="sidebar_new_diagnosis",
        type="primary",
        use_container_width=True,
    ):
        start_new_diagnosis()


# =========================================================
# ESTADO VACÍO
# =========================================================

if not active_destination:
    logo_column, title_column = st.columns(
        [0.65, 3],
        vertical_alignment="center",
    )

    with logo_column:
        if logo_path:
            st.image(
                logo_path,
                use_container_width=True,
            )

    with title_column:
        st.caption(
            "INCUBATOUR DECISION LAB"
        )

        st.title(
            "Centro de Control"
        )

    st.divider()

    with st.container(border=True):
        st.caption(
            "INTELIGENCIA ESTRATÉGICA PARA DESTINOS"
        )

        st.header(
            "Convierte datos turísticos en decisiones claras"
        )

        st.write(
            "Crea el primer expediente para evaluar la salud del "
            "destino, anticipar riesgos y definir una hoja de ruta "
            "basada en evidencia."
        )

        button_column_1, button_column_2, spacer = st.columns(
            [1, 1, 2]
        )

        with button_column_1:
            if st.button(
                "Crear diagnóstico",
                key="empty_create",
                type="primary",
                use_container_width=True,
            ):
                start_new_diagnosis()

        with button_column_2:
            if st.button(
                "Abrir destinos",
                key="empty_destinations",
                use_container_width=True,
            ):
                switch_page(
                    "pages/1_Destinos.py"
                )

    section_header(
        "Metodología Incubatour",
        "Del dato a la acción",
        (
            "El Póker de As organiza la lectura estratégica "
            "en cuatro etapas."
        ),
    )

    methodology_columns = st.columns(4)

    methodology = [
        {
            "number": "01",
            "title": "Analiza",
            "description": (
                "Construye una lectura integral "
                "del destino."
            ),
        },
        {
            "number": "02",
            "title": "Aprende",
            "description": (
                "Reconoce relaciones, patrones "
                "y causas."
            ),
        },
        {
            "number": "03",
            "title": "Adapta",
            "description": (
                "Evalúa oportunidades y posibles "
                "escenarios."
            ),
        },
        {
            "number": "04",
            "title": "Actúa",
            "description": (
                "Convierte los hallazgos "
                "en prioridades."
            ),
        },
    ]

    for column, item in zip(
        methodology_columns,
        methodology,
    ):
        with column:
            with st.container(border=True):
                st.caption(
                    item["number"]
                )

                st.subheader(
                    item["title"]
                )

                st.write(
                    item["description"]
                )

    st.stop()


# =========================================================
# DESTINO ACTIVO
# =========================================================

destination_id = active_destination.get("id")

zones = (
    list_zones(destination_id)
    or []
)

analysis = (
    analyze_destination(
        active_destination,
        zones,
    )
    or {}
)

municipality = safe_text(
    active_destination.get("municipio"),
    "Destino sin nombre",
)

province = safe_text(
    active_destination.get("provincia")
)

autonomous_community = safe_text(
    active_destination.get("comunidad_autonoma")
)

location_parts = [
    value
    for value in [
        province,
        autonomous_community,
    ]
    if value
]

location = (
    " · ".join(location_parts)
    if location_parts
    else "Destino turístico"
)

health_score = safe_int(
    analysis.get("destination_health")
)

risk_score = safe_int(
    analysis.get("global_risk_score")
)

risk_level = safe_text(
    analysis.get("risk_level"),
    "Sin clasificación",
)

confidence = safe_int(
    analysis.get("confidence")
)

stage = safe_text(
    analysis.get("stage"),
    "En construcción",
)

completion, pending_items = calculate_completion(
    active_destination,
    zones,
    analysis,
)


# =========================================================
# CABECERA
# =========================================================

brand_area, destination_area = st.columns(
    [1.65, 1],
    vertical_alignment="center",
)

with brand_area:
    logo_column, name_column = st.columns(
        [0.42, 1.8],
        vertical_alignment="center",
    )

    with logo_column:
        if logo_path:
            st.image(
                logo_path,
                use_container_width=True,
            )

    with name_column:
        st.caption(
            "INCUBATOUR DECISION LAB"
        )

        st.subheader(
            "Centro de Control"
        )


with destination_area:
    destination_options: dict[str, Any] = {}

    for destination in valid_destinations:
        option_municipality = safe_text(
            destination.get("municipio"),
            "Destino sin nombre",
        )

        option_province = safe_text(
            destination.get("provincia")
        )

        option_label = option_municipality

        if option_province:
            option_label = (
                f"{option_municipality} · "
                f"{option_province}"
            )

        original_label = option_label
        suffix = 2

        while option_label in destination_options:
            option_label = (
                f"{original_label} ({suffix})"
            )
            suffix += 1

        destination_options[
            option_label
        ] = destination.get("id")

    option_ids = list(
        destination_options.values()
    )

    try:
        default_index = option_ids.index(
            destination_id
        )
    except ValueError:
        default_index = 0

    selected_label = st.selectbox(
        "Destino activo",
        options=list(
            destination_options.keys()
        ),
        index=default_index,
    )

    selected_destination_id = destination_options[
        selected_label
    ]

    if selected_destination_id != destination_id:
        st.session_state[
            "active_destination_id"
        ] = selected_destination_id

        st.rerun()


# =========================================================
# HERO NATIVO
# =========================================================

with st.container(border=True):
    hero_content, hero_status = st.columns(
        [2.3, 0.8],
        vertical_alignment="center",
    )

    with hero_content:
        st.caption(
            "EXPEDIENTE ESTRATÉGICO ACTIVO"
        )

        st.title(
            municipality
        )

        st.markdown(
            f"📍 **{location}**"
        )

        st.write(
            "Consulta el estado general del destino, continúa el "
            "diagnóstico y convierte la evidencia disponible en "
            "una lectura estratégica lista para decidir."
        )

    with hero_status:
        st.caption(
            "ESTADO"
        )

        st.subheader(
            stage
        )

        st.progress(
            completion / 100
        )

        st.caption(
            f"{completion} % del expediente"
        )


# =========================================================
# MÉTRICAS
# =========================================================

metric_columns = st.columns(4)

with metric_columns[0]:
    st.metric(
        label="Salud global",
        value=f"{health_score}/100",
        delta="Condición integral",
        delta_color="off",
    )

with metric_columns[1]:
    st.metric(
        label="Riesgo global",
        value=f"{risk_score}/100",
        delta=risk_level,
        delta_color="off",
    )

with metric_columns[2]:
    st.metric(
        label="Confianza",
        value=f"{confidence} %",
        delta="Calidad de evidencia",
        delta_color="off",
    )

with metric_columns[3]:
    st.metric(
        label="Avance",
        value=f"{completion} %",
        delta=stage,
        delta_color="off",
    )


with st.container(border=True):
    progress_title, progress_value = st.columns(
        [4, 1],
        vertical_alignment="center",
    )

    with progress_title:
        st.markdown(
            "**Cobertura del expediente**"
        )

        st.caption(
            "Porcentaje aproximado de información disponible "
            "para construir el diagnóstico."
        )

    with progress_value:
        st.markdown(
            f"### {completion} %"
        )

    st.progress(
        completion / 100
    )


# =========================================================
# ACCIONES PRINCIPALES
# =========================================================

section_header(
    "Acciones principales",
    "¿Qué deseas hacer ahora?",
)

main_columns = st.columns(4)

with main_columns[0]:
    action_card(
        title="Continuar diagnóstico",
        description=(
            "Actualiza los datos base y completa "
            "la información turística."
        ),
        status="Expediente",
        button_label="Continuar",
        page_path="pages/2_Diagnostico.py",
        key="main_diagnosis",
        icon="⌁",
        primary=True,
    )

with main_columns[1]:
    action_card(
        title="Dashboard",
        description=(
            "Consulta la salud global, los riesgos "
            "y el estado de los capitales."
        ),
        status=f"Salud {health_score}/100",
        button_label="Abrir Dashboard",
        page_path="pages/6_Dashboard.py",
        key="main_dashboard",
        icon="◫",
    )

with main_columns[2]:
    action_card(
        title="Insights",
        description=(
            "Interpreta los hallazgos mediante "
            "la metodología Póker de As."
        ),
        status="Lectura estratégica",
        button_label="Ver Insights",
        page_path="pages/7_Insights.py",
        key="main_insights",
        icon="✦",
    )

with main_columns[3]:
    action_card(
        title="Informe ejecutivo",
        description=(
            "Prepara la salida profesional "
            "del diagnóstico del destino."
        ),
        status="Documento final",
        button_label="Generar informe",
        page_path="pages/8_Informe.py",
        key="main_report",
        icon="▤",
        primary=True,
    )


# =========================================================
# SIGUIENTE MEJOR ACCIÓN
# =========================================================

section_header(
    "Orientación del sistema",
    "Siguiente mejor acción",
    (
        "La recomendación cambia de acuerdo con "
        "la cobertura actual del expediente."
    ),
)

recommendation_column, status_column = st.columns(
    [1.55, 1]
)

with recommendation_column:
    with st.container(border=True):
        if completion < 35:
            st.subheader(
                "Construye la base del expediente"
            )

            st.write(
                "Completa los indicadores esenciales para que "
                "el motor pueda generar una lectura confiable."
            )

            if st.button(
                "Completar diagnóstico",
                key="recommended_diagnosis",
                type="primary",
                use_container_width=True,
            ):
                switch_page(
                    "pages/2_Diagnostico.py"
                )

        elif completion < 65:
            st.subheader(
                "Añade contexto y territorio"
            )

            st.write(
                "Incorpora percepción social, gobernanza, "
                "reputación, resiliencia y zonas de presión."
            )

            context_button, territory_button = st.columns(2)

            with context_button:
                if st.button(
                    "Completar Contexto",
                    key="recommended_context",
                    type="primary",
                    use_container_width=True,
                ):
                    switch_page(
                        "pages/4_Contexto.py"
                    )

            with territory_button:
                if st.button(
                    "Completar Territorio",
                    key="recommended_territory",
                    use_container_width=True,
                ):
                    switch_page(
                        "pages/5_Territorio.py"
                    )

        elif completion < 85:
            st.subheader(
                "Valida la lectura estratégica"
            )

            st.write(
                "Ya existe información suficiente para revisar "
                "riesgos, capitales e insights."
            )

            if st.button(
                "Revisar Dashboard",
                key="recommended_dashboard",
                type="primary",
                use_container_width=True,
            ):
                switch_page(
                    "pages/6_Dashboard.py"
                )

        else:
            st.subheader(
                "Prepara la presentación ejecutiva"
            )

            st.write(
                "El expediente cuenta con cobertura suficiente "
                "para producir el informe profesional."
            )

            if st.button(
                "Preparar informe",
                key="recommended_report",
                type="primary",
                use_container_width=True,
            ):
                switch_page(
                    "pages/8_Informe.py"
                )


with status_column:
    with st.container(border=True):
        st.caption(
            "ESTADO DEL EXPEDIENTE"
        )

        st.subheader(
            stage
        )

        st.progress(
            completion / 100
        )

        status_metrics = st.columns(3)

        with status_metrics[0]:
            st.metric(
                "Zonas",
                len(zones),
            )

        with status_metrics[1]:
            st.metric(
                "Destinos",
                len(valid_destinations),
            )

        with status_metrics[2]:
            st.metric(
                "Confianza",
                f"{confidence} %",
            )


# =========================================================
# INFORMACIÓN PENDIENTE
# =========================================================

if pending_items:
    section_header(
        "Cobertura",
        "Información pendiente",
    )

    pending_columns = st.columns(
        min(
            len(pending_items),
            3,
        )
    )

    for index, pending_item in enumerate(
        pending_items[:6]
    ):
        column_index = (
            index
            % len(pending_columns)
        )

        with pending_columns[column_index]:
            st.warning(
                pending_item
            )


# =========================================================
# HERRAMIENTAS
# =========================================================

section_header(
    "Herramientas",
    "Explora todos los módulos",
)

tool_columns = st.columns(4)

with tool_columns[0]:
    action_card(
        title="Destinos",
        description=(
            "Organiza, consulta y selecciona "
            "los expedientes del portafolio."
        ),
        status=f"{len(valid_destinations)} registrados",
        button_label="Abrir destinos",
        page_path="pages/1_Destinos.py",
        key="tool_destinations",
        icon="◇",
    )

with tool_columns[1]:
    action_card(
        title="Análisis",
        description=(
            "Consulta indicadores y resultados "
            "del motor cuantitativo."
        ),
        status="Indicadores calculados",
        button_label="Ver análisis",
        page_path="pages/3_Analisis.py",
        key="tool_analysis",
        icon="◉",
    )

with tool_columns[2]:
    action_card(
        title="Contexto",
        description=(
            "Incorpora percepción, gobernanza, "
            "reputación y resiliencia."
        ),
        status="Capitales cualitativos",
        button_label="Editar Contexto",
        page_path="pages/4_Contexto.py",
        key="tool_context",
        icon="◎",
    )

with tool_columns[3]:
    action_card(
        title="Territorio",
        description=(
            "Registra zonas, concentraciones "
            "y presiones territoriales."
        ),
        status=f"{len(zones)} zonas",
        button_label="Editar Territorio",
        page_path="pages/5_Territorio.py",
        key="tool_territory",
        icon="⌖",
    )


# =========================================================
# METODOLOGÍA Y CIERRE
# =========================================================

section_header(
    "Metodología Incubatour",
    "Analiza · Aprende · Adapta · Actúa",
)

with st.container(border=True):
    closing_text, closing_actions = st.columns(
        [1.8, 1],
        vertical_alignment="center",
    )

    with closing_text:
        st.subheader(
            "Le ponemos método a la complejidad turística"
        )

        st.write(
            "El Decision Lab no muestra únicamente cifras: "
            "explica qué significan y qué decisiones deben priorizarse."
        )

    with closing_actions:
        if st.button(
            "+ Crear nuevo diagnóstico",
            key="closing_new_diagnosis",
            type="primary",
            use_container_width=True,
        ):
            start_new_diagnosis()

        if st.button(
            "Abrir portafolio",
            key="closing_portfolio",
            use_container_width=True,
        ):
            switch_page(
                "pages/1_Destinos.py"
            )
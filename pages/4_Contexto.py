import streamlit as st

from context_repository import (
    calculate_context_completeness,
    get_context,
    init_context_table,
    save_context,
)
from database import (
    get_destination,
    init_db,
    list_destinations,
)
from styles import apply_incubatour_theme


st.set_page_config(
    page_title="Contexto del destino",
    page_icon="◆",
    layout="wide",
)

apply_incubatour_theme()
init_db()
init_context_table()


# =========================================================
# CATÁLOGOS
# =========================================================

RELACION_OPTIONS = [
    "Sin evaluar",
    "Muy positiva",
    "Positiva",
    "Neutral",
    "Tensa",
    "Muy conflictiva",
]

CONFLICTOS_OPTIONS = [
    "Sin evaluar",
    "No existen conflictos visibles",
    "Existen casos aislados",
    "Existen tensiones recurrentes",
    "Existen protestas o conflictos organizados",
]

PREOCUPACIONES_SOCIALES = [
    "Acceso y precio de la vivienda",
    "Ruido y convivencia",
    "Congestión del espacio público",
    "Pérdida del comercio local",
    "Aumento del coste de vida",
    "Pérdida de identidad",
    "Empleo precario o estacional",
    "Distribución desigual de beneficios",
    "Presión ambiental",
    "No se identifican preocupaciones relevantes",
]

PARTICIPACION_OPTIONS = [
    "Sin evaluar",
    "Alta y permanente",
    "Existe, pero es puntual",
    "Limitada",
    "Inexistente",
]

YES_NO_OPTIONS = [
    "Sin evaluar",
    "Sí",
    "Parcialmente",
    "No",
]

TEAM_OPTIONS = [
    "Sin evaluar",
    "Equipo consolidado y especializado",
    "Equipo suficiente, pero limitado",
    "Equipo reducido",
    "No existe un equipo específico",
]

COORDINATION_OPTIONS = [
    "Sin evaluar",
    "Alta y estructurada",
    "Frecuente, pero informal",
    "Puntual",
    "Inexistente",
]

POSITIONING_OPTIONS = [
    "Sin evaluar",
    "Emergente",
    "En crecimiento",
    "Consolidado",
    "Premium",
    "Masificado",
    "En recuperación",
    "En reposicionamiento",
]

REPUTATION_OPTIONS = [
    "Sin evaluar",
    "Muy positiva",
    "Positiva",
    "Mixta",
    "Deteriorada",
    "En crisis",
]

REPUTATIONAL_EVENTS = [
    "Desastres naturales",
    "Incendios",
    "Inundaciones",
    "Sequía o falta de agua",
    "Crisis sanitaria",
    "Inseguridad",
    "Accidentes relevantes",
    "Protestas ciudadanas",
    "Cobertura mediática negativa",
    "Crisis política o institucional",
    "Saturación o masificación",
    "Ninguno",
]

RECOVERY_OPTIONS = [
    "Sin evaluar",
    "Muy alta",
    "Alta",
    "Media",
    "Baja",
    "Muy baja",
]

DIVERSIFICATION_OPTIONS = [
    "Sin evaluar",
    "Muy diversificada",
    "Diversificada",
    "Moderadamente concentrada",
    "Muy dependiente de pocos mercados",
]

DEPENDENCY_OPTIONS = [
    "Sin evaluar",
    "Baja",
    "Media",
    "Alta",
    "Muy alta",
]

REDISTRIBUTION_OPTIONS = [
    "Sin evaluar",
    "Alta",
    "Media",
    "Baja",
    "Inexistente",
]


def safe_index(
    options: list[str],
    value: str | None,
) -> int:
    if value in options:
        return options.index(value)

    return 0


# =========================================================
# DESTINO ACTIVO
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


labels = {
    (
        f"{destination['municipio']} · "
        f"{destination.get('provincia', '')}"
    ): destination["id"]
    for destination in destinations
}

active_id = st.session_state.get(
    "active_destination_id"
)

default_index = 0

if active_id in labels.values():
    default_index = list(
        labels.values()
    ).index(active_id)


st.caption("APRENDE · CONTEXTO CUALITATIVO")

st.title("Contexto del destino")

st.write(
    "Esta sección incorpora variables que no pueden "
    "obtenerse únicamente mediante estadísticas: "
    "percepción social, gobernanza, reputación y resiliencia."
)

selected_label = st.selectbox(
    "Destino",
    options=list(labels.keys()),
    index=default_index,
)

destination_id = labels[selected_label]

st.session_state[
    "active_destination_id"
] = destination_id

destination = get_destination(
    destination_id
)

current = get_context(
    destination_id
) or {}

completeness = (
    calculate_context_completeness(
        current
    )
)


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

    st.progress(
        completeness / 100
    )

    st.write(
        f"Contexto cualitativo completado: "
        f"**{completeness} %**"
    )


social_tab, institutional_tab, reputation_tab, resilience_tab = st.tabs(
    [
        "Capital social",
        "Capital institucional",
        "Capital reputacional",
        "Capital de resiliencia",
    ]
)


with st.form(
    "context_form",
    clear_on_submit=False,
):

    # =====================================================
    # CAPITAL SOCIAL
    # =====================================================

    with social_tab:
        st.subheader("Capital social")

        st.write(
            "Evalúa la relación entre actividad turística, "
            "residentes y calidad de vida."
        )

        relacion_residentes_visitantes = st.selectbox(
            "Relación actual entre residentes y visitantes",
            options=RELACION_OPTIONS,
            index=safe_index(
                RELACION_OPTIONS,
                current.get(
                    "relacion_residentes_visitantes"
                ),
            ),
        )

        conflictos_turisticos = st.selectbox(
            "Nivel de conflicto social relacionado con el turismo",
            options=CONFLICTOS_OPTIONS,
            index=safe_index(
                CONFLICTOS_OPTIONS,
                current.get(
                    "conflictos_turisticos"
                ),
            ),
        )

        preocupaciones_sociales = st.multiselect(
            "Principales preocupaciones ciudadanas",
            options=PREOCUPACIONES_SOCIALES,
            default=current.get(
                "preocupaciones_sociales",
                [],
            ),
        )

        participacion_ciudadana = st.selectbox(
            "Participación ciudadana en las decisiones turísticas",
            options=PARTICIPACION_OPTIONS,
            index=safe_index(
                PARTICIPACION_OPTIONS,
                current.get(
                    "participacion_ciudadana"
                ),
            ),
        )

    # =====================================================
    # CAPITAL INSTITUCIONAL
    # =====================================================

    with institutional_tab:
        st.subheader("Capital institucional")

        st.write(
            "Evalúa la capacidad del destino para "
            "planificar, reaccionar y ejecutar decisiones."
        )

        estrategia_turistica = st.selectbox(
            "¿Existe una estrategia turística vigente?",
            options=YES_NO_OPTIONS,
            index=safe_index(
                YES_NO_OPTIONS,
                current.get(
                    "estrategia_turistica"
                ),
            ),
        )

        observatorio_turistico = st.selectbox(
            "¿Existe observatorio o sistema estable de indicadores?",
            options=YES_NO_OPTIONS,
            index=safe_index(
                YES_NO_OPTIONS,
                current.get(
                    "observatorio_turistico"
                ),
            ),
        )

        equipo_tecnico = st.selectbox(
            "Capacidad del equipo técnico de turismo",
            options=TEAM_OPTIONS,
            index=safe_index(
                TEAM_OPTIONS,
                current.get(
                    "equipo_tecnico"
                ),
            ),
        )

        coordinacion_publico_privada = st.selectbox(
            "Coordinación público-privada",
            options=COORDINATION_OPTIONS,
            index=safe_index(
                COORDINATION_OPTIONS,
                current.get(
                    "coordinacion_publico_privada"
                ),
            ),
        )

    # =====================================================
    # CAPITAL REPUTACIONAL
    # =====================================================

    with reputation_tab:
        st.subheader("Capital reputacional")

        st.write(
            "Evalúa la imagen actual del destino y "
            "los acontecimientos que pueden afectarla."
        )

        posicionamiento_destino = st.selectbox(
            "Posicionamiento actual del destino",
            options=POSITIONING_OPTIONS,
            index=safe_index(
                POSITIONING_OPTIONS,
                current.get(
                    "posicionamiento_destino"
                ),
            ),
        )

        reputacion_actual = st.selectbox(
            "Reputación turística actual",
            options=REPUTATION_OPTIONS,
            index=safe_index(
                REPUTATION_OPTIONS,
                current.get(
                    "reputacion_actual"
                ),
            ),
        )

        eventos_reputacionales = st.multiselect(
            "Eventos que han afectado al destino en los últimos tres años",
            options=REPUTATIONAL_EVENTS,
            default=current.get(
                "eventos_reputacionales",
                [],
            ),
        )

        recuperacion_imagen = st.selectbox(
            "Capacidad para recuperar o proteger la imagen",
            options=RECOVERY_OPTIONS,
            index=safe_index(
                RECOVERY_OPTIONS,
                current.get(
                    "recuperacion_imagen"
                ),
            ),
        )

    # =====================================================
    # CAPITAL DE RESILIENCIA
    # =====================================================

    with resilience_tab:
        st.subheader("Capital de resiliencia")

        st.write(
            "Evalúa la preparación del destino para "
            "adaptarse a crisis, cambios de mercado "
            "y nuevas condiciones territoriales."
        )

        plan_crisis = st.selectbox(
            "¿Existe un plan de crisis o contingencia turística?",
            options=YES_NO_OPTIONS,
            index=safe_index(
                YES_NO_OPTIONS,
                current.get(
                    "plan_crisis"
                ),
            ),
        )

        diversificacion_mercados = st.selectbox(
            "Diversificación de mercados y segmentos",
            options=DIVERSIFICATION_OPTIONS,
            index=safe_index(
                DIVERSIFICATION_OPTIONS,
                current.get(
                    "diversificacion_mercados"
                ),
            ),
        )

        dependencia_estacional = st.selectbox(
            "Dependencia percibida de la temporada alta",
            options=DEPENDENCY_OPTIONS,
            index=safe_index(
                DEPENDENCY_OPTIONS,
                current.get(
                    "dependencia_estacional"
                ),
            ),
        )

        capacidad_redistribucion = st.selectbox(
            "Capacidad de redistribuir visitantes hacia otras zonas o periodos",
            options=REDISTRIBUTION_OPTIONS,
            index=safe_index(
                REDISTRIBUTION_OPTIONS,
                current.get(
                    "capacidad_redistribucion"
                ),
            ),
        )

    st.divider()

    notas_contexto = st.text_area(
        "Notas cualitativas adicionales",
        value=current.get(
            "notas_contexto",
            "",
        ),
        placeholder=(
            "Incluye información política, social, "
            "ambiental o reputacional que ayude "
            "a interpretar las respuestas."
        ),
        height=140,
    )

    submitted = st.form_submit_button(
        "Guardar contexto",
        type="primary",
        use_container_width=True,
    )


if submitted:
    save_context(
        destination_id,
        {
            "relacion_residentes_visitantes":
                relacion_residentes_visitantes,
            "conflictos_turisticos":
                conflictos_turisticos,
            "preocupaciones_sociales":
                preocupaciones_sociales,
            "participacion_ciudadana":
                participacion_ciudadana,

            "estrategia_turistica":
                estrategia_turistica,
            "observatorio_turistico":
                observatorio_turistico,
            "equipo_tecnico":
                equipo_tecnico,
            "coordinacion_publico_privada":
                coordinacion_publico_privada,

            "posicionamiento_destino":
                posicionamiento_destino,
            "reputacion_actual":
                reputacion_actual,
            "eventos_reputacionales":
                eventos_reputacionales,
            "recuperacion_imagen":
                recuperacion_imagen,

            "plan_crisis":
                plan_crisis,
            "diversificacion_mercados":
                diversificacion_mercados,
            "dependencia_estacional":
                dependencia_estacional,
            "capacidad_redistribucion":
                capacidad_redistribucion,

            "notas_contexto":
                notas_contexto,
        },
    )

    updated_context = get_context(
        destination_id
    ) or {}

    updated_completeness = (
        calculate_context_completeness(
            updated_context
        )
    )

    st.session_state["contexto_guardado"] = {
        "destination_id": destination_id,
        "completeness": updated_completeness,
    }

    st.rerun()


# =========================================================
# CONFIRMACIÓN Y NAVEGACIÓN POSTERIOR AL GUARDADO
# =========================================================

saved_context_state = st.session_state.get(
    "contexto_guardado"
)

if (
    saved_context_state
    and saved_context_state.get("destination_id")
    == destination_id
):
    saved_completeness = int(
        saved_context_state.get(
            "completeness",
            0,
        )
    )

    with st.container(border=True):
        st.success(
            "Contexto cualitativo guardado correctamente."
        )

        status_col, progress_col = st.columns(
            [1.45, 1],
            vertical_alignment="center",
        )

        with status_col:
            if saved_completeness == 100:
                st.subheader("Contexto completo")
                st.write(
                    "Los cuatro capitales cualitativos ya están "
                    "listos para incorporarse al análisis del destino."
                )
            else:
                st.subheader("Contexto guardado")
                st.write(
                    "Puedes avanzar a Territorio y volver después "
                    "para completar las variables pendientes."
                )

        with progress_col:
            st.metric(
                "Completitud",
                f"{saved_completeness} %",
            )
            st.progress(
                saved_completeness / 100
            )

        action1, action2 = st.columns(
            [1.25, 1]
        )

        with action1:
            if st.button(
                "Continuar a Territorio",
                type="primary",
                use_container_width=True,
                key="context_continue_to_territory",
            ):
                st.session_state.pop(
                    "contexto_guardado",
                    None,
                )
                st.switch_page(
                    "pages/5_Territorio.py"
                )

        with action2:
            if st.button(
                "Volver al análisis",
                use_container_width=True,
                key="context_back_to_analysis",
            ):
                st.session_state.pop(
                    "contexto_guardado",
                    None,
                )
                st.switch_page(
                    "pages/3_Analisis.py"
                )

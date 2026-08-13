import streamlit as st

from calculations import calculate_completeness
from database import (
    get_destination,
    init_db,
    list_destinations,
    save_destination,
)
from styles import apply_incubatour_theme


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Expediente del destino",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_incubatour_theme()
init_db()


# =========================================================
# CATÁLOGOS
# =========================================================

MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

TIPOLOGIAS = [
    "Urbano / ciudad",
    "Cultural y patrimonial",
    "Sol y playa",
    "Naturaleza",
    "Rural",
    "Gastronómico",
    "Negocios y reuniones",
    "Bienestar",
    "Deportivo",
    "Religioso",
]

IMPACTOS = [
    "Congestión y saturación del espacio público",
    "Presión sobre la vivienda",
    "Aumento del coste de vida",
    "Conflictos entre residentes y visitantes",
    "Presión ambiental",
    "Movilidad insuficiente",
    "Concentración de visitantes en pocas zonas",
    "Dependencia económica del turismo",
    "Estacionalidad laboral",
    "Pérdida de identidad local",
]

INFRAESTRUCTURA_OPTIONS = [
    "No evaluada",
    "Alta — funciona con margen incluso en temporada alta",
    "Media — presenta tensiones puntuales",
    "Baja — la demanda supera frecuentemente la capacidad",
]

FRAGILIDAD_OPTIONS = [
    "No evaluada",
    "Baja — territorio resistente a la presión turística",
    "Media — existen espacios o recursos sensibles",
    "Alta — territorio especialmente vulnerable",
]

ACEPTACION_OPTIONS = [
    "No evaluada",
    "Alta — predominan beneficios percibidos",
    "Media — existen tensiones en grupos o zonas concretas",
    "Baja — existen rechazo o conflictos frecuentes",
]

GESTION_OPTIONS = [
    "No evaluada",
    "Avanzada — existen medidas, monitoreo y protocolos",
    "Parcial — existen algunas medidas aisladas",
    "Inexistente — no hay gestión activa de visitantes",
]

VIVIENDAS_OPTIONS = [
    "Sin información",
    "Menos del 5 %",
    "Entre 5 % y 10 %",
    "Entre 10 % y 20 %",
    "Entre 20 % y 30 %",
    "Más del 30 %",
]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def safe_index(options: list[str], value: str | None) -> int:
    if value in options:
        return options.index(value)
    return 0


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def field_label(
    title: str,
    description: str = "",
    required: bool = False,
) -> None:
    """
    Crea una etiqueta propia, siempre visible,
    independientemente del tema de Streamlit.
    """

    required_text = (
        '<span style="color:#F52F8B;"> *</span>'
        if required
        else ""
    )

    description_html = (
        f"""
        <div style="
            color:#73737C;
            font-size:0.78rem;
            line-height:1.45;
            margin-top:0.18rem;
            margin-bottom:0.5rem;
        ">
            {description}
        </div>
        """
        if description
        else '<div style="margin-bottom:0.35rem;"></div>'
    )

    st.markdown(
        f"""
        <div style="
            color:#18181B;
            font-size:0.88rem;
            font-weight:750;
            line-height:1.35;
        ">
            {title}{required_text}
        </div>
        {description_html}
        """,
        unsafe_allow_html=True,
    )


def render_completeness_panel(destination: dict) -> None:
    completeness, missing_fields = calculate_completeness(destination)

    st.markdown("### Estado del expediente")

    progress_col, status_col = st.columns([2.2, 1])

    with progress_col:
        st.progress(completeness / 100)
        st.caption(f"Completitud del diagnóstico: {completeness} %")

    with status_col:
        if completeness == 100:
            st.success("Expediente completo")
        elif completeness >= 70:
            st.warning("Casi listo")
        else:
            st.info("En construcción")

    if missing_fields:
        with st.expander("Información pendiente"):
            for item in missing_fields:
                st.write(f"• {item}")

    st.divider()


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    """
    <div class="section-kicker">Analiza</div>

    <div class="section-title">
        Expediente del destino
    </div>

    <p class="section-copy">
        Integra los datos oficiales, la entrevista inicial y la evidencia
        territorial que sostendrán el diagnóstico y la toma de decisiones.
    </p>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SELECCIÓN DE EXPEDIENTE
# =========================================================

destinations = list_destinations()

destination_options = {
    "Crear un nuevo diagnóstico": None,
    **{
        (
            f"{item['municipio']} · "
            f"actualizado {str(item.get('updated_at', ''))[:10]}"
        ): item["id"]
        for item in destinations
    },
}

field_label(
    "Expediente que deseas abrir",
    "Selecciona un destino existente o inicia un diagnóstico nuevo.",
)

selected_label = st.selectbox(
    "Expediente",
    options=list(destination_options.keys()),
    label_visibility="collapsed",
)

selected_id = destination_options[selected_label]

current = get_destination(selected_id) if selected_id else None
current = current or {}

if selected_id:
    st.caption(
        f"Editando el expediente de "
        f"{current.get('municipio', '')}. "
        "Los cambios se guardarán en este mismo diagnóstico."
    )

    render_completeness_panel(current)


# =========================================================
# FORMULARIO
# =========================================================

with st.form(
    "destination_record",
    clear_on_submit=False,
):

    # =====================================================
    # 1. IDENTIFICACIÓN
    # =====================================================

    st.markdown("## 1. Identificación y contexto")
    st.caption(
        "Define qué destino se analiza, dónde se encuentra "
        "y cuál es su posicionamiento turístico."
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        field_label(
            "Municipio o destino turístico",
            "Nombre oficial del municipio o unidad territorial analizada.",
            required=True,
        )

        municipio = st.text_input(
            "Municipio",
            value=current.get("municipio", ""),
            placeholder="Ej. San Sebastián / Donostia",
            label_visibility="collapsed",
        )

    with col2:
        field_label(
            "Provincia",
            "Provincia española en la que se localiza.",
        )

        provincia = st.text_input(
            "Provincia",
            value=current.get("provincia", ""),
            placeholder="Ej. Gipuzkoa",
            label_visibility="collapsed",
        )

    with col3:
        field_label(
            "Comunidad Autónoma",
            "Comunidad Autónoma a la que pertenece.",
        )

        comunidad_autonoma = st.text_input(
            "Comunidad Autónoma",
            value=current.get("comunidad_autonoma", ""),
            placeholder="Ej. País Vasco",
            label_visibility="collapsed",
        )

    col1, col2 = st.columns([1, 2])

    with col1:
        field_label(
            "Año de referencia",
            "Año principal al que corresponden los datos.",
        )

        anio_referencia = st.number_input(
            "Año",
            min_value=2000,
            max_value=2100,
            value=safe_int(
                current.get("anio_referencia"),
                default=2026,
            ),
            step=1,
            label_visibility="collapsed",
        )

    with col2:
        field_label(
            "Tipología turística del destino",
            "Puedes seleccionar varias categorías.",
        )

        tipologias = st.multiselect(
            "Tipología",
            options=TIPOLOGIAS,
            default=current.get("tipologias", []),
            placeholder="Selecciona una o varias tipologías",
            label_visibility="collapsed",
        )

    field_label(
        "Propuesta de valor turística",
        (
            "Resume en dos o tres líneas qué hace diferente al destino, "
            "qué experiencias ofrece y a qué públicos atrae."
        ),
    )

    propuesta_valor = st.text_area(
        "Propuesta de valor",
        value=current.get("propuesta_valor", ""),
        placeholder=(
            "Ej. Destino urbano costero reconocido por su gastronomía, "
            "playas, patrimonio, festivales y calidad de vida."
        ),
        height=110,
        label_visibility="collapsed",
    )

    # =====================================================
    # 2. DEMANDA Y OFERTA
    # =====================================================

    st.divider()
    st.markdown("## 2. Demanda y oferta turística")
    st.caption(
        "Introduce cifras anuales completas, sin puntos ni abreviaturas. "
        "Por ejemplo: 3200000, no 3.2 M."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        field_label(
            "Población residente",
            "Número total de habitantes del municipio.",
        )

        poblacion_residente = st.number_input(
            "Población residente",
            min_value=0,
            value=safe_int(
                current.get("poblacion_residente"),
            ),
            step=1,
            format="%d",
            label_visibility="collapsed",
        )

        field_label(
            "Número de visitantes anuales",
            (
                "Personas que visitaron el destino durante el último "
                "año disponible, incluyan o no pernocta."
            ),
        )

        visitantes_anuales = st.number_input(
            "Visitantes anuales",
            min_value=0,
            value=safe_int(
                current.get("visitantes_anuales"),
            ),
            step=1000,
            format="%d",
            label_visibility="collapsed",
        )

    with col2:
        field_label(
            "Número de excursionistas anuales",
            (
                "Visitantes de día que llegan al destino, "
                "pero no pasan la noche."
            ),
        )

        excursionistas_anuales = st.number_input(
            "Excursionistas",
            min_value=0,
            value=safe_int(
                current.get("excursionistas_anuales"),
            ),
            step=1000,
            format="%d",
            label_visibility="collapsed",
        )

        field_label(
            "Número de pernoctaciones anuales",
            (
                "Total de noches registradas en alojamientos turísticos "
                "durante el último año disponible."
            ),
        )

        pernoctaciones_anuales = st.number_input(
            "Pernoctaciones",
            min_value=0,
            value=safe_int(
                current.get("pernoctaciones_anuales"),
            ),
            step=1000,
            format="%d",
            label_visibility="collapsed",
        )

    with col3:
        field_label(
            "Número total de plazas de alojamiento",
            (
                "Capacidad estimada de hoteles, hostales, apartamentos, "
                "viviendas turísticas y otros alojamientos."
            ),
        )

        plazas_alojamiento = st.number_input(
            "Plazas de alojamiento",
            min_value=0,
            value=safe_int(
                current.get("plazas_alojamiento"),
            ),
            step=100,
            format="%d",
            label_visibility="collapsed",
        )

        field_label(
            "Meses de temporada alta",
            "Selecciona todos los meses de mayor concentración turística.",
        )

        meses_temporada_alta = st.multiselect(
            "Meses de mayor afluencia",
            options=MESES,
            default=current.get(
                "meses_temporada_alta",
                [],
            ),
            placeholder="Selecciona los meses pico",
            label_visibility="collapsed",
        )

    # =====================================================
    # 3. CAPACIDAD
    # =====================================================

    st.divider()
    st.markdown("## 3. Capacidad del destino")
    st.caption(
        "Valora la situación actual, no la capacidad potencial futura."
    )

    col1, col2 = st.columns(2)

    with col1:
        field_label(
            "Capacidad de la infraestructura turística",
            (
                "Evalúa movilidad, servicios, señalización, espacio público, "
                "equipamientos y capacidad de atención en temporada alta."
            ),
        )

        infraestructura = st.selectbox(
            "Infraestructura",
            options=INFRAESTRUCTURA_OPTIONS,
            index=safe_index(
                INFRAESTRUCTURA_OPTIONS,
                current.get("infraestructura"),
            ),
            label_visibility="collapsed",
        )

        field_label(
            "Fragilidad ambiental del territorio",
            (
                "Evalúa la sensibilidad de playas, áreas naturales, "
                "patrimonio, residuos, agua y espacios de uso intensivo."
            ),
        )

        fragilidad_ambiental = st.selectbox(
            "Fragilidad ambiental",
            options=FRAGILIDAD_OPTIONS,
            index=safe_index(
                FRAGILIDAD_OPTIONS,
                current.get("fragilidad_ambiental"),
            ),
            label_visibility="collapsed",
        )

    with col2:
        field_label(
            "Aceptación social del turismo",
            (
                "Valora el apoyo, tolerancia o rechazo de la población "
                "residente hacia la actividad turística."
            ),
        )

        aceptacion_social = st.selectbox(
            "Aceptación social",
            options=ACEPTACION_OPTIONS,
            index=safe_index(
                ACEPTACION_OPTIONS,
                current.get("aceptacion_social"),
            ),
            label_visibility="collapsed",
        )

        field_label(
            "Nivel de gestión de visitantes y aforos",
            (
                "Considera control de accesos, reservas, monitoreo, "
                "movilidad, información y redistribución de flujos."
            ),
        )

        gestion_flujos = st.selectbox(
            "Gestión de visitantes",
            options=GESTION_OPTIONS,
            index=safe_index(
                GESTION_OPTIONS,
                current.get("gestion_flujos"),
            ),
            label_visibility="collapsed",
        )

    field_label(
        "Porcentaje estimado de viviendas turísticas en zonas centrales",
        (
            "Indica el peso aproximado de viviendas de uso turístico "
            "en el centro o en las zonas más visitadas."
        ),
    )

    viviendas_turisticas = st.selectbox(
        "Viviendas turísticas",
        options=VIVIENDAS_OPTIONS,
        index=safe_index(
            VIVIENDAS_OPTIONS,
            current.get("viviendas_turisticas"),
        ),
        label_visibility="collapsed",
    )

    field_label(
        "Principales impactos turísticos observados",
        (
            "Selecciona los problemas o tensiones que ya se presentan "
            "en el destino."
        ),
    )

    impactos = st.multiselect(
        "Impactos turísticos",
        options=IMPACTOS,
        default=current.get("impactos", []),
        placeholder="Selecciona todos los impactos identificados",
        label_visibility="collapsed",
    )

    # =====================================================
    # 4. EVIDENCIA
    # =====================================================

    st.divider()
    st.markdown("## 4. Evidencia e interpretación inicial")
    st.caption(
        "Registra la procedencia de los datos y la información cualitativa "
        "obtenida durante la entrevista."
    )

    field_label(
        "Fuentes utilizadas y año de actualización",
        (
            "Especifica qué datos son oficiales, cuáles son municipales "
            "y cuáles son estimaciones."
        ),
    )

    fuente_datos = st.text_area(
        "Fuentes",
        value=current.get("fuente_datos", ""),
        placeholder=(
            "Ej. INE 2025; Observatorio Turístico Municipal 2025; "
            "Registro autonómico de viviendas turísticas; "
            "estimación del área de turismo."
        ),
        height=110,
        label_visibility="collapsed",
    )

    field_label(
        "Notas de la entrevista inicial",
        (
            "Incluye preocupaciones del municipio, conflictos, proyectos, "
            "eventos extraordinarios, demandas del sector y contexto político."
        ),
    )

    observaciones = st.text_area(
        "Observaciones",
        value=current.get("observaciones", ""),
        placeholder=(
            "Ej. El municipio identifica saturación en el casco histórico "
            "durante fines de semana y preocupación vecinal por ruido "
            "y viviendas turísticas."
        ),
        height=160,
        label_visibility="collapsed",
    )

    st.caption("* Campo obligatorio")

    submitted = st.form_submit_button(
        "Guardar expediente",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# GUARDADO
# =========================================================

if submitted:

    if not municipio.strip():
        st.error(
            "Es necesario indicar el municipio antes de guardar."
        )

    else:
        record = {
            "municipio": municipio,
            "provincia": provincia,
            "comunidad_autonoma": comunidad_autonoma,
            "pais": "España",
            "anio_referencia": anio_referencia,
            "tipologias": tipologias,
            "propuesta_valor": propuesta_valor,
            "poblacion_residente": poblacion_residente,
            "visitantes_anuales": visitantes_anuales,
            "excursionistas_anuales": excursionistas_anuales,
            "pernoctaciones_anuales": pernoctaciones_anuales,
            "plazas_alojamiento": plazas_alojamiento,
            "meses_temporada_alta": meses_temporada_alta,
            "infraestructura": infraestructura,
            "fragilidad_ambiental": fragilidad_ambiental,
            "aceptacion_social": aceptacion_social,
            "gestion_flujos": gestion_flujos,
            "viviendas_turisticas": viviendas_turisticas,
            "impactos": impactos,
            "fuente_datos": fuente_datos,
            "observaciones": observaciones,
        }

        saved_id = save_destination(
            record,
            destination_id=selected_id,
        )

        st.session_state["active_destination_id"] = saved_id

        saved_destination = get_destination(saved_id) or {}

        completeness, missing_fields = calculate_completeness(
            saved_destination
        )

        # Guardamos el resultado en session_state porque al pulsar otro botón
        # Streamlit ejecuta toda la página nuevamente y submitted vuelve a False.
        st.session_state["diagnostico_guardado"] = {
            "destination_id": saved_id,
            "municipio": municipio,
            "completeness": completeness,
            "missing_fields": missing_fields,
        }

        st.rerun()


# =========================================================
# CONFIRMACIÓN Y NAVEGACIÓN POSTERIOR AL GUARDADO
# =========================================================

saved_state = st.session_state.get("diagnostico_guardado")

if saved_state:
    saved_municipio = saved_state.get("municipio", "Destino")
    saved_completeness = int(saved_state.get("completeness", 0))
    saved_missing_fields = saved_state.get("missing_fields", [])

    with st.container(border=True):

        st.success(
            f"Expediente de {saved_municipio} guardado correctamente."
        )

        left, right = st.columns(
            [1.5, 1],
            vertical_alignment="center",
        )

        with left:
            if saved_completeness == 100:
                st.subheader("Expediente completo")
                st.write(
                    "La información general ya quedó lista. "
                    "Ahora registra las zonas y presiones "
                    "territoriales del destino."
                )
            else:
                st.subheader("Expediente guardado")
                st.write(
                    "Puedes avanzar a Territorio y volver después "
                    "para completar la información pendiente."
                )

        with right:
            st.metric(
                "Completitud",
                f"{saved_completeness} %",
            )
            st.progress(saved_completeness / 100)

        if saved_missing_fields:
            with st.expander("Información pendiente"):
                for item in saved_missing_fields:
                    st.write(f"• {item}")

        next_col, edit_col = st.columns([1.3, 1])

        with next_col:
            if st.button(
                "Continuar a Territorio",
                type="primary",
                use_container_width=True,
                key="continue_to_territory",
            ):
                st.session_state.pop("diagnostico_guardado", None)
                st.switch_page("pages/5_Territorio.py")

        with edit_col:
            if st.button(
                "Seguir editando",
                use_container_width=True,
                key="continue_editing",
            ):
                st.session_state.pop("diagnostico_guardado", None)
                st.rerun()

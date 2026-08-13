import pandas as pd
import pydeck as pdk
import streamlit as st

from calculations import (
    calculate_zone_priority,
    generate_zone_recommendation,
)
from database import (
    delete_zone,
    get_destination,
    get_zone,
    init_db,
    list_destinations,
    list_zones,
    save_zone,
)
from styles import apply_incubatour_theme


st.set_page_config(
    page_title="Territorio",
    page_icon="◆",
    layout="wide",
)

apply_incubatour_theme()
init_db()


ZONE_TYPES = [
    "Centro histórico",
    "Barrio residencial",
    "Playa o litoral",
    "Espacio natural",
    "Área comercial",
    "Zona gastronómica",
    "Equipamiento cultural",
    "Zona de eventos",
    "Puerto o terminal",
    "Mirador o atractivo",
    "Área rural",
    "Otro",
]

PRESSURE_OPTIONS = [
    "No evaluada",
    "Baja",
    "Media",
    "Alta",
    "Crítica",
]

FRAGILITY_OPTIONS = [
    "No evaluada",
    "Baja",
    "Media",
    "Alta",
]

INFRASTRUCTURE_OPTIONS = [
    "No evaluada",
    "Alta",
    "Media",
    "Baja",
]

ZONE_IMPACTS = [
    "Congestión del espacio público",
    "Ruido y molestias vecinales",
    "Presión sobre la vivienda",
    "Residuos y suciedad",
    "Movilidad insuficiente",
    "Erosión o deterioro ambiental",
    "Pérdida de identidad local",
    "Saturación de servicios",
    "Concentración en horarios concretos",
    "Conflicto entre usos turísticos y residenciales",
]


def safe_index(options: list[str], value: str | None) -> int:
    return options.index(value) if value in options else 0


def safe_float(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


destinations = list_destinations()

if not destinations:
    st.warning("Primero debes crear un expediente de destino.")

    if st.button("Crear expediente", type="primary"):
        st.switch_page("pages/2_Diagnostico.py")

    st.stop()


labels = {
    f"{item['municipio']} · {item.get('provincia', '')}": item["id"]
    for item in destinations
}

active_id = st.session_state.get("active_destination_id")

default_index = 0

if active_id in labels.values():
    default_index = list(labels.values()).index(active_id)


st.title("Lectura territorial")

st.write(
    "Identifica dónde se concentra la presión turística, qué zonas "
    "presentan mayor fragilidad y dónde debe priorizarse la intervención."
)

selected_label = st.selectbox(
    "Destino",
    list(labels.keys()),
    index=default_index,
)

destination_id = labels[selected_label]
st.session_state["active_destination_id"] = destination_id

destination = get_destination(destination_id)
zones = list_zones(destination_id)


with st.container(border=True):
    st.subheader(destination.get("municipio", "Destino sin nombre"))

    location = " · ".join(
        value
        for value in [
            destination.get("provincia", ""),
            destination.get("comunidad_autonoma", ""),
        ]
        if value
    )

    if location:
        st.caption(location)

    if destination.get("tipologias"):
        st.write(
            "**Tipología:** "
            + " · ".join(destination["tipologias"])
        )


total_zones = len(zones)
critical_zones = sum(
    zone.get("prioridad_nivel") == "Crítica"
    for zone in zones
)
high_zones = sum(
    zone.get("prioridad_nivel") == "Alta"
    for zone in zones
)
mapped_zones = sum(
    bool(zone.get("latitud")) and bool(zone.get("longitud"))
    for zone in zones
)


metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("Zonas registradas", total_zones)
metric2.metric("Prioridad crítica", critical_zones)
metric3.metric("Prioridad alta", high_zones)
metric4.metric("Zonas en el mapa", mapped_zones)


map_tab, zones_tab, form_tab = st.tabs(
    [
        "Mapa territorial",
        "Zonas registradas",
        "Agregar o editar zona",
    ]
)


with map_tab:
    st.subheader("Mapa de presión y prioridad")

    valid_zones = [
        zone
        for zone in zones
        if zone.get("latitud")
        and zone.get("longitud")
    ]

    if not valid_zones:
        st.info(
            "Todavía no hay zonas con coordenadas válidas."
        )

    else:
        colors = {
            "Baja": [22, 131, 90, 190],
            "Media": [231, 162, 26, 200],
            "Alta": [227, 108, 45, 210],
            "Crítica": [200, 62, 77, 220],
        }

        rows = []

        for zone in valid_zones:
            level = zone.get("prioridad_nivel", "Baja")

            rows.append(
                {
                    "nombre": zone.get("nombre", ""),
                    "tipo_zona": zone.get("tipo_zona", ""),
                    "latitud": float(zone["latitud"]),
                    "longitud": float(zone["longitud"]),
                    "presion": zone.get("presion", ""),
                    "fragilidad": zone.get("fragilidad", ""),
                    "infraestructura": zone.get("infraestructura", ""),
                    "prioridad": level,
                    "score": int(zone.get("prioridad_score", 0)),
                    "recomendacion": zone.get("recomendacion", ""),
                    "color": colors.get(
                        level,
                        [102, 112, 133, 180],
                    ),
                    "radius": (
                        60
                        + int(zone.get("prioridad_score", 0)) * 5
                    ),
                }
            )

        map_df = pd.DataFrame(rows)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["longitud", "latitud"],
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=8,
            radius_max_pixels=28,
            pickable=True,
            auto_highlight=True,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=map_df["latitud"].mean(),
                longitude=map_df["longitud"].mean(),
                zoom=11,
            ),
            tooltip={
                "html": """
                <b>{nombre}</b><br/>
                Tipo: {tipo_zona}<br/>
                Presión: {presion}<br/>
                Fragilidad: {fragilidad}<br/>
                Infraestructura: {infraestructura}<br/>
                Prioridad: {prioridad} ({score}/100)<br/><br/>
                {recomendacion}
                """
            },
            map_style=None,
        )

        st.pydeck_chart(
            deck,
            use_container_width=True,
        )


with zones_tab:
    st.subheader("Zonas registradas")

    if not zones:
        st.info("Todavía no has registrado ninguna zona.")

    for zone in zones:
        zone_id = int(zone["id"])

        with st.container(border=True):
            header_col, status_col = st.columns([3, 1])

            with header_col:
                st.subheader(zone.get("nombre", "Zona sin nombre"))
                st.caption(zone.get("tipo_zona", ""))

            with status_col:
                st.metric(
                    "Prioridad",
                    zone.get("prioridad_nivel", "Sin evaluar"),
                )

            metric1, metric2, metric3, metric4 = st.columns(4)

            metric1.metric(
                "Score",
                int(zone.get("prioridad_score", 0)),
            )

            metric2.metric(
                "Presión",
                zone.get("presion", ""),
            )

            metric3.metric(
                "Fragilidad",
                zone.get("fragilidad", ""),
            )

            metric4.metric(
                "Infraestructura",
                zone.get("infraestructura", ""),
            )

            st.write(
                "**Recomendación inicial:** "
                + zone.get("recomendacion", "")
            )

            action1, action2 = st.columns(2)

            with action1:
                if st.button(
                    "Editar zona",
                    key=f"edit_{zone_id}",
                    use_container_width=True,
                ):
                    st.session_state["editing_zone_id"] = zone_id
                    st.rerun()

            with action2:
                with st.popover(
                    "Eliminar zona",
                    use_container_width=True,
                ):
                    st.warning(
                        "Esta acción no se puede deshacer."
                    )

                    if st.button(
                        "Confirmar eliminación",
                        key=f"delete_{zone_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        delete_zone(zone_id)
                        st.session_state.pop(
                            "editing_zone_id",
                            None,
                        )
                        st.rerun()


with form_tab:
    editing_zone_id = st.session_state.get("editing_zone_id")

    current_zone = (
        get_zone(editing_zone_id)
        if editing_zone_id
        else {}
    ) or {}

    if editing_zone_id:
        st.subheader("Editar zona")

        if st.button("Cancelar edición"):
            st.session_state.pop("editing_zone_id", None)
            st.rerun()

    else:
        st.subheader("Agregar nueva zona")

    with st.form("zone_form"):
        zone_name = st.text_input(
            "Nombre de la zona *",
            value=current_zone.get("nombre", ""),
            placeholder="Ej. Parte Vieja",
        )

        zone_type = st.selectbox(
            "Tipo de zona",
            ZONE_TYPES,
            index=safe_index(
                ZONE_TYPES,
                current_zone.get("tipo_zona"),
            ),
        )

        reference = st.text_input(
            "Lugar o dirección de referencia",
            value=current_zone.get("referencia", ""),
            placeholder=(
                "Ej. Plaza de la Constitución, Parte Vieja"
            ),
        )

        lat_col, lon_col = st.columns(2)

        with lat_col:
            latitude = st.number_input(
                "Latitud",
                min_value=-90.0,
                max_value=90.0,
                value=safe_float(
                    current_zone.get("latitud")
                ),
                step=0.0001,
                format="%.6f",
            )

        with lon_col:
            longitude = st.number_input(
                "Longitud",
                min_value=-180.0,
                max_value=180.0,
                value=safe_float(
                    current_zone.get("longitud")
                ),
                step=0.0001,
                format="%.6f",
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            pressure = st.selectbox(
                "Presión turística",
                PRESSURE_OPTIONS,
                index=safe_index(
                    PRESSURE_OPTIONS,
                    current_zone.get("presion"),
                ),
            )

        with col2:
            fragility = st.selectbox(
                "Fragilidad",
                FRAGILITY_OPTIONS,
                index=safe_index(
                    FRAGILITY_OPTIONS,
                    current_zone.get("fragilidad"),
                ),
            )

        with col3:
            infrastructure = st.selectbox(
                "Capacidad de infraestructura",
                INFRASTRUCTURE_OPTIONS,
                index=safe_index(
                    INFRASTRUCTURE_OPTIONS,
                    current_zone.get("infraestructura"),
                ),
            )

        zone_impacts = st.multiselect(
            "Impactos observados",
            ZONE_IMPACTS,
            default=current_zone.get("impactos", []),
        )

        evidence = st.text_area(
            "Evidencia y observaciones",
            value=current_zone.get("evidencia", ""),
            height=130,
        )

        submitted = st.form_submit_button(
            (
                "Actualizar zona"
                if editing_zone_id
                else "Guardar zona"
            ),
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not zone_name.strip():
            st.error("Es necesario indicar el nombre de la zona.")

        elif "No evaluada" in {
            pressure,
            fragility,
            infrastructure,
        }:
            st.error(
                "Es necesario valorar presión, fragilidad e infraestructura."
            )

        else:
            score, level = calculate_zone_priority(
                pressure,
                fragility,
                infrastructure,
                zone_impacts,
            )

            recommendation = generate_zone_recommendation(
                pressure,
                fragility,
                infrastructure,
                zone_impacts,
            )

            save_zone(
                {
                    "destination_id": destination_id,
                    "nombre": zone_name,
                    "tipo_zona": zone_type,
                    "referencia": reference,
                    "latitud": latitude,
                    "longitud": longitude,
                    "presion": pressure,
                    "fragilidad": fragility,
                    "infraestructura": infrastructure,
                    "impactos": zone_impacts,
                    "evidencia": evidence,
                    "prioridad_score": score,
                    "prioridad_nivel": level,
                    "recomendacion": recommendation,
                },
                zone_id=editing_zone_id,
            )

            st.session_state.pop("editing_zone_id", None)

            st.success(
                f"Zona {zone_name} guardada correctamente."
            )

            st.write(
                f"Prioridad: **{level} ({score}/100)**"
            )

            st.write(
                f"Recomendación inicial: {recommendation}"
            )
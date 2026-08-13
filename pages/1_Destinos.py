import streamlit as st

from calculations import calculate_completeness
from database import init_db, list_destinations
from styles import apply_incubatour_theme


st.set_page_config(
    page_title="Destinos",
    page_icon="◆",
    layout="wide",
)

apply_incubatour_theme()
init_db()


def get_status(completeness: int) -> str:
    if completeness == 100:
        return "Completo"
    if completeness >= 70:
        return "Avanzado"
    if completeness >= 35:
        return "En construcción"
    return "Inicial"


def next_action(
    destination: dict,
    completeness: int,
    missing_fields: list[str],
) -> str:
    if completeness == 100:
        return "Agregar zonas y construir la lectura territorial."

    if missing_fields:
        return f"Completar: {missing_fields[0]}."

    return "Revisar y validar el expediente."


def format_number(value: object) -> str:
    try:
        return f"{int(value or 0):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


st.title("Destinos")

st.write(
    "Consulta el avance de cada expediente y retoma el análisis "
    "desde el punto exacto en el que se quedó."
)

action_col, info_col = st.columns([1, 2])

with action_col:
    if st.button(
        "+ Analizar un nuevo destino",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.pop("active_destination_id", None)
        st.switch_page("pages/2_Diagnostico.py")

with info_col:
    st.info(
        "Cada expediente integra datos oficiales, entrevista, "
        "territorio, diagnóstico e interpretación final."
    )


destinations = list_destinations()

if not destinations:
    with st.container(border=True):
        st.subheader("Todavía no hay destinos guardados")
        st.write(
            "Crea el primer expediente para comenzar a integrar "
            "datos, entrevistas y evidencia territorial."
        )
    st.stop()


analysed_destinations = []

for destination in destinations:
    completeness, missing_fields = calculate_completeness(destination)

    analysed_destinations.append(
        {
            "destination": destination,
            "completeness": completeness,
            "missing_fields": missing_fields,
        }
    )


total = len(analysed_destinations)
complete = sum(
    item["completeness"] == 100
    for item in analysed_destinations
)
advanced = sum(
    70 <= item["completeness"] < 100
    for item in analysed_destinations
)
construction = sum(
    item["completeness"] < 70
    for item in analysed_destinations
)


st.subheader("Panorama del portafolio")

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("Destinos", total)
metric2.metric("Completos", complete)
metric3.metric("Avanzados", advanced)
metric4.metric("En construcción", construction)


search_col, order_col = st.columns([2, 1])

with search_col:
    search_term = st.text_input(
        "Buscar destino",
        placeholder="Municipio, provincia o Comunidad Autónoma",
    )

with order_col:
    order_option = st.selectbox(
        "Ordenar por",
        [
            "Última actualización",
            "Mayor avance",
            "Menor avance",
            "Nombre",
        ],
    )


filtered = analysed_destinations

if search_term.strip():
    query = search_term.lower().strip()

    filtered = [
        item
        for item in filtered
        if query in (
            f"{item['destination'].get('municipio', '')} "
            f"{item['destination'].get('provincia', '')} "
            f"{item['destination'].get('comunidad_autonoma', '')}"
        ).lower()
    ]


if order_option == "Mayor avance":
    filtered = sorted(
        filtered,
        key=lambda item: item["completeness"],
        reverse=True,
    )

elif order_option == "Menor avance":
    filtered = sorted(
        filtered,
        key=lambda item: item["completeness"],
    )

elif order_option == "Nombre":
    filtered = sorted(
        filtered,
        key=lambda item: item["destination"]
        .get("municipio", "")
        .lower(),
    )

else:
    filtered = sorted(
        filtered,
        key=lambda item: str(
            item["destination"].get("updated_at", "")
        ),
        reverse=True,
    )


st.subheader("Expedientes guardados")

for item in filtered:
    destination = item["destination"]
    completeness = item["completeness"]
    missing_fields = item["missing_fields"]

    destination_id = int(destination["id"])

    municipio = destination.get("municipio") or "Destino sin nombre"
    provincia = destination.get("provincia") or "Provincia no indicada"
    comunidad = (
        destination.get("comunidad_autonoma")
        or "Comunidad Autónoma no indicada"
    )

    with st.container(border=True):
        header_col, status_col = st.columns([3, 1])

        with header_col:
            st.subheader(municipio)
            st.caption(f"{provincia} · {comunidad}")

        with status_col:
            st.metric(
                "Estado",
                get_status(completeness),
            )

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric(
            "Completitud",
            f"{completeness} %",
        )

        metric2.metric(
            "Población",
            format_number(
                destination.get("poblacion_residente")
            ),
        )

        metric3.metric(
            "Visitantes",
            format_number(
                destination.get("visitantes_anuales")
            ),
        )

        metric4.metric(
            "Actualización",
            str(destination.get("updated_at", ""))[:10],
        )

        st.progress(completeness / 100)

        st.write(
            f"**Siguiente acción:** "
            f"{next_action(destination, completeness, missing_fields)}"
        )

        action1, action2, action3 = st.columns(3)

        with action1:
            if st.button(
                "Abrir expediente",
                key=f"open_{destination_id}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state["active_destination_id"] = destination_id
                st.switch_page("pages/2_Diagnostico.py")

        with action2:
            if st.button(
                "Continuar a Territorio",
                key=f"territory_{destination_id}",
                use_container_width=True,
            ):
                st.session_state["active_destination_id"] = destination_id
                st.switch_page("pages/4_Territorio.py")

        with action3:
            with st.popover(
                "Información pendiente",
                use_container_width=True,
            ):
                if missing_fields:
                    for field in missing_fields:
                        st.write(f"• {field}")
                else:
                    st.success("Expediente general completo.")
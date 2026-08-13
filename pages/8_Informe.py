import io
import json
import os
import re
import unicodedata
from datetime import date
from typing import Any

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

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
    page_title="Informe ejecutivo",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
apply_incubatour_theme()


# =========================================================
# PALETA DE MARCA PARA EL PDF
# =========================================================

COLOR_PINK = colors.HexColor("#F42C86")
COLOR_RED = colors.HexColor("#FF4C55")
COLOR_PURPLE = colors.HexColor("#8C4DFF")
COLOR_DARK = colors.HexColor("#191922")
COLOR_TEXT = colors.HexColor("#383842")
COLOR_MUTED = colors.HexColor("#777783")
COLOR_BORDER = colors.HexColor("#E4E3E8")
COLOR_LIGHT = colors.HexColor("#F7F5FA")
COLOR_WHITE = colors.white

PAGE_WIDTH, PAGE_HEIGHT = A4


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    try:
        return int(round(float(value or 0)))
    except (TypeError, ValueError):
        return default


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value or 0)
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


def format_number(value: Any) -> str:
    try:
        number = int(float(value or 0))
        return f"{number:,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def normalize_list(value: Any) -> list:
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


def health_status(
    score: int | None,
) -> str:
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


def risk_status(
    score: int | None,
) -> str:
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


def get_item_title(
    item: Any,
    default: str,
) -> str:
    if isinstance(item, dict):
        return safe_text(
            item.get("name")
            or item.get("title")
            or item.get("description")
            or item.get("text"),
            default,
        )

    return safe_text(
        item,
        default,
    )


def get_item_description(
    item: Any,
) -> str:
    if not isinstance(item, dict):
        return ""

    return safe_text(
        item.get("evidence")
        or item.get("description")
        or item.get("text"),
        "",
    )


def clean_filename(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    ascii_value = normalized.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    cleaned = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        ascii_value,
    )

    return cleaned.strip("_") or "Destino"


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


def escape_pdf_text(value: Any) -> str:
    """
    Convierte texto a una forma segura para Paragraph de ReportLab.
    """
    text = safe_text(value)

    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\n": "<br/>",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new,
        )

    return text


def normalized_progress(value: Any) -> float:
    return max(
        0.0,
        min(
            safe_float(value) / 100,
            1.0,
        ),
    )


# =========================================================
# ESTILOS DEL PDF
# =========================================================

def build_pdf_styles() -> dict:
    sample_styles = getSampleStyleSheet()

    styles = {
        "cover_kicker": ParagraphStyle(
            "CoverKicker",
            parent=sample_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=COLOR_PURPLE,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=sample_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=33,
            textColor=COLOR_DARK,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "cover_location": ParagraphStyle(
            "CoverLocation",
            parent=sample_styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=COLOR_MUTED,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "cover_intro": ParagraphStyle(
            "CoverIntro",
            parent=sample_styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=17,
            textColor=COLOR_TEXT,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "section_kicker": ParagraphStyle(
            "SectionKicker",
            parent=sample_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=COLOR_PINK,
            spaceAfter=4,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=sample_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=COLOR_DARK,
            spaceBefore=6,
            spaceAfter=12,
        ),
        "subheading": ParagraphStyle(
            "Subheading",
            parent=sample_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=COLOR_DARK,
            spaceBefore=7,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=COLOR_TEXT,
            spaceAfter=7,
        ),
        "body_small": ParagraphStyle(
            "BodySmall",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=COLOR_TEXT,
            spaceAfter=5,
        ),
        "muted": ParagraphStyle(
            "Muted",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=COLOR_MUTED,
            spaceAfter=5,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=sample_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.5,
            leading=8,
            textColor=COLOR_MUTED,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            parent=sample_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=19,
            textColor=COLOR_DARK,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "metric_note": ParagraphStyle(
            "MetricNote",
            parent=sample_styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=COLOR_MUTED,
            alignment=TA_LEFT,
        ),
        "list_item": ParagraphStyle(
            "ListItem",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=13,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=COLOR_TEXT,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=sample_styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=8,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=COLOR_MUTED,
            backColor=COLOR_LIGHT,
            borderColor=COLOR_BORDER,
            borderWidth=0.6,
            borderPadding=8,
            spaceBefore=5,
            spaceAfter=8,
        ),
    }

    return styles


# =========================================================
# COMPONENTES DEL PDF
# =========================================================

def pdf_section(
    story: list,
    styles: dict,
    number: str,
    title: str,
) -> None:
    story.append(
        Paragraph(
            escape_pdf_text(number.upper()),
            styles["section_kicker"],
        )
    )

    story.append(
        Paragraph(
            escape_pdf_text(title),
            styles["section_title"],
        )
    )


def pdf_bullet(
    text: Any,
    styles: dict,
) -> Paragraph:
    return Paragraph(
        f"• {escape_pdf_text(text)}",
        styles["list_item"],
    )


def pdf_metric_cell(
    label: str,
    value: str,
    note: str,
    styles: dict,
) -> list:
    return [
        Paragraph(
            escape_pdf_text(label.upper()),
            styles["metric_label"],
        ),
        Paragraph(
            escape_pdf_text(value),
            styles["metric_value"],
        ),
        Paragraph(
            escape_pdf_text(note),
            styles["metric_note"],
        ),
    ]


def create_metric_table(
    metrics: list[tuple[str, str, str]],
    styles: dict,
    columns: int = 4,
) -> Table:
    rows = []

    for start_index in range(
        0,
        len(metrics),
        columns,
    ):
        row_metrics = metrics[
            start_index:start_index + columns
        ]

        row = [
            pdf_metric_cell(
                label,
                value,
                note,
                styles,
            )
            for label, value, note in row_metrics
        ]

        while len(row) < columns:
            row.append("")

        rows.append(row)

    available_width = (
        PAGE_WIDTH
        - 3.4 * cm
    )

    table = Table(
        rows,
        colWidths=[
            available_width / columns
        ] * columns,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    COLOR_LIGHT,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    COLOR_BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    COLOR_BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    return table


def create_capital_card(
    capital_key: str,
    capital: dict,
    styles: dict,
) -> Table:
    score = capital.get(
        "health_score"
    )

    pressure = capital.get(
        "pressure_score"
    )

    completeness = safe_int(
        capital.get("completeness")
    )

    title = (
        f"Capital {capital_label(capital_key)}"
    )

    if score is None:
        content = [
            Paragraph(
                escape_pdf_text(title),
                styles["subheading"],
            ),
            Paragraph(
                "Sin evaluar",
                styles["metric_value"],
            ),
            Paragraph(
                (
                    "Se requiere completar información "
                    "para calcular esta dimensión."
                ),
                styles["muted"],
            ),
        ]

    else:
        score_value = safe_int(score)
        pressure_value = safe_int(pressure)

        status = safe_text(
            capital.get("status"),
            health_status(score_value),
        )

        risk = safe_text(
            capital.get("risk_level"),
            risk_status(pressure_value),
        )

        content = [
            Paragraph(
                escape_pdf_text(title),
                styles["subheading"],
            ),
            Table(
                [
                    [
                        pdf_metric_cell(
                            "Salud",
                            f"{score_value}/100",
                            status,
                            styles,
                        ),
                        pdf_metric_cell(
                            "Presión",
                            f"{pressure_value}/100",
                            risk,
                            styles,
                        ),
                    ]
                ],
                colWidths=[
                    7.25 * cm,
                    7.25 * cm,
                ],
                style=TableStyle(
                    [
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            4,
                        ),
                    ]
                ),
            ),
            Paragraph(
                (
                    f"<b>Completitud:</b> "
                    f"{completeness} %"
                ),
                styles["body_small"],
            ),
        ]

        findings = normalize_list(
            capital.get("findings")
        )

        if findings:
            content.append(
                Paragraph(
                    "Hallazgos principales",
                    styles["body_small"],
                )
            )

            for finding in findings[:3]:
                content.append(
                    pdf_bullet(
                        get_item_title(
                            finding,
                            "Hallazgo",
                        ),
                        styles,
                    )
                )

    card = Table(
        [[content]],
        colWidths=[
            PAGE_WIDTH - 3.4 * cm
        ],
        hAlign="LEFT",
    )

    card.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    COLOR_WHITE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    COLOR_BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    11,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    11,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    return card


def add_pdf_header_footer(
    canvas,
    document,
    municipality: str,
    logo_path: str | None,
) -> None:
    canvas.saveState()

    page_number = canvas.getPageNumber()

    if page_number > 1:
        canvas.setStrokeColor(COLOR_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(
            1.7 * cm,
            PAGE_HEIGHT - 1.35 * cm,
            PAGE_WIDTH - 1.7 * cm,
            PAGE_HEIGHT - 1.35 * cm,
        )

        if logo_path and os.path.isfile(logo_path):
            try:
                canvas.drawImage(
                    logo_path,
                    1.7 * cm,
                    PAGE_HEIGHT - 1.15 * cm,
                    width=2.3 * cm,
                    height=0.65 * cm,
                    preserveAspectRatio=True,
                    mask="auto",
                    anchor="sw",
                )
            except Exception:
                canvas.setFont(
                    "Helvetica-Bold",
                    8,
                )

                canvas.setFillColor(
                    COLOR_DARK
                )

                canvas.drawString(
                    1.7 * cm,
                    PAGE_HEIGHT - 1.05 * cm,
                    "INCUBATOUR DECISION LAB",
                )
        else:
            canvas.setFont(
                "Helvetica-Bold",
                8,
            )

            canvas.setFillColor(
                COLOR_DARK
            )

            canvas.drawString(
                1.7 * cm,
                PAGE_HEIGHT - 1.05 * cm,
                "INCUBATOUR DECISION LAB",
            )

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.setFillColor(
            COLOR_MUTED
        )

        canvas.drawRightString(
            PAGE_WIDTH - 1.7 * cm,
            PAGE_HEIGHT - 1.05 * cm,
            safe_text(
                municipality,
                "Destino",
            ),
        )

    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(
        1.7 * cm,
        1.25 * cm,
        PAGE_WIDTH - 1.7 * cm,
        1.25 * cm,
    )

    canvas.setFont(
        "Helvetica",
        7,
    )

    canvas.setFillColor(
        COLOR_MUTED
    )

    canvas.drawString(
        1.7 * cm,
        0.86 * cm,
        "Incubatour Decision Lab · Diagnóstico estratégico",
    )

    canvas.drawRightString(
        PAGE_WIDTH - 1.7 * cm,
        0.86 * cm,
        f"Página {page_number}",
    )

    canvas.restoreState()


# =========================================================
# GENERACIÓN DEL PDF
# =========================================================

def build_pdf_report(
    destination: dict,
    zones: list,
    analysis: dict,
    logo_path: str | None,
) -> bytes:
    buffer = io.BytesIO()

    municipality = safe_text(
        destination.get("municipio"),
        "Destino sin nombre",
    )

    province = safe_text(
        destination.get("provincia")
    )

    autonomous_community = safe_text(
        destination.get("comunidad_autonoma")
    )

    location = " · ".join(
        value
        for value in [
            province,
            autonomous_community,
        ]
        if value
    )

    health_score = safe_int(
        analysis.get("destination_health")
    )

    risk_score = safe_int(
        analysis.get("global_risk_score")
    )

    risk_level = safe_text(
        analysis.get("risk_level"),
        "Sin evaluar",
    )

    confidence = safe_int(
        analysis.get("confidence")
    )

    stage = safe_text(
        analysis.get("stage"),
        "Sin clasificación",
    )

    executive_summary = safe_text(
        analysis.get("executive_summary"),
        (
            "No existe información suficiente para "
            "generar una lectura ejecutiva."
        ),
    )

    capitals = (
        analysis.get("capitals")
        or {}
    )

    main_risks = normalize_list(
        analysis.get("main_risks")
    )

    main_strengths = normalize_list(
        analysis.get("main_strengths")
    )

    main_opportunities = normalize_list(
        analysis.get("main_opportunities")
    )

    poker_as = (
        analysis.get("poker_as")
        or {}
    )

    styles = build_pdf_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title=(
            f"Informe ejecutivo - {municipality}"
        ),
        author="Incubatour Decision Lab",
        subject="Diagnóstico estratégico del destino",
    )

    story = []

    # -----------------------------------------------------
    # PORTADA
    # -----------------------------------------------------

    story.append(
        Spacer(
            1,
            0.35 * cm,
        )
    )

    if logo_path and os.path.isfile(logo_path):
        try:
            logo = Image(
                logo_path,
                width=5.2 * cm,
                height=1.5 * cm,
                kind="proportional",
            )

            logo.hAlign = "LEFT"
            story.append(logo)

            story.append(
                Spacer(
                    1,
                    1.2 * cm,
                )
            )

        except Exception:
            story.append(
                Paragraph(
                    "INCUBATOUR DECISION LAB",
                    styles["cover_kicker"],
                )
            )

            story.append(
                Spacer(
                    1,
                    0.8 * cm,
                )
            )

    else:
        story.append(
            Paragraph(
                "INCUBATOUR DECISION LAB",
                styles["cover_kicker"],
            )
        )

        story.append(
            Spacer(
                1,
                0.8 * cm,
            )
        )

    story.append(
        HRFlowable(
            width="100%",
            thickness=4,
            color=COLOR_PINK,
            spaceBefore=0,
            spaceAfter=18,
        )
    )

    story.append(
        Paragraph(
            "DIAGNÓSTICO ESTRATÉGICO DEL DESTINO",
            styles["cover_kicker"],
        )
    )

    story.append(
        Paragraph(
            escape_pdf_text(municipality),
            styles["cover_title"],
        )
    )

    if location:
        story.append(
            Paragraph(
                escape_pdf_text(location),
                styles["cover_location"],
            )
        )

    story.append(
        Paragraph(
            (
                "Informe ejecutivo generado por "
                "<b>Incubatour Decision Lab</b>."
            ),
            styles["cover_intro"],
        )
    )

    story.append(
        Spacer(
            1,
            0.8 * cm,
        )
    )

    cover_metrics = create_metric_table(
        [
            (
                "Salud global",
                f"{health_score}/100",
                health_status(health_score),
            ),
            (
                "Riesgo global",
                f"{risk_score}/100",
                risk_level,
            ),
            (
                "Confianza",
                f"{confidence} %",
                "Calidad de la evidencia",
            ),
            (
                "Estado",
                stage,
                "Etapa estratégica",
            ),
        ],
        styles,
        columns=2,
    )

    story.append(cover_metrics)

    story.append(
        Spacer(
            1,
            1.2 * cm,
        )
    )

    cover_information = Table(
        [
            [
                Paragraph(
                    "<b>Fecha de generación</b>",
                    styles["body_small"],
                ),
                Paragraph(
                    date.today().strftime(
                        "%d/%m/%Y"
                    ),
                    styles["body_small"],
                ),
            ],
            [
                Paragraph(
                    "<b>Zonas territoriales analizadas</b>",
                    styles["body_small"],
                ),
                Paragraph(
                    str(len(zones)),
                    styles["body_small"],
                ),
            ],
            [
                Paragraph(
                    "<b>Capitales evaluados</b>",
                    styles["body_small"],
                ),
                Paragraph(
                    (
                        f"{safe_int(analysis.get('capitals_evaluated'))}"
                        "/"
                        f"{safe_int(analysis.get('capitals_total', 6))}"
                    ),
                    styles["body_small"],
                ),
            ],
        ],
        colWidths=[
            7.5 * cm,
            7.2 * cm,
        ],
    )

    cover_information.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    COLOR_BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    COLOR_BORDER,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    COLOR_LIGHT,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(cover_information)

    story.append(PageBreak())

    # -----------------------------------------------------
    # 1. RESUMEN EJECUTIVO
    # -----------------------------------------------------

    pdf_section(
        story,
        styles,
        "01 · Resumen general",
        "Lectura ejecutiva",
    )

    story.append(
        create_metric_table(
            [
                (
                    "Salud global",
                    f"{health_score}/100",
                    health_status(health_score),
                ),
                (
                    "Riesgo global",
                    f"{risk_score}/100",
                    risk_level,
                ),
                (
                    "Confianza",
                    f"{confidence} %",
                    "Cobertura de datos",
                ),
                (
                    "Zonas",
                    str(len(zones)),
                    "Áreas analizadas",
                ),
            ],
            styles,
            columns=4,
        )
    )

    story.append(
        Spacer(
            1,
            0.5 * cm,
        )
    )

    story.append(
        Paragraph(
            escape_pdf_text(executive_summary),
            styles["body"],
        )
    )

    # -----------------------------------------------------
    # 2. PERFIL
    # -----------------------------------------------------

    pdf_section(
        story,
        styles,
        "02 · Perfil",
        "Perfil del destino",
    )

    story.append(
        create_metric_table(
            [
                (
                    "Población residente",
                    format_number(
                        destination.get(
                            "poblacion_residente"
                        )
                    ),
                    "Habitantes",
                ),
                (
                    "Visitantes anuales",
                    format_number(
                        destination.get(
                            "visitantes_anuales"
                        )
                    ),
                    "Demanda estimada",
                ),
                (
                    "Pernoctaciones",
                    format_number(
                        destination.get(
                            "pernoctaciones_anuales"
                        )
                    ),
                    "Pernoctaciones anuales",
                ),
                (
                    "Zonas analizadas",
                    str(len(zones)),
                    "Cobertura territorial",
                ),
            ],
            styles,
            columns=4,
        )
    )

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
        story.append(
            Spacer(
                1,
                0.45 * cm,
            )
        )

        story.append(
            Paragraph(
                (
                    "<b>Tipologías turísticas:</b> "
                    + escape_pdf_text(
                        " · ".join(typologies)
                    )
                ),
                styles["body"],
            )
        )

    # -----------------------------------------------------
    # 3. CAPITALES
    # -----------------------------------------------------

    story.append(PageBreak())

    pdf_section(
        story,
        styles,
        "03 · Sistema de capitales",
        "Los seis capitales del destino",
    )

    capital_order = [
        "tourism",
        "territorial",
        "social",
        "institutional",
        "reputational",
        "resilience",
    ]

    for capital_key in capital_order:
        capital = (
            capitals.get(capital_key)
            or {}
        )

        story.append(
            KeepTogether(
                [
                    create_capital_card(
                        capital_key,
                        capital,
                        styles,
                    ),
                    Spacer(
                        1,
                        0.35 * cm,
                    ),
                ]
            )
        )

    # -----------------------------------------------------
    # 4. RIESGOS
    # -----------------------------------------------------

    story.append(PageBreak())

    pdf_section(
        story,
        styles,
        "04 · Priorización",
        "Riesgos prioritarios",
    )

    if main_risks:
        for index, risk in enumerate(
            main_risks[:8],
            start=1,
        ):
            title = get_item_title(
                risk,
                f"Riesgo {index}",
            )

            description = get_item_description(
                risk
            )

            risk_level_item = ""
            score = 0
            capital_name = ""

            if isinstance(risk, dict):
                score = safe_int(
                    risk.get("score")
                )

                risk_level_item = safe_text(
                    risk.get("level"),
                    "Sin evaluar",
                )

                capital_name = safe_text(
                    risk.get("capital")
                )

            title_paragraph = Paragraph(
                (
                    f"<b>{index}. "
                    f"{escape_pdf_text(title)}</b>"
                ),
                styles["subheading"],
            )

            details = []

            if isinstance(risk, dict):
                detail_text = (
                    f"<b>Score:</b> {score}/100"
                    f" &nbsp;&nbsp; "
                    f"<b>Nivel:</b> "
                    f"{escape_pdf_text(risk_level_item)}"
                )

                if capital_name:
                    detail_text += (
                        f" &nbsp;&nbsp; "
                        f"<b>Capital:</b> "
                        f"{escape_pdf_text(capital_name)}"
                    )

                details.append(
                    Paragraph(
                        detail_text,
                        styles["body_small"],
                    )
                )

            if description:
                details.append(
                    Paragraph(
                        escape_pdf_text(description),
                        styles["body"],
                    )
                )

            risk_card = Table(
                [
                    [
                        [
                            title_paragraph,
                            *details,
                        ]
                    ]
                ],
                colWidths=[
                    PAGE_WIDTH - 3.4 * cm
                ],
            )

            risk_card.setStyle(
                TableStyle(
                    [
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.7,
                            COLOR_BORDER,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            COLOR_LIGHT,
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            10,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            10,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]
                )
            )

            story.append(risk_card)

            story.append(
                Spacer(
                    1,
                    0.3 * cm,
                )
            )

    else:
        story.append(
            Paragraph(
                (
                    "No se identificaron riesgos prioritarios "
                    "con la información disponible."
                ),
                styles["note"],
            )
        )

    # -----------------------------------------------------
    # 5. FORTALEZAS Y OPORTUNIDADES
    # -----------------------------------------------------

    pdf_section(
        story,
        styles,
        "05 · Capacidades",
        "Fortalezas y oportunidades",
    )

    strengths_content = [
        Paragraph(
            "Fortalezas",
            styles["subheading"],
        )
    ]

    if main_strengths:
        for strength in main_strengths[:8]:
            strengths_content.append(
                pdf_bullet(
                    get_item_title(
                        strength,
                        "Fortaleza",
                    ),
                    styles,
                )
            )
    else:
        strengths_content.append(
            Paragraph(
                (
                    "No se identificaron fortalezas "
                    "consolidadas."
                ),
                styles["muted"],
            )
        )

    opportunities_content = [
        Paragraph(
            "Oportunidades",
            styles["subheading"],
        )
    ]

    if main_opportunities:
        for opportunity in main_opportunities[:8]:
            opportunities_content.append(
                pdf_bullet(
                    get_item_title(
                        opportunity,
                        "Oportunidad",
                    ),
                    styles,
                )
            )
    else:
        opportunities_content.append(
            Paragraph(
                (
                    "No se identificaron oportunidades "
                    "automáticas."
                ),
                styles["muted"],
            )
        )

    strengths_table = Table(
        [
            [
                strengths_content,
                opportunities_content,
            ]
        ],
        colWidths=[
            7.35 * cm,
            7.35 * cm,
        ],
    )

    strengths_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    COLOR_BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    COLOR_BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(strengths_table)

    # -----------------------------------------------------
    # 6. PÓKER DE AS
    # -----------------------------------------------------

    story.append(PageBreak())

    pdf_section(
        story,
        styles,
        "06 · Metodología Incubatour",
        "Póker de As",
    )

    poker_sections = [
        (
            "Analiza",
            "¿Qué está ocurriendo en el destino?",
            normalize_list(
                poker_as.get("analiza")
            ),
        ),
        (
            "Aprende",
            "¿Por qué ocurre y qué relaciones existen?",
            normalize_list(
                poker_as.get("aprende")
            ),
        ),
        (
            "Adapta",
            "¿Qué oportunidades de ajuste existen?",
            normalize_list(
                poker_as.get("adapta")
            ),
        ),
        (
            "Actúa",
            "¿Qué decisiones deben priorizarse?",
            normalize_list(
                poker_as.get("actua")
            ),
        ),
    ]

    for title, question, items in poker_sections:
        section_content = [
            Paragraph(
                escape_pdf_text(title),
                styles["subheading"],
            ),
            Paragraph(
                escape_pdf_text(question),
                styles["muted"],
            ),
        ]

        if items:
            for item in items[:8]:
                section_content.append(
                    pdf_bullet(
                        get_item_title(
                            item,
                            title,
                        ),
                        styles,
                    )
                )

                description = get_item_description(
                    item
                )

                if description:
                    section_content.append(
                        Paragraph(
                            escape_pdf_text(description),
                            styles["body_small"],
                        )
                    )
        else:
            section_content.append(
                Paragraph(
                    "Sin información suficiente.",
                    styles["muted"],
                )
            )

        poker_card = Table(
            [[section_content]],
            colWidths=[
                PAGE_WIDTH - 3.4 * cm
            ],
        )

        poker_card.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        COLOR_BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            KeepTogether(
                [
                    poker_card,
                    Spacer(
                        1,
                        0.35 * cm,
                    ),
                ]
            )
        )

    # -----------------------------------------------------
    # 7. CALIDAD
    # -----------------------------------------------------

    pdf_section(
        story,
        styles,
        "07 · Calidad del diagnóstico",
        "Cobertura y confiabilidad",
    )

    story.append(
        create_metric_table(
            [
                (
                    "Capitales evaluados",
                    (
                        f"{safe_int(analysis.get('capitals_evaluated'))}"
                        "/"
                        f"{safe_int(analysis.get('capitals_total', 6))}"
                    ),
                    "Dimensiones calculadas",
                ),
                (
                    "Confianza",
                    f"{confidence} %",
                    "Calidad de evidencia",
                ),
                (
                    "Zonas analizadas",
                    str(len(zones)),
                    "Cobertura territorial",
                ),
            ],
            styles,
            columns=3,
        )
    )

    story.append(
        Spacer(
            1,
            0.45 * cm,
        )
    )

    if confidence < 60:
        quality_message = (
            "Este informe debe considerarse preliminar. "
            "La cobertura de datos todavía es limitada."
        )

    elif confidence < 80:
        quality_message = (
            "El informe cuenta con una base suficiente, "
            "aunque todavía puede reforzarse."
        )

    else:
        quality_message = (
            "El informe cuenta con una base sólida "
            "para orientar decisiones estratégicas."
        )

    story.append(
        Paragraph(
            escape_pdf_text(quality_message),
            styles["note"],
        )
    )

    story.append(
        Paragraph(
            (
                "<b>Nota metodológica.</b> "
                "Este informe se genera mediante el modelo de "
                "diagnóstico de Incubatour Decision Lab. "
                "Los resultados dependen de la calidad, actualidad "
                "y cobertura de la información incorporada."
            ),
            styles["body_small"],
        )
    )

    # -----------------------------------------------------
    # CONSTRUCCIÓN
    # -----------------------------------------------------

    def page_callback(canvas, doc):
        add_pdf_header_footer(
            canvas,
            doc,
            municipality,
            logo_path,
        )

    document.build(
        story,
        onFirstPage=page_callback,
        onLaterPages=page_callback,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# =========================================================
# ENCABEZADO DE LA PÁGINA
# =========================================================

logo_path = find_logo()

header_logo, header_title = st.columns(
    [0.55, 3],
    vertical_alignment="center",
)

with header_logo:
    if logo_path:
        st.image(
            logo_path,
            use_container_width=True,
        )

with header_title:
    st.caption(
        "INCUBATOUR DECISION LAB"
    )

    st.title(
        "Informe ejecutivo"
    )

    st.write(
        "Consolida el diagnóstico del destino en un documento "
        "profesional listo para presentación y descarga."
    )


# =========================================================
# SELECCIÓN DEL DESTINO
# =========================================================

destinations = (
    list_destinations()
    or []
)

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


destination_labels: dict[str, Any] = {}

for destination_item in destinations:
    destination_item_id = destination_item.get(
        "id"
    )

    if destination_item_id is None:
        continue

    item_municipality = safe_text(
        destination_item.get("municipio"),
        "Destino sin nombre",
    )

    item_province = safe_text(
        destination_item.get("provincia")
    )

    label = item_municipality

    if item_province:
        label = (
            f"{item_municipality} · "
            f"{item_province}"
        )

    original_label = label
    suffix = 2

    while label in destination_labels:
        label = (
            f"{original_label} ({suffix})"
        )

        suffix += 1

    destination_labels[
        label
    ] = destination_item_id


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
    options=list(
        destination_labels.keys()
    ),
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

if not destination:
    st.error(
        "No fue posible cargar el expediente seleccionado."
    )

    st.stop()


zones = (
    list_zones(destination_id)
    or []
)

analysis = (
    analyze_destination(
        destination,
        zones,
    )
    or {}
)


# =========================================================
# VARIABLES DEL DESTINO
# =========================================================

municipality = safe_text(
    destination.get("municipio"),
    "Destino sin nombre",
)

province = safe_text(
    destination.get("provincia")
)

autonomous_community = safe_text(
    destination.get("comunidad_autonoma")
)

location = " · ".join(
    value
    for value in [
        province,
        autonomous_community,
    ]
    if value
)

health_score = safe_int(
    analysis.get("destination_health")
)

risk_score = safe_int(
    analysis.get("global_risk_score")
)

risk_level = safe_text(
    analysis.get("risk_level"),
    "Sin evaluar",
)

confidence = safe_int(
    analysis.get("confidence")
)

stage = safe_text(
    analysis.get("stage"),
    "Sin clasificación",
)

executive_summary = safe_text(
    analysis.get("executive_summary")
)

capitals = (
    analysis.get("capitals")
    or {}
)

main_risks = normalize_list(
    analysis.get("main_risks")
)

main_strengths = normalize_list(
    analysis.get("main_strengths")
)

main_opportunities = normalize_list(
    analysis.get("main_opportunities")
)

poker_as = (
    analysis.get("poker_as")
    or {}
)


# =========================================================
# PORTADA EN PANTALLA
# =========================================================

with st.container(border=True):
    title_column, date_column = st.columns(
        [3, 1]
    )

    with title_column:
        st.caption(
            "DIAGNÓSTICO ESTRATÉGICO DEL DESTINO"
        )

        st.header(
            municipality
        )

        if location:
            st.write(
                location
            )

        st.write(
            "**Incubatour Decision Lab**"
        )

    with date_column:
        st.metric(
            "Fecha",
            date.today().strftime(
                "%d/%m/%Y"
            ),
        )

        st.metric(
            "Estado",
            stage,
        )


# =========================================================
# 1. RESUMEN GENERAL
# =========================================================

st.header(
    "1. Resumen general"
)

metric_1, metric_2, metric_3, metric_4 = st.columns(
    4
)

with metric_1:
    st.metric(
        "Salud global",
        f"{health_score}/100",
    )

with metric_2:
    st.metric(
        "Riesgo global",
        f"{risk_score}/100",
    )

with metric_3:
    st.metric(
        "Nivel de riesgo",
        risk_level,
    )

with metric_4:
    st.metric(
        "Confianza",
        f"{confidence} %",
    )


with st.container(border=True):
    st.subheader(
        "Lectura ejecutiva"
    )

    if executive_summary:
        st.write(
            executive_summary
        )

    else:
        st.info(
            "No existe información suficiente "
            "para generar la lectura ejecutiva."
        )


# =========================================================
# 2. PERFIL
# =========================================================

st.header(
    "2. Perfil del destino"
)

profile_1, profile_2, profile_3, profile_4 = st.columns(
    4
)

with profile_1:
    st.metric(
        "Población",
        format_number(
            destination.get(
                "poblacion_residente"
            )
        ),
    )

with profile_2:
    st.metric(
        "Visitantes",
        format_number(
            destination.get(
                "visitantes_anuales"
            )
        ),
    )

with profile_3:
    st.metric(
        "Pernoctaciones",
        format_number(
            destination.get(
                "pernoctaciones_anuales"
            )
        ),
    )

with profile_4:
    st.metric(
        "Zonas analizadas",
        len(zones),
    )


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
    st.write(
        "**Tipologías turísticas:** "
        + " · ".join(typologies)
    )


# =========================================================
# 3. CAPITALES
# =========================================================

st.header(
    "3. Los seis capitales"
)

capital_order = [
    "tourism",
    "territorial",
    "social",
    "institutional",
    "reputational",
    "resilience",
]

capital_columns = st.columns(2)

for index, capital_key in enumerate(
    capital_order
):
    capital = (
        capitals.get(capital_key)
        or {}
    )

    score = capital.get(
        "health_score"
    )

    pressure = capital.get(
        "pressure_score"
    )

    status = safe_text(
        capital.get("status")
    )

    risk = safe_text(
        capital.get("risk_level")
    )

    completeness = safe_int(
        capital.get("completeness")
    )

    findings = normalize_list(
        capital.get("findings")
    )

    risks = normalize_list(
        capital.get("risks")
    )

    opportunities = normalize_list(
        capital.get("opportunities")
    )

    current_column = capital_columns[
        index % 2
    ]

    with current_column:
        with st.container(border=True):
            st.subheader(
                f"Capital {capital_label(capital_key)}"
            )

            if score is None:
                st.metric(
                    "Salud",
                    "Pendiente",
                )

                st.write(
                    "No existe información suficiente "
                    "para evaluar esta dimensión."
                )

                continue

            score_value = safe_int(
                score
            )

            pressure_value = safe_int(
                pressure
            )

            capital_metric_1, capital_metric_2 = st.columns(
                2
            )

            with capital_metric_1:
                st.metric(
                    "Salud",
                    f"{score_value}/100",
                )

            with capital_metric_2:
                st.metric(
                    "Presión",
                    f"{pressure_value}/100",
                )

            st.progress(
                normalized_progress(
                    score_value
                )
            )

            st.write(
                "**Estado:** "
                + (
                    status
                    or health_status(
                        score_value
                    )
                )
            )

            st.write(
                "**Riesgo:** "
                + (
                    risk
                    or risk_status(
                        pressure_value
                    )
                )
            )

            st.caption(
                (
                    "Completitud de la dimensión: "
                    f"{completeness} %"
                )
            )

            if findings:
                with st.expander(
                    "Hallazgos"
                ):
                    for finding in findings[:5]:
                        st.write(
                            "• "
                            + get_item_title(
                                finding,
                                "Hallazgo",
                            )
                        )

            if risks:
                with st.expander(
                    "Riesgos"
                ):
                    for risk_item in risks[:5]:
                        st.write(
                            "• "
                            + get_item_title(
                                risk_item,
                                "Riesgo",
                            )
                        )

            if opportunities:
                with st.expander(
                    "Oportunidades"
                ):
                    for opportunity in opportunities[:5]:
                        st.write(
                            "• "
                            + get_item_title(
                                opportunity,
                                "Oportunidad",
                            )
                        )


# =========================================================
# 4. RIESGOS PRIORITARIOS
# =========================================================

st.header(
    "4. Riesgos prioritarios"
)

if main_risks:
    for index, risk in enumerate(
        main_risks[:8],
        start=1,
    ):
        with st.container(border=True):
            content_column, metric_column = st.columns(
                [4, 1]
            )

            with content_column:
                st.subheader(
                    (
                        f"{index}. "
                        + get_item_title(
                            risk,
                            "Riesgo",
                        )
                    )
                )

                description = get_item_description(
                    risk
                )

                if description:
                    st.write(
                        description
                    )

                if isinstance(risk, dict):
                    capital_name = safe_text(
                        risk.get("capital")
                    )

                    if capital_name:
                        st.caption(
                            (
                                "Capital relacionado: "
                                f"{capital_name}"
                            )
                        )

            with metric_column:
                if isinstance(risk, dict):
                    st.metric(
                        "Score",
                        (
                            f"{safe_int(risk.get('score'))}"
                            "/100"
                        ),
                    )

                    st.write(
                        "**Nivel:** "
                        + safe_text(
                            risk.get("level"),
                            "Sin evaluar",
                        )
                    )

else:
    st.success(
        "No se identificaron riesgos prioritarios "
        "con la información disponible."
    )


# =========================================================
# 5. FORTALEZAS Y OPORTUNIDADES
# =========================================================

st.header(
    "5. Fortalezas y oportunidades"
)

strength_column, opportunity_column = st.columns(
    2
)

with strength_column:
    st.subheader(
        "Fortalezas"
    )

    if main_strengths:
        for index, strength in enumerate(
            main_strengths[:8],
            start=1,
        ):
            with st.container(border=True):
                st.write(
                    (
                        f"**{index}. "
                        f"{get_item_title(strength, 'Fortaleza')}**"
                    )
                )

                description = get_item_description(
                    strength
                )

                if description:
                    st.write(
                        description
                    )

    else:
        st.info(
            "No se identificaron fortalezas consolidadas."
        )


with opportunity_column:
    st.subheader(
        "Oportunidades"
    )

    if main_opportunities:
        for index, opportunity in enumerate(
            main_opportunities[:8],
            start=1,
        ):
            with st.container(border=True):
                st.write(
                    (
                        f"**{index}. "
                        f"{get_item_title(opportunity, 'Oportunidad')}**"
                    )
                )

                description = get_item_description(
                    opportunity
                )

                if description:
                    st.write(
                        description
                    )

    else:
        st.info(
            "No se identificaron oportunidades automáticas."
        )


# =========================================================
# 6. PÓKER DE AS
# =========================================================

st.header(
    "6. Póker de As"
)

poker_tabs = st.tabs(
    [
        "Analiza",
        "Aprende",
        "Adapta",
        "Actúa",
    ]
)

poker_sections = [
    (
        poker_tabs[0],
        "Analiza",
        normalize_list(
            poker_as.get("analiza")
        ),
        "¿Qué está ocurriendo en el destino?",
    ),
    (
        poker_tabs[1],
        "Aprende",
        normalize_list(
            poker_as.get("aprende")
        ),
        "¿Por qué ocurre y qué relaciones existen?",
    ),
    (
        poker_tabs[2],
        "Adapta",
        normalize_list(
            poker_as.get("adapta")
        ),
        "¿Qué oportunidades de ajuste existen?",
    ),
    (
        poker_tabs[3],
        "Actúa",
        normalize_list(
            poker_as.get("actua")
        ),
        "¿Qué decisiones deben priorizarse?",
    ),
]

for tab, title, items, question in poker_sections:
    with tab:
        st.subheader(
            title
        )

        st.write(
            question
        )

        if items:
            for index, item in enumerate(
                items[:8],
                start=1,
            ):
                with st.container(border=True):
                    st.write(
                        (
                            f"**{index}. "
                            f"{get_item_title(item, title)}**"
                        )
                    )

                    description = get_item_description(
                        item
                    )

                    if description:
                        st.write(
                            description
                        )

        else:
            st.info(
                "No existe información suficiente "
                "para esta fase."
            )


# =========================================================
# 7. CALIDAD
# =========================================================

st.header(
    "7. Calidad del diagnóstico"
)

quality_1, quality_2, quality_3 = st.columns(
    3
)

with quality_1:
    st.metric(
        "Capitales evaluados",
        (
            f"{safe_int(analysis.get('capitals_evaluated'))}"
            f"/{safe_int(analysis.get('capitals_total', 6))}"
        ),
    )

with quality_2:
    st.metric(
        "Confianza",
        f"{confidence} %",
    )

with quality_3:
    st.metric(
        "Zonas analizadas",
        len(zones),
    )


if confidence < 60:
    st.warning(
        "Este informe debe considerarse preliminar. "
        "La cobertura de datos todavía es limitada."
    )

elif confidence < 80:
    st.info(
        "El informe cuenta con una base suficiente, "
        "aunque todavía puede reforzarse."
    )

else:
    st.success(
        "El informe cuenta con una base sólida "
        "para orientar decisiones estratégicas."
    )


# =========================================================
# 8. DESCARGAS
# =========================================================

st.header(
    "8. Descargar informe"
)

with st.spinner(
    "Preparando el informe profesional..."
):
    pdf_report = build_pdf_report(
        destination,
        zones,
        analysis,
        logo_path,
    )


report_data = {
    "generated_at": date.today().isoformat(),
    "destination": destination,
    "zones": zones,
    "analysis": analysis,
}

json_report = json.dumps(
    report_data,
    ensure_ascii=False,
    indent=2,
    default=str,
)

filename_base = clean_filename(
    municipality
)

download_column_1, download_column_2 = st.columns(
    2
)

with download_column_1:
    st.download_button(
        label="Descargar informe profesional en PDF",
        data=pdf_report,
        file_name=(
            f"Informe_Ejecutivo_{filename_base}.pdf"
        ),
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

with download_column_2:
    st.download_button(
        label="Descargar datos técnicos",
        data=json_report,
        file_name=(
            f"Datos_Diagnostico_{filename_base}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


st.caption(
    "El PDF se genera automáticamente con el logo, "
    "los indicadores y la lectura estratégica del destino."
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
        "Volver a Insights",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/7_Insights.py"
        )

with navigation_2:
    if st.button(
        "Volver al Dashboard",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Dashboard.py"
        )

with navigation_3:
    if st.button(
        "Editar diagnóstico",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/2_Diagnostico.py"
        )
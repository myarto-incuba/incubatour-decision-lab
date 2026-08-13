import streamlit as st


def apply_incubatour_theme() -> None:
    """
    Aplica la identidad visual global de Incubatour Decision Lab.
    """

    st.markdown(
        """
        <style>
        :root {
            --inc-black: #18181B;
            --inc-dark: #25252D;
            --inc-gray: #667085;
            --inc-light: #F7F7F5;
            --inc-border: #E7E7E4;
            --inc-white: #FFFFFF;
            --inc-pink: #F52F8B;
            --inc-pink-dark: #C91E70;
            --inc-pink-soft: #FCE8F2;
            --inc-orange: #FFB438;
            --inc-green: #82E83E;
        }

        html,
        body,
        [class*="css"],
        [data-testid="stAppViewContainer"] {
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif !important;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 96% 3%,
                    rgba(245, 47, 139, 0.07),
                    transparent 22rem
                ),
                radial-gradient(
                    circle at 4% 96%,
                    rgba(130, 232, 62, 0.06),
                    transparent 22rem
                ),
                var(--inc-light);
            color: var(--inc-black);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Sidebar */

        [data-testid="stSidebar"] {
            background: var(--inc-black);
            border-right: none;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 11px;
            margin: 0.18rem 0.65rem;
            padding: 0.58rem 0.8rem;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(255, 255, 255, 0.12);
        }

        [data-testid="stSidebarNav"] a span {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* Títulos y texto */

        h1,
        h2,
        h3,
        h4 {
            color: var(--inc-black) !important;
            letter-spacing: -0.03em;
        }

        h1 {
            font-weight: 800 !important;
        }

        h2,
        h3 {
            font-weight: 750 !important;
        }

        p,
        li {
            color: #4F4F57;
        }

        /* Contenedores */

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border-color: var(--inc-border) !important;
            border-radius: 20px !important;
            box-shadow: 0 7px 24px rgba(24, 24, 27, 0.035);
        }

        /* Formularios */

        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1px solid var(--inc-border);
            border-radius: 22px;
            padding: 1.7rem 1.9rem 2rem;
            box-shadow: 0 8px 26px rgba(24, 24, 27, 0.035);
        }

        /* Etiquetas */

        [data-testid="stWidgetLabel"] {
            opacity: 1 !important;
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] span {
            color: var(--inc-black) !important;
            font-size: 0.86rem !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }

        /* Inputs de texto y números */

        [data-baseweb="input"] > div,
        [data-baseweb="base-input"],
        [data-baseweb="textarea"] {
            background: var(--inc-dark) !important;
            border-color: #3C3C45 !important;
            color: #FFFFFF !important;
            border-radius: 9px !important;
        }

        [data-baseweb="input"] input,
        [data-baseweb="base-input"] input,
        [data-baseweb="textarea"] textarea {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        [data-baseweb="input"] input::placeholder,
        [data-baseweb="textarea"] textarea::placeholder {
            color: #B8B8C0 !important;
            opacity: 1 !important;
        }

        /* Selectbox simple */

        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: var(--inc-dark) !important;
            border-color: #3C3C45 !important;
            color: #FFFFFF !important;
            border-radius: 9px !important;
        }

        [data-testid="stSelectbox"] [data-baseweb="select"] span,
        [data-testid="stSelectbox"] [data-baseweb="select"] div {
            color: #FFFFFF !important;
        }

        [data-testid="stSelectbox"] [data-baseweb="select"] svg {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        /* Multiselect legible */

        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            min-height: 46px;
            background: #FFFFFF !important;
            border: 1px solid #D8D8DD !important;
            border-radius: 9px !important;
            color: var(--inc-black) !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="select"] input {
            color: var(--inc-black) !important;
            -webkit-text-fill-color: var(--inc-black) !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder {
            color: #767680 !important;
            opacity: 1 !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
            color: #5F5F67 !important;
            fill: #5F5F67 !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] {
            background: var(--inc-pink-soft) !important;
            border: 1px solid rgba(245, 47, 139, 0.18) !important;
            border-radius: 999px !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
            color: var(--inc-pink-dark) !important;
            font-weight: 650 !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
            color: var(--inc-pink-dark) !important;
            fill: var(--inc-pink-dark) !important;
        }

        /* Menús desplegables */

        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background: #FFFFFF !important;
            color: var(--inc-black) !important;
        }

        [data-baseweb="popover"] * {
            color: var(--inc-black) !important;
        }

        [role="option"] {
            background: #FFFFFF !important;
            color: var(--inc-black) !important;
        }

        [role="option"] span,
        [role="option"] div {
            color: var(--inc-black) !important;
        }

        [role="option"]:hover,
        [role="option"][aria-selected="true"] {
            background: var(--inc-pink-soft) !important;
            color: var(--inc-pink-dark) !important;
        }

        /* Tabs */

        [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }

        button[data-baseweb="tab"] {
            color: #5F5F67 !important;
            font-weight: 650 !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"] p {
            color: #5F5F67 !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--inc-pink-dark) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] p {
            color: var(--inc-pink-dark) !important;
        }

        [data-baseweb="tab-highlight"] {
            background-color: var(--inc-pink) !important;
        }

        /* Métricas */

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--inc-border);
            border-radius: 15px;
            padding: 0.9rem 1rem;
        }

        [data-testid="stMetricLabel"] p {
            color: var(--inc-gray) !important;
            font-size: 0.77rem !important;
            font-weight: 650 !important;
            opacity: 1 !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--inc-black) !important;
            font-weight: 800 !important;
        }

        /* Botones */

        .stButton > button,
        .stFormSubmitButton > button {
            width: 100%;
            min-height: 44px;
            border-radius: 11px;
            font-weight: 700;
            transition: all 0.15s ease;
        }

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            color: #FFFFFF !important;
            border: none !important;
            background:
                linear-gradient(
                    90deg,
                    var(--inc-pink),
                    #FF4D4D
                ) !important;
            box-shadow:
                0 8px 20px rgba(245, 47, 139, 0.2);
        }

        .stButton > button[kind="primary"] p,
        .stFormSubmitButton > button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow:
                0 11px 24px rgba(245, 47, 139, 0.28);
        }

        .stButton > button[kind="secondary"] {
            color: var(--inc-black) !important;
            background: #FFFFFF !important;
            border: 1px solid #DADADD !important;
        }

        .stButton > button[kind="secondary"] p {
            color: var(--inc-black) !important;
        }

        /* Alertas */

        [data-testid="stAlert"] {
            border-radius: 14px;
            padding-top: 0.85rem;
            padding-bottom: 0.85rem;
        }

        [data-testid="stAlert"] p {
            color: inherit !important;
        }

        /* Progreso */

        [data-testid="stProgress"] > div > div {
            background: var(--inc-pink) !important;
        }

        /* Textos secundarios */

        [data-testid="stCaptionContainer"] p,
        .stCaptionContainer p {
            color: var(--inc-gray) !important;
            opacity: 1 !important;
        }

        [data-testid="InputInstructions"] {
            color: var(--inc-gray) !important;
        }

        hr {
            border-color: var(--inc-border) !important;
            margin-top: 1.8rem !important;
            margin-bottom: 1.6rem !important;
        }

        
        /* =========================================================
           COMPONENTES DASHBOARD
        ========================================================= */

        .dashboard-status-card{
            background:#FFFFFF;
            border:1px solid var(--inc-border);
            border-radius:18px;
            padding:1.15rem 1.25rem;
            box-shadow:0 7px 24px rgba(24,24,27,.035);
        }

        .dashboard-status-label{
            color:var(--inc-gray);
            font-size:.82rem;
            font-weight:700;
            margin-bottom:.45rem;
        }

        .dashboard-status-value{
            color:var(--inc-black);
            font-size:1.45rem;
            font-weight:800;
            line-height:1.2;
            overflow-wrap:anywhere;
        }

        .dashboard-chip-row{
            display:flex;
            flex-wrap:wrap;
            gap:.45rem;
            margin-top:.8rem;
        }

        .dashboard-chip{
            display:inline-flex;
            align-items:center;
            padding:.38rem .72rem;
            border-radius:999px;
            background:var(--inc-pink-soft);
            border:1px solid rgba(245,47,139,.15);
            color:var(--inc-pink-dark);
            font-size:.78rem;
            font-weight:700;
        }

        .priority-badge{
            display:flex;
            justify-content:center;
            align-items:center;
            width:100%;
            min-height:44px;
            border-radius:12px;
            font-weight:800;
            text-align:center;
            line-height:1.2;
            padding:.55rem .8rem;
        }

        .priority-immediate{
            background:#FDE8E8;
            border:1px solid #F5B6B6;
            color:#991B1B;
        }

        .priority-high{
            background:#FFF4B5;
            border:1px solid #E4D277;
            color:#5F4500;
        }

        .priority-medium{
            background:#EAF1FF;
            border:1px solid #C8D8F7;
            color:#1E4F91;
        }


        @media (max-width: 800px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            [data-testid="stForm"] {
                padding: 1.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
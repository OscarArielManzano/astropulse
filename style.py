"""Offline visual theme shared by the Streamlit UI and Plotly figures."""
import streamlit as st


COLORS = {
    "green": "#28D21B",
    "yellow": "#E4E51A",
    "red": "#FF626F",
    "baseline": "#94A3B8",
    "line": "#30A4E0",
    "background": "#0B0B20",
    "text": "#F5F6FA",
    "surface": "#192638",
    "border": "#304156",
}

PLOTLY_COLORWAY = [COLORS["line"], COLORS["yellow"], COLORS["green"],
                   COLORS["red"], COLORS["baseline"]]


def apply_style():
    """Inject presentation styles without external fonts or image requests."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0B0B20;
            background-image:
                radial-gradient(circle at 12% 18%, #94a3b825 0 1px, transparent 2px),
                radial-gradient(circle at 72% 35%, #30a4e015 0 1px, transparent 2px),
                radial-gradient(ellipse at 80% 10%, #181831 0%, transparent 55%);
            background-size: 173px 191px, 257px 239px, 100% 100%;
            color: #F5F6FA;
        }
        [data-testid="stHeader"] { background: #0b0b20ed; }
        [data-testid="stSidebar"] { background: #192638; border-right: 1px solid #304156; }
        .stMainBlockContainer { max-width: 1240px; padding: 2rem 2rem 3rem; }
        .stApp, .stApp p, .stApp input, .stApp textarea,
        .stApp button, .stApp select {
            font-family: "Courier New", Courier, monospace;
        }
        h1, h2, h3, [data-testid="stMetricLabel"] {
            font-family: "Courier New", Courier, monospace;
            color: #F5F6FA;
        }
        h1, h1 a {
            font-family: Arial, Helvetica, sans-serif;
            font-weight: 400;
            letter-spacing: .025em;
            text-transform: uppercase;
        }
        h2, h3 { font-weight: 700; letter-spacing: .015em; text-transform: uppercase; }
        [data-testid="stCaptionContainer"] { color: #B9C5D6; }
        [data-testid="stMetric"] {
            background: #192638;
            border: 1px solid #304156;
            border-radius: 10px;
            padding: 1rem 1.15rem;
            height: 100%;
        }
        [data-testid="stMetricLabel"] { font-weight: 700; }
        [data-testid="stMetricValue"] {
            font-family: "Courier New", Courier, monospace;
            font-size: clamp(1.25rem, 2.5vw, 1.9rem);
            font-weight: 700;
            color: #F5F6FA;
        }
        .st-key-domain_statuses [data-testid="stMetric"] { min-height: 118px; }
        .st-key-domain_statuses [data-testid="stHorizontalBlock"] {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
        }
        .st-key-domain_statuses [data-testid="stColumn"] { width: 100%; min-width: 0; }
        .st-key-domain_statuses [data-testid="stMetricLabel"] {
            text-transform: uppercase;
            letter-spacing: .025em;
        }
        .st-key-domain_statuses [data-testid="stMetricLabel"] p {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
        }
        .st-key-domain_statuses [data-testid="stMetricValue"] { text-transform: uppercase; }
        [class*="st-key-domain_level_0_"] [data-testid="stMetricValue"] { color: #28D21B; }
        [class*="st-key-domain_level_1_"] [data-testid="stMetricValue"] { color: #E4E51A; }
        [class*="st-key-domain_level_2_"] [data-testid="stMetricValue"] { color: #FF626F; }
        [data-testid="stExpander"], [data-testid="stForm"],
        [data-testid="stFileUploader"] {
            background: #192638;
            border-radius: 10px;
        }
        [data-testid="stExpander"] details, [data-testid="stForm"] {
            border-color: #304156;
        }
        [data-testid="stFileUploader"] { padding: .8rem 1rem; }
        [data-testid="stFileUploaderDropzone"] { background: #142032; }
        [data-testid="stAlert"] {
            border: 1px solid #304156;
            border-radius: 10px;
        }
        [data-testid="stAlert"] p {
            font-family: "Courier New", Courier, monospace;
            line-height: 1.6;
        }
        [data-testid="stPlotlyChart"] {
            background: #192638;
            border: 1px solid #304156;
            border-radius: 10px;
            overflow: hidden;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: #192638;
            border-radius: 10px;
            padding: .25rem .75rem;
            gap: 1.5rem;
        }
        .stTabs [data-baseweb="tab"] { color: #B9C5D6; }
        .stTabs [aria-selected="true"] { color: #30A4E0; }
        .stButton button, .stDownloadButton button, .stFormSubmitButton button {
            border-radius: 8px;
            border-color: #40566F;
            background: #192638;
            color: #F5F6FA;
        }
        .stButton button:hover, .stDownloadButton button:hover,
        .stFormSubmitButton button:hover {
            border-color: #30A4E0;
            color: #30A4E0;
        }
        @media (max-width: 640px) {
            .stMainBlockContainer { padding: 1.25rem 1rem 2rem; }
            .stTabs [data-baseweb="tab-list"] { gap: .5rem; }
            .st-key-domain_statuses [data-testid="stHorizontalBlock"] {
                grid-template-columns: minmax(0, 1fr);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

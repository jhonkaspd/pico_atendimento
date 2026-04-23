# =========================================================
# Bloco 1 — Imports
# =========================================================

import io
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textwrap import dedent
import os
import shutil
import tempfile
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import streamlit as st

# =========================================================
# Bloco 2 — Configuração da página
# =========================================================

st.set_page_config(
    page_title="Dashboard Executivo | Fluxo de Atendimento",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# Bloco 3 — Definição das cores
# =========================================================
COLORS = {
    "primary":       "#00995D",
    "primary_light": "#B6D44C",
    "deep":          "#004B52",
    "alert":         "#F47920",
    "danger":        "#C94F4F",
    "danger_dark":   "#8F2D2D",
    "warning":       "#F0B24A",
    "success":       "#00995D",
    "info":          "#2E7D8A",
    "bg":            "#F4F8F6",
    "surface":       "#FFFFFF",
    "surface_soft":  "#EEF5F1",
    "surface_deep":  "#073B3A",
    "border":        "#D8E4DD",
    "text":          "#18302B",
    "muted":         "#6B7D76",
    "grid":          "#E8EFEB",
    "white":         "#FFFFFF",
    "support_ice":   "#C7DEE2",
    "support_mint":  "#C1D0B9",
    "support_warm":  "#F4E2B1",
    "support_blush": "#E5C6C0",
}

# =========================================================
# Bloco 4 — CSS / identidade visual
# =========================================================
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {COLORS["text"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(182,212,76,0.10), transparent 24%),
                radial-gradient(circle at top left,  rgba(0,153,93,0.08),   transparent 28%),
                linear-gradient(180deg, #F7FBF8 0%, #F2F7F4 100%);
        }}

        .block-container {{
            max-width: 1580px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #083A39 0%, #052F2F 100%) !important;
            border-right: 2px solid rgba(255,255,255,0.14);
            min-width: 325px !important;
            box-shadow: 8px 0 26px rgba(0,0,0,0.18);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background: linear-gradient(180deg, #083A39 0%, #052F2F 100%) !important;
        }}

        [data-testid="stSidebar"] * {{
            color: #ECF8F2 !important;
        }}

        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {{
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            border-radius: 14px;
        }}

        [data-testid="stSidebar"] input {{
            color: #ECF8F2 !important;
            background: transparent !important;
        }}

        /* ── File uploader na sidebar ── */
        [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
            background: transparent !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {{
            background: rgba(255,255,255,0.06) !important;
            border: 1.5px dashed rgba(255,255,255,0.22) !important;
            border-radius: 14px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] * {{
            color: rgba(236,248,242,0.75) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] small,
        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] span {{
            color: rgba(236,248,242,0.50) !important;
        }}

        /* Botão "Browse files" dentro do uploader */
        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button {{
            background: rgba(0,153,93,0.28) !important;
            border: 1px solid rgba(0,153,93,0.45) !important;
            color: #ECF8F2 !important;
            border-radius: 10px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button:hover {{
            background: rgba(0,153,93,0.45) !important;
        }}

        /* ── Expander "Trocar arquivo" na sidebar ── */
        [data-testid="stSidebar"] [data-testid="stExpander"] {{
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 16px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
            color: #ECF8F2 !important;
            background: transparent !important;
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] > div > div {{
            background: transparent !important;
        }}

        /* ── Botão "Remover" e demais botões secundários na sidebar ── */
        [data-testid="stSidebar"] button {{
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            color: #ECF8F2 !important;
            border-radius: 10px !important;
        }}

        [data-testid="stSidebar"] button:hover {{
            background: rgba(255,255,255,0.18) !important;
            border-color: rgba(255,255,255,0.35) !important;
        }}

        /* ── Date inputs — texto e ícones visíveis ── */
        [data-testid="stSidebar"] [data-baseweb="input"] input,
        [data-testid="stSidebar"] .stDateInput input {{
            color: #ECF8F2 !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="input"] svg,
        [data-testid="stSidebar"] .stDateInput svg {{
            fill: rgba(236,248,242,0.65) !important;
        }}

        #MainMenu, footer, header {{
            visibility: hidden;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg,
                    rgba(0,75,82,0.98) 0%,
                    rgba(0,153,93,0.94) 58%,
                    rgba(182,212,76,0.88) 100%);
            border-radius: 26px;
            padding: 1.5rem 1.6rem;
            box-shadow: 0 16px 40px rgba(0,75,82,0.18);
            border: 1px solid rgba(255,255,255,0.14);
            margin-bottom: 1rem;
        }}

        .hero:before {{
            content: "";
            position: absolute;
            right: -30px; top: -30px;
            width: 220px; height: 220px;
            border-radius: 50%;
            background: rgba(255,255,255,0.08);
            filter: blur(5px);
        }}

        .hero-title {{
            color: white;
            font-size: 1.9rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.03em;
            margin-bottom: 0.25rem;
        }}

        .hero-sub {{
            color: rgba(255,255,255,0.90);
            font-size: 0.97rem;
            line-height: 1.5;
            margin-bottom: 0.9rem;
            max-width: 980px;
        }}

        .hero-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            color: white;
            font-size: 0.77rem;
            font-weight: 700;
            border: 1px solid rgba(255,255,255,0.14);
            backdrop-filter: blur(6px);
        }}

        .section-title {{
            margin-top: 0.9rem;
            margin-bottom: 0.7rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}

        .section-title .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});
            box-shadow: 0 0 0 4px rgba(0,153,93,0.10);
        }}

        .section-title .text {{
            font-size: 0.83rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: {COLORS["deep"]};
        }}

        .caption-box {{
            background: linear-gradient(180deg, rgba(193,208,185,0.22), rgba(255,255,255,0.76));
            border: 1px solid {COLORS["border"]};
            padding: 0.8rem 0.95rem;
            border-radius: 16px;
            color: {COLORS["muted"]};
            font-size: 0.82rem;
            margin-bottom: 0.85rem;
        }}

        .kpi-card {{
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, rgba(255,255,255,0.99) 0%, rgba(248,252,249,0.98) 100%);
            border: 1px solid {COLORS["border"]};
            border-radius: 22px;
            padding: 1rem 1.05rem 0.95rem 1.05rem;
            min-height: 138px;
            box-shadow: 0 12px 26px rgba(0,75,82,0.07);
        }}

        .kpi-card:before {{
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: var(--accent);
        }}

        .kpi-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.55rem;
        }}

        .kpi-icon {{
            width: 38px;
            height: 38px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            background: var(--accent-soft);
        }}

        .kpi-label {{
            font-size: 0.74rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {COLORS["muted"]};
        }}

        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.72rem;
            font-weight: 800;
            color: var(--accent);
            line-height: 1.0;
            margin-bottom: 0.35rem;
        }}

        .kpi-sub {{
            font-size: 0.82rem;
            color: {COLORS["muted"]};
            line-height: 1.35;
            min-height: 40px;
        }}

        .kpi-bar {{
            margin-top: 0.65rem;
            height: 8px;
            border-radius: 999px;
            background: #EAF2EE;
            overflow: hidden;
        }}

        .kpi-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }}

        .insight-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(243,249,245,0.96));
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 24px rgba(0,75,82,0.05);
            min-height: 125px;
        }}

        .insight-title {{
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {COLORS["deep"]};
            margin-bottom: 0.45rem;
        }}

        .insight-text {{
            font-size: 0.84rem;
            line-height: 1.5;
            color: {COLORS["muted"]};
        }}

        .info-note {{
            background: rgba(255,255,255,0.82);
            border: 1px solid {COLORS["border"]};
            border-left: 4px solid {COLORS["deep"]};
            border-radius: 14px;
            padding: 0.75rem 0.9rem;
            color: {COLORS["muted"]};
            font-size: 0.80rem;
            line-height: 1.55;
            margin-top: 0.35rem;
            margin-bottom: 0.6rem;
        }}

        .footer-note {{
            color: {COLORS["muted"]};
            font-size: 0.75rem;
            text-align: center;
            padding-top: 1rem;
            margin-top: 1rem;
            border-top: 1px solid {COLORS["border"]};
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.84);
            border: 1px solid {COLORS["border"]};
            border-radius: 16px;
            padding: 0.75rem 0.9rem;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            background: rgba(255,255,255,0.76);
        }}

        .stTabs {{
            margin-top: 1rem;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            padding-bottom: 2px;
            border-bottom: 1px solid {COLORS["border"]};
            margin-bottom: 0;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.72);
            border-radius: 12px 12px 0 0;
            border: 1px solid {COLORS["border"]};
            border-bottom: none;
            padding: 9px 16px;
            font-weight: 700;
            color: {COLORS["deep"]};
            margin-bottom: -1px;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(180deg, rgba(0,153,93,0.10), rgba(182,212,76,0.12));
            border-color: rgba(0,153,93,0.35);
            border-bottom-color: transparent;
        }}

        .stTabs [data-baseweb="tab-panel"] {{
            padding-top: 1rem;
            padding-left: 0;
            padding-right: 0;
        }}

        .sidebar-divider {{
            height: 1px;
            background: rgba(255,255,255,0.10);
            margin: 1rem 0 1rem 0;
        }}

        .sidebar-section-title {{
            font-size: 0.80rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: rgba(236,248,242,0.92);
            margin-bottom: 0.65rem;
        }}

        .sidebar-info-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.07));
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        .sidebar-info-title {{
            font-size: 0.88rem;
            font-weight: 800;
            color: #ECF8F2;
            margin-bottom: 0.2rem;
        }}

        .sidebar-info-periodo {{
            font-size: 0.78rem;
            color: rgba(236,248,242,0.78);
            margin-bottom: 0.8rem;
        }}

        .sidebar-info-subtitle {{
            font-size: 0.73rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: rgba(236,248,242,0.82);
            margin-bottom: 0.55rem;
        }}

        .sidebar-info-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            padding: 0.34rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            font-size: 0.78rem;
            color: rgba(236,248,242,0.86);
        }}

        .sidebar-info-item:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .sidebar-info-item strong {{
            color: #FFFFFF;
            font-weight: 800;
        }}

        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stDateInput label {{
            font-weight: 700 !important;
            color: #ECF8F2 !important;
        }}

        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stDateInput > div > div {{
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            border-radius: 16px !important;
            min-height: 48px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }}

        .sidebar-status-card {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background: linear-gradient(180deg, rgba(0,153,93,0.18), rgba(182,212,76,0.10));
            border: 1px solid rgba(182,212,76,0.30);
            border-radius: 18px;
            padding: 0.85rem 0.95rem;
            margin-top: 0.85rem;
            margin-bottom: 0.9rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        .sidebar-status-icon {{
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.14);
            font-size: 1.15rem;
            flex-shrink: 0;
        }}

        .sidebar-status-title {{
            font-size: 0.84rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.08rem;
        }}

        .sidebar-status-sub {{
            font-size: 0.75rem;
            color: rgba(236,248,242,0.82);
            line-height: 1.35;
        }}

        .sidebar-upload-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.07));
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            margin-top: 0.75rem;
            margin-bottom: 0.8rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        .sidebar-upload-top {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.65rem;
        }}

        .sidebar-upload-icon {{
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.14);
            font-size: 1.05rem;
            flex-shrink: 0;
        }}

        .sidebar-upload-title {{
            font-size: 0.84rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.08rem;
        }}

        .sidebar-upload-sub {{
            font-size: 0.75rem;
            color: rgba(236,248,242,0.82);
            line-height: 1.35;
        }}

        .sidebar-upload-meta {{
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            font-size: 0.75rem;
            color: rgba(236,248,242,0.84);
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255,255,255,0.08);
        }}

        .sidebar-upload-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            background: rgba(182,212,76,0.14);
            border: 1px solid rgba(182,212,76,0.22);
            font-size: 0.72rem;
            font-weight: 700;
            color: #ECF8F2;
        }}

        .sidebar-file-card {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.07));
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 20px;
            padding: 1rem;
            margin-top: 0.7rem;
            margin-bottom: 0.7rem;
        }}

        .sidebar-file-icon {{
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.12);
            font-size: 1.1rem;
            flex-shrink: 0;
        }}

        .sidebar-file-content {{
            min-width: 0;
            flex: 1;
        }}

        .sidebar-file-title {{
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: rgba(236,248,242,0.72);
            margin-bottom: 0.18rem;
        }}

        .sidebar-file-name {{
            font-size: 0.92rem;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.3;
            word-break: break-word;
            margin-bottom: 0.45rem;
        }}

        .sidebar-file-meta {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .sidebar-file-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            background: rgba(182,212,76,0.14);
            border: 1px solid rgba(182,212,76,0.22);
            font-size: 0.72rem;
            font-weight: 700;
            color: #ECF8F2;
        }}

        [data-testid="stSidebar"] div[data-testid="stExpander"] {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

# =========================================================
# Bloco 5 — Constantes
# =========================================================
SERVICO_MAP = {
    "Realização de Exames": "Realização de Exames",
    "Laboratório - Realização de Exames": "Realização de Exames",
    "Exames Laboratoriais": "Realização de Exames",
    "Laboratório": "Realização de Exames",
    "Exame Especial": "Realização de Exames",
    "Exames Agendados": "Realização de Exames",
    "Coleta de exames": "Coleta de Exames",
    "Coleta": "Coleta de Exames",
    "Coleta de Exames  térreo": "Coleta de Exames",
    "Coleta de Material Pendente": "Coleta de Material Pendente",
    "Coleta de Materiais Pendentes": "Coleta de Material Pendente",
    "Coleta de  Materiais Pendentes": "Coleta de Material Pendente",
    "Entrega de Materiais Pendentes": "Entrega de Material Pendente",
    "Entrega de  Materiais Pendentes": "Entrega de Material Pendente",
    "Laboratório - Entrega de Material Pendente": "Entrega de Material Pendente",
    "Entrega de Resultado de Exame": "Entrega Resultado",
}

ETAPA_LIMITES = {
    "1.Espera Recepção": 7,
    "2.Recepção": 10,
    "3.Espera Coleta": 7,
    "4.Coleta": 6,
}

COLUNAS_OBRIGATORIAS = [
    "ID", "Inicio", "Fim", "Etapa", "TipoAtendimento", "Operador",
    "FuncaoOperador", "Prioridade", "Servico", "tEtapa", "Unidade"
]

COLUNAS_NOVA_BASE = [
    "Unidade", "ID",
    "Bil_Emissao", "Bil_ChamadaRecepcao", "Bil_EncaminhaColeta",
    "Bil_ChamadaColeta", "Bil_Finalizacao",
    "TipoAtendimento", "Operador_Recepcao", "Operador_Coleta",
    "ServicoOrdem1", "ServicoOrdem2",
]

DIAS_SEMANA_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MAPA_DIAS_PT = {
    "Monday": "Seg",
    "Tuesday": "Ter",
    "Wednesday": "Qua",
    "Thursday": "Qui",
    "Friday": "Sex",
    "Saturday": "Sáb",
    "Sunday": "Dom",
}

# =========================================================
# Bloco 6 — Helpers de formatação
# =========================================================
def _fmt_int(v):
    return f"{int(round(v)):,}".replace(",", ".")

def _fmt_float(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _fmt_min(v):
    return f"{_fmt_float(v, 1)} min"

# =========================================================
# Bloco 7 — Componentes visuais
# =========================================================
def section_header(title):
    st.markdown(
        f"""
        <div class="section-title">
            <span class="dot"></span>
            <span class="text">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def info_note(text):
    st.markdown(f"""<div class="info-note">{text}</div>""", unsafe_allow_html=True)

def caption_box(text):
    st.markdown(f"""<div class="caption-box">{text}</div>""", unsafe_allow_html=True)

def insight_card(title, text):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{title}</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi_card(label, value, sub, accent, icon="•", fill=0.7, accent_2=None):
    accent_2 = accent_2 or COLORS["primary_light"]
    accent_soft = f"{accent}22"
    fill_pct = max(0, min(fill, 1)) * 100

    return f"""
    <div class="kpi-card" style="--accent:{accent}; --accent-2:{accent_2}; --accent-soft:{accent_soft}">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        <div class="kpi-bar">
            <div class="kpi-fill" style="width:{fill_pct:.0f}%"></div>
        </div>
    </div>
    """

def plot_layout(title=None, height=380, legend="default", margin=None, **kwargs):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.76)",
        font=dict(family="Inter, sans-serif", size=12, color=COLORS["text"]),
        height=height,
        hoverlabel=dict(
            bgcolor=COLORS["deep"],
            font_color=COLORS["white"],
            font_size=12,
            font_family="Inter, sans-serif",
        ),
        margin=margin if margin is not None else dict(l=8, r=8, t=50, b=8),
    )

    if title is not None:
        base["title"] = dict(
            text=title,
            x=0,
            font=dict(size=15, color=COLORS["deep"]),
        )

    if legend == "default":
        base["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        )
    elif legend is not None:
        base["legend"] = legend

    base.update(kwargs)
    return base

# =========================================================
# Bloco 8 — Carga e ETL
# =========================================================
@st.cache_data(show_spinner=False)
def load_data(uploaded_file, sheet_name=None):
    if uploaded_file is None:
        return None

    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name or 0)
    elif suffix == ".csv":
        df = pd.read_csv(uploaded_file)
    else:
        raise ValueError("Formato não suportado. Use CSV ou Excel.")

    return df


def add_weekday_columns(df, datetime_col, label_col="DiaSemanaLabel"):
    serie = pd.to_datetime(df[datetime_col], errors="coerce")
    dia_semana = serie.dt.day_name()
    df["DiaSemana"] = pd.Categorical(dia_semana, categories=DIAS_SEMANA_EN, ordered=True)
    df[label_col] = pd.Categorical(
        df["DiaSemana"].map(MAPA_DIAS_PT),
        categories=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        ordered=True,
    )
    return df


def transformar_nova_base(df_raw):
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS), {
            "total_linhas": 0,
            "atendimentos_validos": 0,
            "atendimentos_descartados": 0,
            "tipos_invalidos": 0,
            "etapas_geradas": 0,
        }

    df = df_raw.copy()

    faltantes = [c for c in COLUNAS_NOVA_BASE if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas ausentes na nova base: {faltantes}")

    total_linhas = len(df)

    for col in [
        "Bil_Emissao", "Bil_ChamadaRecepcao", "Bil_EncaminhaColeta",
        "Bil_ChamadaColeta", "Bil_Finalizacao"
    ]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in [
        "Unidade", "ID", "TipoAtendimento", "Operador_Recepcao",
        "Operador_Coleta", "ServicoOrdem1", "ServicoOrdem2"
    ]:
        df[col] = df[col].astype(str).str.strip()

    df = df.replace({"nan": np.nan, "None": np.nan, "NaT": np.nan, "": np.nan})

    df["TipoAtendimento"] = df["TipoAtendimento"].replace({
        "Guiche": "Guichê",
        "GUICHE": "Guichê",
        "guiche": "Guichê",
        "guichê": "Guichê",
        "totem": "Totem",
        "TOTEM": "Totem",
    })

    df["Servico"] = df["ServicoOrdem2"].where(df["ServicoOrdem2"].notna(), df["ServicoOrdem1"])
    df["Servico"] = df["Servico"].fillna("Não informado")
    df["Prioridade"] = "Normal"

    etapas = []
    ids_descartados = set()
    ids_tipo_invalido = set()

    def add_etapa(row, nome, ini_col, fim_col, operador=None, funcao_operador=None):
        ini = row[ini_col]
        fim = row[fim_col]

        if pd.isna(ini) or pd.isna(fim):
            return
        if fim < ini:
            return

        etapas.append({
            "ID": row["ID"],
            "Inicio": ini,
            "Fim": fim,
            "Etapa": nome,
            "TipoAtendimento": row["TipoAtendimento"],
            "Operador": row[operador] if operador else np.nan,
            "FuncaoOperador": funcao_operador if operador else np.nan,
            "Prioridade": row["Prioridade"],
            "Servico": row["Servico"],
            "tEtapa": (fim - ini).total_seconds() / 60,
            "Unidade": row["Unidade"],
        })

    for _, row in df.iterrows():
        tipo = row["TipoAtendimento"]
        id_at = row["ID"]
        etapas_antes = len(etapas)

        if tipo == "Guichê":
            add_etapa(row, "1.Espera Recepção", "Bil_Emissao", "Bil_ChamadaRecepcao")
            add_etapa(row, "2.Recepção", "Bil_ChamadaRecepcao", "Bil_EncaminhaColeta", "Operador_Recepcao", "Recepção")
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao", "Operador_Coleta", "Coleta")

        elif tipo == "Totem":
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao", "Operador_Coleta", "Coleta")

        else:
            ids_tipo_invalido.add(id_at)

        if len(etapas) == etapas_antes:
            ids_descartados.add(id_at)

    df_etapas = pd.DataFrame(etapas)

    if df_etapas.empty:
        raise ValueError(
            "A transformação não gerou etapas válidas. Verifique as colunas de data/hora e o TipoAtendimento."
        )

    ordem_etapas = {
        "1.Espera Recepção": 1,
        "2.Recepção": 2,
        "3.Espera Coleta": 3,
        "4.Coleta": 4,
    }

    df_etapas["OrdemEtapa"] = df_etapas["Etapa"].map(ordem_etapas).fillna(99)
    df_etapas = df_etapas.sort_values(["Inicio", "ID", "OrdemEtapa"]).drop(columns="OrdemEtapa")
    df_etapas = df_etapas[COLUNAS_OBRIGATORIAS].reset_index(drop=True)

    qualidade = {
        "total_linhas": total_linhas,
        "atendimentos_validos": df_etapas["ID"].nunique(),
        "atendimentos_descartados": len(ids_descartados),
        "tipos_invalidos": len(ids_tipo_invalido),
        "etapas_geradas": len(df_etapas),
    }

    return df_etapas, qualidade


def preprocess_data(df_raw):
    df = df_raw.copy()

    missing = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")
    df["Fim"] = pd.to_datetime(df["Fim"], errors="coerce")
    df["tEtapa"] = pd.to_numeric(df["tEtapa"], errors="coerce")

    df = df.dropna(subset=["ID", "Inicio", "Fim", "Etapa", "Unidade"]).copy()
    df = df[df["Fim"] >= df["Inicio"]].copy()

    df["Servico"] = df["Servico"].replace(SERVICO_MAP)
    df["DuracaoMin"] = ((df["Fim"] - df["Inicio"]).dt.total_seconds() / 60).clip(lower=0)
    df["Data"] = df["Inicio"].dt.date
    df["Hora"] = df["Inicio"].dt.hour
    df = add_weekday_columns(df, "Inicio")
    df["MesRef"] = df["Inicio"].dt.to_period("M").astype(str)

    return df

# =========================================================
# Bloco 9 — Funções analíticas
# =========================================================
@st.cache_data(show_spinner=False)
def build_minute_level(df):
    work = df.copy()

    work["Minuto"] = work.apply(
        lambda row: pd.date_range(
            start=row["Inicio"].floor("min"),
            end=(row["Fim"] - pd.Timedelta(seconds=1)).floor("min"),
            freq="min",
        ) if row["Fim"] > row["Inicio"]
        else pd.DatetimeIndex([row["Inicio"].floor("min")]),
        axis=1,
    )

    exploded = work.explode("Minuto", ignore_index=True)
    exploded["Data"] = exploded["Minuto"].dt.date
    exploded["HoraMin"] = exploded["Minuto"].dt.strftime("%H:%M")
    exploded["Hora"] = exploded["Minuto"].dt.hour

    simultaneos = (
        exploded.groupby(["Unidade", "Minuto"])["ID"]
        .nunique()
        .reset_index(name="PacientesSimultaneos")
    )
    simultaneos["Data"] = simultaneos["Minuto"].dt.date
    simultaneos["Hora"] = simultaneos["Minuto"].dt.hour
    simultaneos["HoraMin"] = simultaneos["Minuto"].dt.strftime("%H:%M")
    simultaneos = add_weekday_columns(simultaneos, "Minuto")

    return exploded, simultaneos


def apply_filters(df, unidades, etapas, servicos, operadores, periodo):
    out = df.copy()

    if unidades:
        out = out[out["Unidade"].isin(unidades)]
    if etapas:
        out = out[out["Etapa"].isin(etapas)]
    if servicos:
        out = out[out["Servico"].isin(servicos)]
    if operadores:
        out = out[out["Operador"].isin(operadores)]

    if periodo and len(periodo) == 2:
        ini, fim = periodo
        ini = pd.to_datetime(ini)
        fim = pd.to_datetime(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        out = out[(out["Inicio"] >= ini) & (out["Inicio"] <= fim)]

    return out


def make_kpis(df_f, simultaneos_f):
    # Pico simultâneo: se filtro por unidade → pico da(s) unidade(s) selecionada(s)
    # sem filtro → pico da soma de todas as unidades por minuto (total global)
    if not simultaneos_f.empty:
        total_por_minuto = (
            simultaneos_f.groupby("Minuto")["PacientesSimultaneos"]
            .sum()
            .reset_index(name="TotalSimultaneos")
        )
        idx_pico = total_por_minuto["TotalSimultaneos"].idxmax()
        pico_max  = int(total_por_minuto.loc[idx_pico, "TotalSimultaneos"])
        hora_pico = total_por_minuto.loc[idx_pico, "Minuto"]
    else:
        pico_max  = 0
        hora_pico = pd.NaT

    return {
        "registros":     len(df_f),
        "atendimentos":  df_f["ID"].nunique(),
        "unidades":      df_f["Unidade"].nunique(),
        "operadores":    df_f["Operador"].dropna().nunique(),
        "duracao_media": df_f["DuracaoMin"].mean(),
        "pico_max":      pico_max,
        "hora_pico":     hora_pico,
    }


def make_insights(df_f, simultaneos_f):
    insights = []
    if df_f.empty:
        return insights

    etapa_tempo = (
        df_f.groupby("Etapa", as_index=False)["DuracaoMin"]
        .mean()
        .sort_values("DuracaoMin", ascending=False)
    )
    top_etapa = etapa_tempo.iloc[0]

    unid_volume = df_f.groupby("Unidade")["ID"].nunique().sort_values(ascending=False)
    top_unidade = unid_volume.index[0]
    top_val = unid_volume.iloc[0]

    conformidade = []
    for etapa, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa]
        if not base.empty:
            conformidade.append({
                "Etapa": etapa,
                "Conformidade": (base["DuracaoMin"] <= limite).mean() * 100,
                "Limite": limite,
            })

    conf_df = pd.DataFrame(conformidade).sort_values("Conformidade")
    pior_conf = conf_df.iloc[0] if not conf_df.empty else None

    if not simultaneos_f.empty:
        picos_unid = simultaneos_f.groupby("Unidade")["PacientesSimultaneos"].max().sort_values(ascending=False)
        unid_pico = picos_unid.index[0]
        valor_pico = picos_unid.iloc[0]
        momento_pico = simultaneos_f.loc[simultaneos_f["PacientesSimultaneos"].idxmax(), "Minuto"]
    else:
        unid_pico, valor_pico, momento_pico = "-", 0, pd.NaT

    insights.append({
        "title": "Maior gargalo médio",
        "text": f"<b>{top_etapa['Etapa']}</b> lidera com tempo médio de <b>{_fmt_float(top_etapa['DuracaoMin'])} min</b>."
    })
    insights.append({
        "title": "Maior volume",
        "text": f"<b>{top_unidade}</b> concentra <b>{_fmt_int(top_val)} atendimentos</b> no período filtrado."
    })

    if pior_conf is not None:
        insights.append({
            "title": "Maior risco de SLA",
            "text": f"<b>{pior_conf['Etapa']}</b> tem conformidade de <b>{_fmt_float(pior_conf['Conformidade'])}%</b> para limite de {int(pior_conf['Limite'])} min."
        })

    if pd.notna(momento_pico):
        insights.append({
            "title": "Maior pressão operacional",
            "text": f"Pico de <b>{_fmt_int(valor_pico)} pacientes simultâneos</b> em <b>{unid_pico}</b> às <b>{momento_pico.strftime('%d/%m %H:%M')}</b>."
        })

    return insights


def build_tabelas_pico(simultaneos_df):
    if simultaneos_df.empty:
        return None, None, None, None

    picos = (
        simultaneos_df.loc[
            simultaneos_df.groupby(["Unidade", "Data"])["PacientesSimultaneos"].idxmax()
        ]
        .reset_index(drop=True)
    )

    tabela_pico_dias = picos.pivot(index="Unidade", columns="Data", values="PacientesSimultaneos")
    tabela_horario_pico = picos.pivot(index="Unidade", columns="Data", values="HoraMin")

    total_por_minuto = simultaneos_df.groupby("Minuto")["PacientesSimultaneos"].sum().reset_index()
    total_por_minuto["Data"] = total_por_minuto["Minuto"].dt.date

    pico_total_por_dia = (
        total_por_minuto.loc[total_por_minuto.groupby("Data")["PacientesSimultaneos"].idxmax()]
        .set_index("Data")["PacientesSimultaneos"]
    )

    return tabela_pico_dias, tabela_horario_pico, None, pico_total_por_dia


def calcular_estatisticas_picos(unidade, tabela_horario_pico, tabela_pico_dias):
    if unidade not in tabela_horario_pico.index:
        return pd.Series({"Cedo": "-", "Tardio": "-", "Mediana": "-", "Média": "-"})

    horarios_str = tabela_horario_pico.loc[unidade].dropna()
    if horarios_str.empty:
        return pd.Series({"Cedo": "-", "Tardio": "-", "Mediana": "-", "Média": "-"})

    horarios_dt = pd.to_datetime(horarios_str, format="%H:%M")
    minutos_list = [h.hour * 60 + h.minute for h in horarios_dt]
    media_min = sum(minutos_list) / len(minutos_list)

    return pd.Series({
        "Cedo": horarios_dt.sort_values().iloc[0].strftime("%H:%M"),
        "Tardio": horarios_dt.sort_values().iloc[-1].strftime("%H:%M"),
        "Mediana": horarios_dt.sort_values().iloc[len(horarios_dt) // 2].strftime("%H:%M"),
        "Média": f"{int(media_min // 60):02d}:{int(media_min % 60):02d}",
    })


def extrato_pico_por_data(data_sel, simultaneos_df, exploded_df):
    data_dt = pd.to_datetime(data_sel).date()

    picos = (
        simultaneos_df[simultaneos_df["Data"] == data_dt]
        .loc[lambda d: d.groupby("Unidade")["PacientesSimultaneos"].idxmax()]
        .reset_index(drop=True)
        [["Unidade", "Minuto", "PacientesSimultaneos"]]
        .rename(columns={"Minuto": "Horário do Pico", "PacientesSimultaneos": "Qtd de Pacientes"})
    )

    if picos.empty:
        return picos

    picos["Horário do Pico_str"] = picos["Horário do Pico"].dt.strftime("%H:%M")

    def contar_etapas(row):
        ev = exploded_df[
            (exploded_df["Unidade"] == row["Unidade"]) &
            (exploded_df["Minuto"] == row["Horário do Pico"])
        ]["Etapa"].value_counts()

        return pd.Series({
            "1.Espera Recepção": ev.get("1.Espera Recepção", 0),
            "2.Recepção": ev.get("2.Recepção", 0),
            "3.Espera Coleta": ev.get("3.Espera Coleta", 0),
            "4.Coleta": ev.get("4.Coleta", 0),
        })

    etapas_cols = picos.apply(contar_etapas, axis=1)
    out = pd.concat([picos[["Unidade", "Horário do Pico_str", "Qtd de Pacientes"]], etapas_cols], axis=1)

    return out.rename(columns={"Horário do Pico_str": "Horário do Pico"}).sort_values("Unidade").reset_index(drop=True)


def calcular_resumo_operadores(df_filtrado, etapa_selecionada):
    tabela = []

    if etapa_selecionada == "2.Recepção":
        limite_etapa = 10
    elif etapa_selecionada == "4.Coleta":
        limite_etapa = 6
    else:
        limite_etapa = None

    for operador, grupo in df_filtrado.groupby("Operador"):
        grupo = grupo.sort_values("Inicio").reset_index(drop=True)
        tempos = (grupo["Fim"] - grupo["Inicio"]).dt.total_seconds() / 60

        gaps = []
        for i in range(1, len(grupo)):
            gap = (grupo.loc[i, "Inicio"] - grupo.loc[i - 1, "Fim"]).total_seconds() / 60
            if gap > 0:
                gaps.append(gap)

        conformidade = (tempos <= limite_etapa).mean() * 100 if limite_etapa is not None else np.nan

        tabela.append({
            "Operador": operador,
            "Pacientes únicos": grupo["ID"].nunique(),
            "Etapas executadas": grupo.shape[0],
            "Hora da Primeira Etapa": grupo["Inicio"].min().strftime("%H:%M"),
            "Hora da Última Etapa": grupo["Fim"].max().strftime("%H:%M"),
            "Tempo Médio (min)": round(tempos.mean(), 1),
            "Conformidade da Etapa (%)": round(conformidade, 1) if pd.notna(conformidade) else np.nan,
            "Qtde de GAPs": len(gaps),
            "Total GAPs (min)": round(sum(gaps), 1) if gaps else 0,
            "GAP Mín (min)": round(min(gaps), 1) if gaps else 0,
            "GAP Máx (min)": round(max(gaps), 1) if gaps else 0,
            "GAP Médio (min)": round(np.mean(gaps), 1) if gaps else 0,
        })

    return pd.DataFrame(tabela)

# =========================================================
# Bloco 10 — Função do gráfico timeline de operadores
# =========================================================
def fig_timeline_operadores(df_tl, unidade, data_sel, etapa_sel):
    if df_tl.empty:
        return None

    df_plot = df_tl.copy().sort_values(["Operador", "Inicio"]).reset_index(drop=True)

    ordem_operadores = (
        df_plot.groupby("Operador")["Inicio"]
        .min()
        .sort_values()
        .index.tolist()
    )

    palette = [
        COLORS["support_mint"],
        COLORS["support_warm"],
        COLORS["support_ice"],
        COLORS["support_blush"],
        COLORS["primary_light"],
        COLORS["warning"],
        COLORS["info"],
        COLORS["primary"],
    ]
    color_map = {op: palette[i % len(palette)] for i, op in enumerate(ordem_operadores)}

    fig = go.Figure()

    for op in ordem_operadores:
        sub = df_plot[df_plot["Operador"] == op].copy()
        if sub.empty:
            continue

        dur_ms = (sub["Fim"] - sub["Inicio"]).dt.total_seconds() * 1000
        dur_min = (sub["Fim"] - sub["Inicio"]).dt.total_seconds() / 60

        labels = [f"{int(round(v))}min" if v >= 2 else "" for v in dur_min]

        fig.add_trace(go.Bar(
            x=dur_ms,
            y=sub["Operador"],
            base=sub["Inicio"],
            orientation="h",
            name=op,
            marker=dict(
                color=color_map[op],
                line=dict(color="rgba(60,60,60,0.55)", width=1)
            ),
            width=0.50,
            text=labels,
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=10, color="rgba(40,40,40,0.88)"),
            customdata=np.stack([
                sub["Inicio"].dt.strftime("%H:%M"),
                sub["Fim"].dt.strftime("%H:%M"),
                dur_min.round(1),
                sub["ID"].astype(str)
            ], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Início: %{customdata[0]}<br>"
                "Fim: %{customdata[1]}<br>"
                "Duração: %{customdata[2]} min<br>"
                "Atendimento: %{customdata[3]}<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        **plot_layout(
            title=(
                f"Timeline de Atividades - Etapa: {etapa_sel}<br>"
                f"Unidade: {unidade} | {pd.to_datetime(data_sel).strftime('%Y-%m-%d')}"
            ),
            height=max(500, len(ordem_operadores) * 160),
            legend=None,
            margin=dict(l=20, r=20, t=75, b=40),
        ),
        barmode="overlay",
        bargap=0.35,
        xaxis=dict(
            title="Horário",
            type="date",
            tickformat="%H:%M",
            showgrid=True,
            gridcolor="rgba(120,120,120,0.22)",
            griddash="dot",
            tickangle=-45,
        ),
        yaxis=dict(
            title="Operadores",
            categoryorder="array",
            categoryarray=ordem_operadores[::-1],
            showgrid=True,
            gridcolor="rgba(120,120,120,0.10)",
        ),
    )

    return fig

# =========================================================
# Bloco 11 — Sidebar inicial
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding-top:0.15rem;">
            <div style="font-size:1.15rem;font-weight:800;">Fluxo de Atendimento</div>
            <div style="font-size:0.83rem;opacity:0.88;">Análise de picos e gargalos operacionais</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.85rem'></div>", unsafe_allow_html=True)
    st.markdown("**Fonte de dados**")

    if "uploaded_fluxo" not in st.session_state:
        st.session_state["uploaded_fluxo"] = None

    if st.session_state["uploaded_fluxo"] is None:
        uploaded = st.file_uploader(
            "Envie a planilha de fluxo",
            type=["xlsx", "xls", "csv"],
            help="Use a mesma estrutura do arquivo exportado do seu processo.",
            key="upload_fluxo_inicial",
        )

        if uploaded is not None:
            st.session_state["uploaded_fluxo"] = uploaded
            st.rerun()

    else:
        uploaded = st.session_state["uploaded_fluxo"]
        file_ext = Path(uploaded.name).suffix.upper().replace(".", "")

        st.markdown(
            f"""
            <div class="sidebar-file-card">
                <div class="sidebar-file-icon">📄</div>
                <div class="sidebar-file-content">
                    <div class="sidebar-file-title">Arquivo carregado</div>
                    <div class="sidebar-file-name">{uploaded.name}</div>
                    <div class="sidebar-file-meta">
                        <span class="sidebar-file-chip">✅ {file_ext}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Trocar arquivo", expanded=False):
            novo_arquivo = st.file_uploader(
                "Substituir arquivo",
                type=["xlsx", "xls", "csv"],
                label_visibility="collapsed",
                key="upload_fluxo_substituir",
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if novo_arquivo is not None:
                    st.session_state["uploaded_fluxo"] = novo_arquivo
                    st.rerun()
            with col_b:
                if st.button("Remover", use_container_width=True):
                    st.session_state["uploaded_fluxo"] = None
                    st.rerun()
    
# =========================================================
# Bloco 12 — Hero inicial e stop sem arquivo
# =========================================================
if uploaded is None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">📊 Dashboard de Análise de Pico de Atendimentos</div>
            <div class="hero-sub">
                Sistema de monitoramento operacional — volume, capacidade, gargalos, SLA e produtividade.
            </div>
            <div class="hero-badges">
                <span class="badge">📁 Envie a planilha na barra lateral</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Envie a planilha na barra lateral para carregar o dashboard.")
    st.stop()

# =========================================================
# Bloco 13 — Carga e preprocessamento
# =========================================================
try:
    df_raw = load_data(uploaded)
    df_transformado, qualidade_base = transformar_nova_base(df_raw)
    df = preprocess_data(df_transformado)
except Exception as e:
    st.error(f"Não foi possível processar a base: {e}")
    st.stop()

# =========================================================
# Bloco 14 — Sidebar pós-carga
# =========================================================
with st.sidebar:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section-title'>Filtros</div>", unsafe_allow_html=True)

    min_date = pd.to_datetime(df["Inicio"]).min().date()
    max_date = pd.to_datetime(df["Inicio"]).max().date()

    col_dt1, col_dt2 = st.columns(2)

    with col_dt1:
        periodo_inicio = st.date_input(
            "Início",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key="dt_ini",
        )

    with col_dt2:
        periodo_fim = st.date_input(
            "Fim",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key="dt_fim",
        )

    unidades = st.multiselect(
        "Unidade",
        sorted(df["Unidade"].dropna().unique().tolist()),
        placeholder="Selecionar Unidade",
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    with st.container(border=False):
        st.markdown("### Base carregada")
        st.caption(f"{min_date:%d/%m/%Y} até {max_date:%d/%m/%Y}")

        st.markdown("**Qualidade da base**")

        info_rows = [
            ("Linhas origem", _fmt_int(qualidade_base["total_linhas"])),
            ("Atendimentos válidos", _fmt_int(qualidade_base["atendimentos_validos"])),
            ("Atendimentos descartados", _fmt_int(qualidade_base["atendimentos_descartados"])),
            ("Tipos inválidos", _fmt_int(qualidade_base["tipos_invalidos"])),
            ("Etapas geradas", _fmt_int(qualidade_base["etapas_geradas"])),
        ]

        for label, value in info_rows:
            c1, c2 = st.columns([2.4, 1])
            with c1:
                st.write(label)
            with c2:
                st.write(f"**{value}**")

# =========================================================
# Bloco 15 — Aplicar filtros e preparar base analítica
# =========================================================

df_f = apply_filters(df, unidades, [], [], [], (periodo_inicio, periodo_fim))

if df_f.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

exploded_f, simultaneos_f = build_minute_level(df_f)

# =========================================================
# Bloco 16 — Hero final, caption, KPIs e insights
# =========================================================

kpis = make_kpis(df_f, simultaneos_f)

periodo_ini_real = pd.to_datetime(df_f["Inicio"]).min()
periodo_fim_real = pd.to_datetime(df_f["Inicio"]).max()
titulo_unidade = ", ".join(unidades) if unidades else "Todas as unidades"

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">📊 Dashboard de Análise de Pico de Atendimentos</div>
        <div class="hero-sub">
            Painel de monitoramento operacional — volume, capacidade, gargalos, SLA e produtividade por unidade, etapa e operador.
        </div>
        <div class="hero-badges">
            <span class="badge">🏢 Unidade: {titulo_unidade}</span>
            <span class="badge">📅 Período: {periodo_ini_real:%d/%m/%Y} a {periodo_fim_real:%d/%m/%Y}</span>
            <span class="badge">🎟️ {_fmt_int(kpis['atendimentos'])} atendimentos</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

caption_box(
    "<b>Leitura executiva:</b> o painel identifica os momentos de maior pressão operacional, "
    "gargalos por etapa do fluxo e oportunidades de melhoria por unidade e operador."
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(kpi_card(
        "Registros",
        _fmt_int(kpis["registros"]),
        f"{_fmt_int(kpis['atendimentos'])} atendimentos únicos",
        COLORS["deep"],
        icon="📋",
        fill=1,
        accent_2=COLORS["primary"],
    ), unsafe_allow_html=True)

with k2:
    st.markdown(kpi_card(
        "Operadores",
        _fmt_int(kpis["operadores"]),
        f"{_fmt_int(kpis['unidades'])} unidades no período",
        COLORS["info"],
        icon="👥",
        fill=min(kpis["operadores"] / 50, 1),
        accent_2=COLORS["support_ice"],
    ), unsafe_allow_html=True)

with k3:
    st.markdown(kpi_card(
        "Tempo médio",
        _fmt_min(kpis["duracao_media"]) if pd.notna(kpis["duracao_media"]) else "—",
        "Duração média por etapa",
        COLORS["alert"],
        icon="⏱️",
        fill=min(kpis["duracao_media"] / 20, 1) if pd.notna(kpis["duracao_media"]) else 0,
        accent_2=COLORS["warning"],
    ), unsafe_allow_html=True)

_pico_sub = (
    f"Pico na unidade: {', '.join(unidades)}" if len(unidades) == 1
    else "Total simultâneo — soma de todas as unidades"
)
with k4:
    st.markdown(kpi_card(
        "Pico simultâneo",
        _fmt_int(kpis["pico_max"]),
        _pico_sub,
        COLORS["danger"],
        icon="🔝",
        fill=min(kpis["pico_max"] / 50, 1),
        accent_2=COLORS["danger_dark"],
    ), unsafe_allow_html=True)

with k5:
    hora_pico_str = kpis["hora_pico"].strftime("%d/%m %H:%M") if pd.notna(kpis["hora_pico"]) else "—"
    st.markdown(kpi_card(
        "Horário do pico",
        hora_pico_str,
        _pico_sub,
        COLORS["danger_dark"],
        icon="🕐",
        fill=0.8,
        accent_2=COLORS["alert"],
    ), unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

insights = make_insights(df_f, simultaneos_f)
insight_cols = st.columns(len(insights)) if insights else []

for col, ins in zip(insight_cols, insights):
    with col:
        insight_card(ins["title"], ins["text"])

def preparar_analise_capacidade(df_base, funcao_sel="Todas", capacidade_individual_hora=5):
    """
    Prepara a base da aba Capacidade considerando apenas etapas de atendimento real:
    - 2.Recepção
    - 4.Coleta

    Capacidade estimada por hora:
    capacidade = operadores equivalentes ativos na hora * capacidade_individual_hora

    Onde operadores equivalentes ativos na hora = média, por minuto, do número de operadores
    simultaneamente em atendimento naquela hora.
    """
    df_cap = df_base.copy()

    etapas_validas = ["2.Recepção", "4.Coleta"]
    df_cap = df_cap[df_cap["Etapa"].isin(etapas_validas)].copy()
    df_cap = df_cap[df_cap["Operador"].notna()].copy()

    if funcao_sel != "Todas":
        df_cap = df_cap[df_cap["FuncaoOperador"] == funcao_sel].copy()

    if df_cap.empty:
        return {
            "df_cap": df_cap,
            "exploded_cap": pd.DataFrame(),
            "simult_cap": pd.DataFrame(),
            "resumo_hora": pd.DataFrame(),
            "resumo_data_hora": pd.DataFrame(),
        }

    exploded_cap, simult_cap = build_minute_level(df_cap)

    # Demanda por hora = quantidade de atendimentos iniciados naquela hora
    demanda_hora = (
        df_cap.groupby(["Data", "Hora"])
        .agg(
            Atendimentos=("ID", "size"),
            PacientesUnicos=("ID", "nunique"),
            DuracaoMedia=("DuracaoMin", "mean"),
        )
        .reset_index()
    )

    # Operadores ativos por minuto
    operadores_minuto = (
        exploded_cap.groupby(["Data", "Hora", "Minuto"])["Operador"]
        .nunique()
        .reset_index(name="OperadoresAtivosMin")
    )

    # Operadores equivalentes por hora = média dos operadores ativos por minuto
    operadores_hora = (
        operadores_minuto.groupby(["Data", "Hora"])
        .agg(
            OperadoresEquiv=("OperadoresAtivosMin", "mean"),
            PicoOperadores=("OperadoresAtivosMin", "max"),
        )
        .reset_index()
    )

    # Pacientes simultâneos por hora = média por minuto
    simult_hora = (
        simult_cap.groupby(["Data", "Hora"])
        .agg(
            PacientesSimultaneosMed=("PacientesSimultaneos", "mean"),
            PacientesSimultaneosPico=("PacientesSimultaneos", "max"),
        )
        .reset_index()
    )

    resumo_data_hora = (
        demanda_hora
        .merge(operadores_hora, on=["Data", "Hora"], how="outer")
        .merge(simult_hora, on=["Data", "Hora"], how="outer")
        .fillna(0)
        .sort_values(["Data", "Hora"])
        .reset_index(drop=True)
    )

    resumo_data_hora["CapacidadeHora"] = (
        resumo_data_hora["OperadoresEquiv"] * capacidade_individual_hora
    )

    resumo_data_hora["PressaoPct"] = np.where(
        resumo_data_hora["CapacidadeHora"] > 0,
        resumo_data_hora["Atendimentos"] / resumo_data_hora["CapacidadeHora"] * 100,
        np.nan,
    )

    resumo_hora = (
        resumo_data_hora.groupby("Hora")
        .agg(
            Atendimentos=("Atendimentos", "mean"),
            PacientesUnicos=("PacientesUnicos", "mean"),
            DuracaoMedia=("DuracaoMedia", "mean"),
            OperadoresEquiv=("OperadoresEquiv", "mean"),
            PicoOperadores=("PicoOperadores", "mean"),
            CapacidadeHora=("CapacidadeHora", "mean"),
            PressaoPct=("PressaoPct", "mean"),
            PacientesSimultaneosMed=("PacientesSimultaneosMed", "mean"),
            PacientesSimultaneosPico=("PacientesSimultaneosPico", "mean"),
        )
        .reset_index()
        .sort_values("Hora")
    )

    return {
        "df_cap": df_cap,
        "exploded_cap": exploded_cap,
        "simult_cap": simult_cap,
        "resumo_hora": resumo_hora,
        "resumo_data_hora": resumo_data_hora,
    }

def gerar_video_fluxo_por_minuto(
    df_exploded: pd.DataFrame,
    unidade_desejada: str,
    data_desejada,
    fps: int = 4,
):
    """
    Gera um vídeo MP4 com a evolução minuto a minuto do fluxo de pacientes
    por etapa para uma unidade e uma data específicas.

    Retorna:
        bytes_video, nome_arquivo
    """
    if df_exploded is None or df_exploded.empty:
        raise ValueError("A base minuto a minuto está vazia.")

    colunas_necessarias = ["Unidade", "Minuto", "Etapa", "ID"]
    faltantes = [c for c in colunas_necessarias if c not in df_exploded.columns]
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes para gerar vídeo: {faltantes}")

    data_ref = pd.to_datetime(data_desejada).date()

    df_filtrado = df_exploded[
        (df_exploded["Unidade"] == unidade_desejada) &
        (df_exploded["Minuto"].notna()) &
        (df_exploded["Minuto"].dt.date == data_ref)
    ].copy()

    if df_filtrado.empty:
        raise ValueError("Nenhum dado encontrado para a combinação de unidade e data selecionadas.")

    dados_anim = (
        df_filtrado.groupby(["Minuto", "Etapa"])["ID"]
        .nunique()
        .reset_index(name="Qtd")
    )

    tempos = sorted(dados_anim["Minuto"].unique())
    etapas = ["1.Espera Recepção", "2.Recepção", "3.Espera Coleta", "4.Coleta"]

    cores = {
        "1.Espera Recepção": "#F4E2B1",
        "2.Recepção": "#00995D",
        "3.Espera Coleta": "#F47920",
        "4.Coleta": "#C1D0B9",
    }

    max_y = dados_anim["Qtd"].max() if not dados_anim.empty else 1
    max_y = max(max_y + 2, 5)

    temp_dir = tempfile.mkdtemp(prefix="frames_fluxo_")
    frames = []

    try:
        for i, tempo in enumerate(tempos):
            df_minuto = dados_anim[dados_anim["Minuto"] == tempo]
            valores = [df_minuto[df_minuto["Etapa"] == e]["Qtd"].sum() for e in etapas]

            fig, ax = plt.subplots(figsize=(10, 5.8))
            bars = ax.bar(
                etapas,
                valores,
                color=[cores[e] for e in etapas],
                edgecolor="white",
                linewidth=1.2
            )

            ax.set_title(
                f"{unidade_desejada} · {pd.to_datetime(tempo).strftime('%d/%m/%Y %H:%M')}",
                fontsize=15,
                fontweight="bold",
                pad=16,
            )
            ax.set_ylabel("Pacientes no minuto")
            ax.set_xlabel("Etapas do fluxo")
            ax.set_ylim(0, max_y)
            ax.grid(axis="y", linestyle="--", alpha=0.25)

            for bar, val in zip(bars, valores):
                if val > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        val + 0.12,
                        str(int(val)),
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                    )

            plt.xticks(rotation=18, ha="right")
            plt.tight_layout()

            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            plt.savefig(frame_path, dpi=110, bbox_inches="tight")
            plt.close(fig)

            frames.append(imageio.imread(frame_path))

        if not frames:
            raise ValueError("Nenhum frame foi gerado para a animação.")

        nome_arquivo = (
            f"fluxo_{unidade_desejada.replace(' ', '_').replace('/', '_')}_{str(data_ref)}.mp4"
        )
        video_path = os.path.join(temp_dir, nome_arquivo)
        imageio.mimsave(video_path, frames, fps=fps)

        with open(video_path, "rb") as f:
            video_bytes = f.read()

        return video_bytes, nome_arquivo

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# =========================================================
# Bloco 17 — Tabs
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Resumo",
    "🔥 Picos",
    "🌡️ Capacidade",
    "⏱️ SLA",
    "👥 Operadores",
    "🎬 Animação",
])

# =========================================================
# Bloco 18 — Tab 1: Resumo Executivo
# =========================================================

with tab1:
    section_header("Volume e composição do fluxo de atendimento")

    a, b = st.columns([1.2, 1])

    with a:
        vol_dia = df_f.groupby("Data")["ID"].nunique().reset_index(name="Atendimentos")

        fig = go.Figure(go.Scatter(
            x=vol_dia["Data"],
            y=vol_dia["Atendimentos"],
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=6, color=COLORS["deep"]),
            fill="tozeroy",
            fillcolor="rgba(0,153,93,0.07)",
            hovertemplate="<b>%{x}</b><br>%{y} atendimentos<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Volume diário de atendimentos"),
            xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
            yaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

    with b:
        unid = (
            df_f.groupby("Unidade")["ID"].nunique()
            .sort_values(ascending=False)
            .reset_index(name="Atendimentos")
        )

        fig = go.Figure(go.Bar(
            y=unid["Unidade"],
            x=unid["Atendimentos"],
            orientation="h",
            marker_color=COLORS["primary"],
            text=unid["Atendimentos"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} atendimentos<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Unidades por volume"),
            xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
            yaxis=dict(title=None, showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    c, d = st.columns([1, 1.2])

    with c:
        etapa = df_f.groupby("Etapa", as_index=False)["DuracaoMin"].mean().sort_values("DuracaoMin")
        cores_etapa = [
            COLORS["primary"] if v <= 6 else COLORS["alert"] if v <= 10 else COLORS["danger"]
            for v in etapa["DuracaoMin"]
        ]

        fig = go.Figure(go.Bar(
            y=etapa["Etapa"],
            x=etapa["DuracaoMin"],
            orientation="h",
            marker_color=cores_etapa,
            text=[f"{v:.1f} min" for v in etapa["DuracaoMin"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Tempo médio: %{x:.1f} min<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Tempo médio por etapa"),
            xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
            yaxis=dict(title=None, showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with d:
        tipo = df_f.groupby("TipoAtendimento")["ID"].nunique().reset_index(name="Atendimentos")

        fig = go.Figure(go.Pie(
            labels=tipo["TipoAtendimento"],
            values=tipo["Atendimentos"],
            hole=0.55,
            marker=dict(colors=[COLORS["primary"], COLORS["primary_light"], COLORS["support_ice"], COLORS["alert"]]),
            textinfo="percent",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>%{value} atendimentos (%{percent})<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout(
                "Tipo de Atendimento",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.20,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12),
                ),
                margin=dict(l=8, r=8, t=50, b=60),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# Bloco 19 — Tab 2: Picos de Atendimento
# =========================================================

with tab2:
    section_header("Análise de picos de atendimento por unidade")

    tabela_pico_dias, tabela_horario_pico, _, pico_total_por_dia = build_tabelas_pico(simultaneos_f)

    if tabela_pico_dias is None:
        st.info("Dados insuficientes para análise de picos com os filtros atuais.")
    else:
        cols_str = [str(c) for c in tabela_pico_dias.columns]

        # ── Margem esquerda comum para alinhar os dois heatmaps ──
        _n_unidades  = len(tabela_pico_dias)
        _altura_unid = max(300, _n_unidades * 38 + 80)
        # largura do maior label de unidade (px aprox)
        _max_label   = max((len(str(y)) for y in tabela_pico_dias.index), default=10)
        _margem_y    = max(120, _max_label * 7)

        fig_heat_unid = go.Figure(go.Heatmap(
            z=tabela_pico_dias.values,
            x=cols_str,
            y=list(tabela_pico_dias.index),
            colorscale=[
                [0.00, COLORS["surface_soft"]],
                [0.30, COLORS["support_mint"]],
                [0.60, COLORS["primary_light"]],
                [0.80, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            text=[[f"{int(v)}" if pd.notna(v) else "—" for v in row] for row in tabela_pico_dias.values],
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorbar=dict(title="Pico", x=1.01),
            hovertemplate="<b>%{y}</b><br>Data: %{x}<br>Pico: %{z:.0f} pacientes<extra></extra>",
        ))
        fig_heat_unid.update_layout(
            **plot_layout(
                "Pico de pacientes simultâneos por unidade e dia",
                height=_altura_unid,
                margin=dict(l=_margem_y, r=60, t=50, b=10),
            ),
            xaxis=dict(title=None, tickangle=-45, showticklabels=False),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig_heat_unid, use_container_width=True)

        total_vals = [[float(pico_total_por_dia.get(c, 0)) for c in tabela_pico_dias.columns]]

        fig_heat_total = go.Figure(go.Heatmap(
            z=total_vals,
            x=cols_str,
            y=["Total"],
            colorscale=[
                [0.00, COLORS["surface_soft"]],
                [0.50, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            text=[[f"{int(v)}" for v in total_vals[0]]],
            texttemplate="%{text}",
            textfont=dict(size=11, color="white"),
            showscale=False,
            hovertemplate="Data: %{x}<br>Total: %{z:.0f} pacientes<extra></extra>",
        ))
        fig_heat_total.update_layout(
            **plot_layout(
                "Total de pacientes simultâneos por dia",
                height=130,
                margin=dict(l=_margem_y, r=60, t=40, b=50),
            ),
            xaxis=dict(title=None, tickangle=-45),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig_heat_total, use_container_width=True)

        section_header("Horário de pico por unidade — estatísticas")

        estat = tabela_horario_pico.index.to_series().apply(
            lambda u: calcular_estatisticas_picos(u, tabela_horario_pico, tabela_pico_dias)
        )

        # Colunas de data → dd/mm
        cols_ddmm = {
            c: pd.to_datetime(c).strftime("%d/%m")
            for c in tabela_horario_pico.columns
        }
        tabela_exib = tabela_horario_pico.rename(columns=cols_ddmm).copy()
        tabela_exib = pd.concat([tabela_exib, estat], axis=1).reset_index()
        tabela_exib.columns.name = None
        tabela_exib = tabela_exib.rename(columns={"Unidade": "Unidade"})

        # Highlight: horário do dia com maior pico por unidade
        def _highlight_pico(row):
            unidade = row.iloc[0]
            styles  = [""] * len(row)
            if unidade not in tabela_pico_dias.index:
                return styles
            picos_unid = tabela_pico_dias.loc[unidade]
            if picos_unid.dropna().empty:
                return styles
            dia_max_orig  = picos_unid.idxmax()                       # date original
            dia_max_ddmm  = pd.to_datetime(dia_max_orig).strftime("%d/%m")  # formato exibido
            for i, col in enumerate(row.index):
                if col == dia_max_ddmm:
                    styles[i] = (
                        f"background-color: {COLORS['danger']}28;"
                        f"color: {COLORS['danger_dark']};"
                        "font-weight: 800;"
                        "border-radius: 4px;"
                    )
            return styles

        # column_config: largura compacta para colunas de data e estatísticas
        _col_cfg = {c: st.column_config.TextColumn(c, width="small")
                    for c in tabela_exib.columns if c != "Unidade"}
        _col_cfg["Unidade"] = st.column_config.TextColumn("Unidade", width="medium")

        st.dataframe(
            tabela_exib.style.apply(_highlight_pico, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config=_col_cfg,
        )

        section_header("Extrato de pico por unidade — por data")

        datas_disponiveis = sorted(simultaneos_f["Data"].unique())
        _col_sel, _ = st.columns([1, 3])
        with _col_sel:
            data_sel = st.selectbox(
                "Data:",
                options=datas_disponiveis,
                format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
                key="extrato_data",
                label_visibility="collapsed",
            )

        extrato = extrato_pico_por_data(data_sel, simultaneos_f, exploded_f)

        if extrato.empty:
            st.warning(f"Nenhum dado para {pd.to_datetime(data_sel).strftime('%d/%m/%Y')}.")
        else:
            # Centralizar colunas numéricas e de horário
            _ext_cfg = {
                "Unidade":           st.column_config.TextColumn("Unidade",           width="medium"),
                "Horário do Pico":   st.column_config.TextColumn("Horário do Pico",   width="small"),
                "Qtd de Pacientes":  st.column_config.NumberColumn("Qtd de Pacientes", width="small", format="%d"),
                "1.Espera Recepção": st.column_config.NumberColumn("Espera Recepção",  width="small", format="%d"),
                "2.Recepção":        st.column_config.NumberColumn("Recepção",         width="small", format="%d"),
                "3.Espera Coleta":   st.column_config.NumberColumn("Espera Coleta",    width="small", format="%d"),
                "4.Coleta":          st.column_config.NumberColumn("Coleta",           width="small", format="%d"),
            }
            st.dataframe(
                extrato,
                use_container_width=True,
                hide_index=True,
                column_config=_ext_cfg,
            )
            info_note("Distribuição dos pacientes simultâneos pelas etapas do fluxo no momento de pico de cada unidade.")

# =========================================================
# Bloco 20 — Tab 3: Capacidade & Heatmaps
# =========================================================

with tab3:
    section_header("Capacidade operacional e pressão por função")

    col_ctrl1, col_ctrl2 = st.columns([1, 1])

    with col_ctrl1:
        funcao_cap = st.radio(
            "Função visualizada",
            options=["Todas", "Recepção", "Coleta"],
            horizontal=True,
            key="cap_funcao",
        )

    with col_ctrl2:
        capacidade_individual_hora = st.select_slider(
            "Capacidade individual por profissional (pacientes/hora)",
            options=[5, 6, 7, 8, 9, 10],
            value=5,
            key="cap_pph",
        )

    analise_cap = preparar_analise_capacidade(
        df_f,
        funcao_sel=funcao_cap,
        capacidade_individual_hora=capacidade_individual_hora,
    )

    df_cap = analise_cap["df_cap"]
    resumo_hora = analise_cap["resumo_hora"]
    resumo_data_hora = analise_cap["resumo_data_hora"]

    if df_cap.empty or resumo_hora.empty:
        st.info("Não há dados suficientes para análise de capacidade com os filtros selecionados.")
    else:
        info_note(
            f"<b>Regra adotada:</b> somente etapas de atendimento real foram consideradas "
            f"(<b>2.Recepção</b> e <b>4.Coleta</b>). "
            f"A capacidade estimada usa <b>{capacidade_individual_hora} pacientes/hora</b> por profissional ativo."
        )

        # =========================
        # KPIs da aba
        # =========================
        pico_pressao = resumo_data_hora["PressaoPct"].max()
        hora_pico_pressao = resumo_data_hora.loc[
            resumo_data_hora["PressaoPct"].idxmax(), ["Data", "Hora"]
        ] if resumo_data_hora["PressaoPct"].notna().any() else None

        cap_cols = st.columns(4)

        with cap_cols[0]:
            st.markdown(kpi_card(
                "Atendimentos/hora",
                _fmt_float(resumo_hora["Atendimentos"].mean(), 1),
                "Média de atendimentos iniciados por hora",
                COLORS["primary"],
                icon="📈",
                fill=min(resumo_hora["Atendimentos"].mean() / 30, 1),
                accent_2=COLORS["primary_light"],
            ), unsafe_allow_html=True)

        with cap_cols[1]:
            st.markdown(kpi_card(
                "Capacidade/hora",
                _fmt_float(resumo_hora["CapacidadeHora"].mean(), 1),
                "Capacidade média estimada por hora",
                COLORS["info"],
                icon="🧩",
                fill=min(resumo_hora["CapacidadeHora"].mean() / 30, 1),
                accent_2=COLORS["support_ice"],
            ), unsafe_allow_html=True)

        with cap_cols[2]:
            st.markdown(kpi_card(
                "Pressão média",
                f"{_fmt_float(resumo_hora['PressaoPct'].mean(), 1)}%",
                "Demanda ÷ capacidade estimada",
                COLORS["alert"],
                icon="⚠️",
                fill=min((resumo_hora["PressaoPct"].mean() or 0) / 100, 1),
                accent_2=COLORS["warning"],
            ), unsafe_allow_html=True)

        with cap_cols[3]:
            hora_pico_txt = (
                f"{pd.to_datetime(hora_pico_pressao['Data']).strftime('%d/%m')} · {int(hora_pico_pressao['Hora']):02d}h"
                if hora_pico_pressao is not None else "—"
            )
            st.markdown(kpi_card(
                "Pico de pressão",
                f"{_fmt_float(pico_pressao, 1)}%" if pd.notna(pico_pressao) else "—",
                hora_pico_txt,
                COLORS["danger"],
                icon="🔥",
                fill=min((pico_pressao or 0) / 100, 1) if pd.notna(pico_pressao) else 0,
                accent_2=COLORS["danger_dark"],
            ), unsafe_allow_html=True)

        # =========================
        # Gráfico 1 — Demanda x Capacidade
        # =========================
        section_header("Demanda versus capacidade por hora")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=resumo_hora["Hora"],
            y=resumo_hora["Atendimentos"],
            name="Demanda (atendimentos/hora)",
            marker_color=COLORS["primary"],
            text=[f"{v:.1f}" for v in resumo_hora["Atendimentos"]],
            textposition="outside",
            hovertemplate="<b>%{x}h</b><br>Demanda: %{y:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=resumo_hora["Hora"],
            y=resumo_hora["CapacidadeHora"],
            mode="lines+markers",
            name="Capacidade estimada/hora",
            line=dict(color=COLORS["danger_dark"], width=3),
            marker=dict(size=8, color=COLORS["danger_dark"]),
            hovertemplate="<b>%{x}h</b><br>Capacidade: %{y:.1f}<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Demanda realizada × capacidade estimada"),
            xaxis=dict(title="Hora", dtick=1, showgrid=False),
            yaxis=dict(title="Pacientes por hora", showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # Gráfico 2 — Pressão operacional
        # =========================
        section_header("Pressão operacional por hora")

        cores_pressao = [
            COLORS["primary"] if v < 70 else COLORS["alert"] if v < 100 else COLORS["danger"]
            for v in resumo_hora["PressaoPct"].fillna(0)
        ]

        fig = go.Figure(go.Bar(
            x=resumo_hora["Hora"],
            y=resumo_hora["PressaoPct"],
            marker_color=cores_pressao,
            text=[f"{v:.0f}%" if pd.notna(v) else "—" for v in resumo_hora["PressaoPct"]],
            textposition="outside",
            hovertemplate="<b>%{x}h</b><br>Pressão: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=70, line_dash="dot", line_color=COLORS["alert"], opacity=0.8)
        fig.add_hline(y=100, line_dash="dot", line_color=COLORS["danger"], opacity=0.8)
        fig.update_layout(
            **plot_layout("Pressão operacional (demanda ÷ capacidade)"),
            xaxis=dict(title="Hora", dtick=1, showgrid=False),
            yaxis=dict(title="%", showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # Gráfico 3 — Pacientes em atendimento simultâneo
        # =========================
        section_header("Pacientes em atendimento simultâneo")

        fig = go.Figure(go.Bar(
            x=resumo_hora["Hora"],
            y=resumo_hora["PacientesSimultaneosMed"],
            marker_color=[
                COLORS["primary"] if v < resumo_hora["PacientesSimultaneosMed"].quantile(0.75)
                else COLORS["alert"] if v < resumo_hora["PacientesSimultaneosMed"].max()
                else COLORS["danger"]
                for v in resumo_hora["PacientesSimultaneosMed"]
            ],
            text=[f"{v:.1f}" for v in resumo_hora["PacientesSimultaneosMed"]],
            textposition="outside",
            hovertemplate="<b>%{x}h</b><br>Média simultânea: %{y:.1f}<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Média de pacientes em atendimento simultâneo por hora"),
            xaxis=dict(title="Hora", dtick=1, showgrid=False),
            yaxis=dict(title="Pacientes simultâneos", showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # Gráfico 4 — Heatmap de pressão por dia e hora
        # =========================
        section_header("Heatmap de pressão operacional por dia e hora")

        heat_cap = resumo_data_hora.copy()
        heat_cap["DiaSemanaLabel"] = pd.to_datetime(heat_cap["Data"]).dt.day_name().map(MAPA_DIAS_PT)
        ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        heat_cap["DiaSemanaLabel"] = pd.Categorical(
            heat_cap["DiaSemanaLabel"],
            categories=ordem,
            ordered=True
        )

        heat_pivot = (
            heat_cap.groupby(["DiaSemanaLabel", "Hora"])["PressaoPct"]
            .mean()
            .reset_index()
            .pivot(index="DiaSemanaLabel", columns="Hora", values="PressaoPct")
            .fillna(0)
        )

        fig = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=[f"{h:02d}h" for h in heat_pivot.columns],
            y=list(heat_pivot.index),
            colorscale=[
                [0.00, COLORS["surface_soft"]],
                [0.40, COLORS["support_mint"]],
                [0.70, COLORS["primary_light"]],
                [0.85, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            zmin=0,
            zmax=max(100, heat_pivot.values.max()),
            text=[[f"{v:.0f}%" if v > 0 else "" for v in row] for row in heat_pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(title="Pressão %"),
            hovertemplate="%{y} · %{x}<br>Pressão média: %{z:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Pressão média por dia da semana e hora"),
            xaxis=dict(title=None),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # Tabela de apoio
        # =========================
        section_header("Tabela resumo por hora")

        tabela_cap = resumo_hora.copy()
        tabela_cap = tabela_cap.rename(columns={
            "Hora": "Hora",
            "Atendimentos": "Demanda/h",
            "CapacidadeHora": "Capacidade/h",
            "PressaoPct": "Pressão %",
            "OperadoresEquiv": "Operadores equivalentes",
            "PacientesSimultaneosMed": "Simultâneos médios",
            "PacientesSimultaneosPico": "Pico simultâneo",
            "DuracaoMedia": "Duração média (min)",
        })

        for col in ["Demanda/h", "Capacidade/h", "Pressão %", "Operadores equivalentes", "Simultâneos médios", "Pico simultâneo", "Duração média (min)"]:
            if col in tabela_cap.columns:
                tabela_cap[col] = tabela_cap[col].round(1)

        st.dataframe(
            tabela_cap,
            use_container_width=True,
            hide_index=True,
        )

        info_note(
            "<b>Interpretação:</b> pressão abaixo de <b>70%</b> indica folga operacional; "
            "entre <b>70% e 100%</b> indica atenção; "
            "acima de <b>100%</b> sugere demanda acima da capacidade estimada para a função selecionada."
        )

# =========================================================
# Bloco 21 — Tab 4: Etapas & SLA
# =========================================================

with tab4:
    section_header("Conformidade e análise de SLA por etapa")

    slas = []
    for etapa_nome, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa_nome]
        if base.empty:
            continue

        slas.append({
            "Etapa": etapa_nome,
            "SLA (min)": limite,
            "Tempo médio": base["DuracaoMin"].mean(),
            "Conformidade %": (base["DuracaoMin"] <= limite).mean() * 100,
            "P95 (min)": base["DuracaoMin"].quantile(0.95),
        })

    sla_df = pd.DataFrame(slas)

    a, b = st.columns([1, 1])

    with a:
        if not sla_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sla_df["Etapa"],
                y=sla_df["Tempo médio"],
                name="Tempo médio",
                marker_color=COLORS["primary"],
                text=[f"{v:.1f}" for v in sla_df["Tempo médio"]],
                textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=sla_df["Etapa"],
                y=sla_df["SLA (min)"],
                mode="lines+markers",
                name="Limite SLA",
                line=dict(color=COLORS["danger"], dash="dot", width=2),
                marker=dict(size=8, color=COLORS["danger"]),
            ))
            fig.update_layout(
                **plot_layout("Tempo médio × limite de SLA por etapa"),
                xaxis=dict(title=None, showgrid=False),
                yaxis=dict(title="Minutos", showgrid=True, gridcolor=COLORS["grid"]),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de SLA.")

    with b:
        if not sla_df.empty:
            sla_ord = sla_df.sort_values("Conformidade %").copy()
            cores_conf = [
                COLORS["primary"] if v >= 85 else COLORS["alert"] if v >= 70 else COLORS["danger"]
                for v in sla_ord["Conformidade %"]
            ]

            fig = go.Figure(go.Bar(
                y=sla_ord["Etapa"],
                x=sla_ord["Conformidade %"],
                orientation="h",
                marker_color=cores_conf,
                text=[f"{v:.1f}%" for v in sla_ord["Conformidade %"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Conformidade: %{x:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                **plot_layout("Conformidade por etapa"),
                xaxis=dict(title=None, range=[0, 110], ticksuffix="%", showgrid=True, gridcolor=COLORS["grid"]),
                yaxis=dict(title=None, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

    c, d = st.columns([1, 1])

    with c:
        fig = go.Figure()

        for i, etapa_nome in enumerate(df_f["Etapa"].dropna().unique()):
            sub_vals = df_f[df_f["Etapa"] == etapa_nome]["DuracaoMin"]
            fig.add_trace(go.Box(
                y=sub_vals,
                name=etapa_nome,
                marker_color=[COLORS["primary"], COLORS["info"], COLORS["alert"], COLORS["danger"]][i % 4],
                boxmean=True,
            ))

        fig.update_layout(
            **plot_layout("Distribuição de duração por etapa"),
            xaxis=dict(title=None, showgrid=False),
            yaxis=dict(title="Minutos", showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

    with d:
        serv = (
            df_f.groupby("Servico")
            .agg(
                TempoMedio=("DuracaoMin", "mean"),
                Volume=("ID", "nunique"),
            )
            .query("Volume >= 20")
            .sort_values("TempoMedio", ascending=False)
            .reset_index()
        )

        fig = go.Figure(go.Bar(
            y=serv["Servico"],
            x=serv["TempoMedio"],
            orientation="h",
            marker_color=COLORS["alert"],
            text=[f"{v:.1f} min" for v in serv["TempoMedio"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Tempo médio: %{x:.1f} min<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Serviços com maior tempo médio"),
            xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
            yaxis=dict(title=None, showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    if not sla_df.empty:
        section_header("Tabela de SLA por etapa")

        sla_exib = sla_df.copy()
        sla_exib["Tempo médio"] = sla_exib["Tempo médio"].round(1)
        sla_exib["Conformidade %"] = sla_exib["Conformidade %"].round(1)
        sla_exib["P95 (min)"] = sla_exib["P95 (min)"].round(1)

        st.dataframe(
            sla_exib,
            use_container_width=True,
            hide_index=True,
        )

        info_note(
            "<b>SLA:</b> limite de tempo aceitável por etapa. "
            "<b>P95:</b> 95% dos atendimentos estão abaixo desse tempo. "
            "Conformidade abaixo de 70% indica risco operacional."
        )

# =========================================================
# Bloco 22 — Tab 5: Operadores
# =========================================================

with tab5:
    section_header("Produtividade e análise de operadores")

    df_oper = df_f[df_f["Operador"].notna()].copy()

    if df_oper.empty:
        st.info("Não há operadores vinculados aos filtros selecionados.")
    else:
        funcao_sel = st.radio(
            "Função analisada",
            options=["Todas", "Recepção", "Coleta"],
            horizontal=True,
            key="funcao_operador",
        )

        if funcao_sel != "Todas":
            df_oper = df_oper[df_oper["FuncaoOperador"] == funcao_sel].copy()

        oper = (
            df_oper.groupby(["Operador", "FuncaoOperador"])
            .agg(
                Atendimentos=("ID", "nunique"),
                Etapas=("ID", "size"),
                TempoMedio=("DuracaoMin", "mean"),
                TempoTotalMin=("DuracaoMin", "sum"),
                Unidades=("Unidade", "nunique"),
            )
            .reset_index()
            .sort_values(["Atendimentos", "TempoTotalMin"], ascending=[False, False])
        )

        a, b = st.columns([1.1, 1])

        with a:
            oper_volume = oper[oper["Atendimentos"] >= 10].copy()
            if oper_volume.empty:
                oper_volume = oper.copy()

            oper_volume = oper_volume.sort_values("Atendimentos")

            fig = go.Figure(go.Bar(
                y=oper_volume["Operador"],
                x=oper_volume["Atendimentos"],
                orientation="h",
                marker_color=COLORS["primary"],
                text=oper_volume["Atendimentos"],
                textposition="outside",
                customdata=np.stack([oper_volume["FuncaoOperador"]], axis=-1),
                hovertemplate="<b>%{y}</b><br>Atendimentos: %{x}<br>Função: %{customdata[0]}<extra></extra>",
            ))
            fig.update_layout(
                **plot_layout("Operadores por atendimentos"),
                xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
                yaxis=dict(title=None, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

        with b:
            top_ef = oper[oper["Atendimentos"] >= 10].sort_values("TempoMedio")
            if not top_ef.empty:
                max_tempo_total = top_ef["TempoTotalMin"].max() if top_ef["TempoTotalMin"].max() > 0 else 1

                fig = go.Figure(go.Scatter(
                    x=top_ef["Atendimentos"],
                    y=top_ef["TempoMedio"],
                    mode="markers+text",
                    text=top_ef["Operador"],
                    textposition="top center",
                    customdata=np.stack([top_ef["FuncaoOperador"]], axis=-1),
                    marker=dict(
                        size=np.clip(top_ef["TempoTotalMin"] / max_tempo_total * 40 + 10, 10, 50),
                        color=COLORS["info"],
                        opacity=0.82,
                        line=dict(color="white", width=1.2),
                    ),
                    hovertemplate="<b>%{text}</b><br>Atendimentos: %{x}<br>Tempo médio: %{y:.1f} min<br>Função: %{customdata[0]}<extra></extra>",
                ))
                fig.add_hline(y=top_ef["TempoMedio"].median(), line_dash="dot", line_color=COLORS["deep"], opacity=0.45)
                fig.add_vline(x=top_ef["Atendimentos"].median(), line_dash="dot", line_color=COLORS["deep"], opacity=0.45)

                fig.update_layout(
                    **plot_layout("Eficiência operacional | volume × tempo médio"),
                    xaxis=dict(title="Atendimentos", showgrid=True, gridcolor=COLORS["grid"]),
                    yaxis=dict(title="Tempo médio (min)", showgrid=True, gridcolor=COLORS["grid"]),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione um período com mais volume para avaliar eficiência dos operadores.")

        section_header("Matriz operador × serviço")

        serv_op = (
            df_oper.groupby(["Operador", "Servico"])["ID"]
            .nunique()
            .reset_index(name="Atendimentos")
        )

        operadores_relevantes = oper[oper["Atendimentos"] >= 10]["Operador"].tolist()
        if not operadores_relevantes:
            operadores_relevantes = oper["Operador"].tolist()

        serv_op = serv_op[serv_op["Operador"].isin(operadores_relevantes)]

        if not serv_op.empty:
            pivot = serv_op.pivot(index="Operador", columns="Servico", values="Atendimentos").fillna(0)

            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(c) for c in pivot.columns],
                y=list(pivot.index),
                colorscale=[
                    [0.00, COLORS["surface_soft"]],
                    [0.40, COLORS["support_mint"]],
                    [0.70, COLORS["primary"]],
                    [1.00, COLORS["deep"]],
                ],
                text=[[f"{int(v)}" if v > 0 else "" for v in row] for row in pivot.values],
                texttemplate="%{text}",
                textfont=dict(size=9),
                colorbar=dict(title="Atend."),
                hovertemplate="<b>%{y}</b><br>%{x}<br>%{z} atendimentos<extra></extra>",
            ))
            fig.update_layout(
                **plot_layout("Matriz operador × serviço", height=max(300, len(pivot) * 32 + 120)),
                xaxis=dict(title=None, tickangle=-35),
                yaxis=dict(title=None),
            )
            st.plotly_chart(fig, use_container_width=True)

        section_header("Timeline de operadores por etapa e data")

        col_u, col_d, col_e = st.columns(3)

        with col_u:
            unid_sel = st.selectbox("Unidade", sorted(df_oper["Unidade"].dropna().unique()), key="tl_u")

        with col_d:
            data_sel_tl = st.selectbox(
                "Data",
                sorted(df_oper["Data"].unique()),
                format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
                key="tl_d",
            )

        with col_e:
            etapa_sel = st.selectbox("Etapa", sorted(df_oper["Etapa"].dropna().unique()), key="tl_e")

        df_tl = df_oper[
            (df_oper["Unidade"] == unid_sel) &
            (df_oper["Etapa"] == etapa_sel) &
            (df_oper["Data"] == data_sel_tl)
        ].copy()

        if df_tl.empty:
            st.info("Nenhum dado encontrado para essa combinação de filtros.")
        else:
            fig_tl = fig_timeline_operadores(df_tl, unid_sel, data_sel_tl, etapa_sel)
            if fig_tl is not None:
                st.plotly_chart(fig_tl, use_container_width=True)

            section_header("Resumo por operador")
            resumo_op = calcular_resumo_operadores(df_tl, etapa_sel)

            if not resumo_op.empty:
                st.dataframe(
                    resumo_op,
                    use_container_width=True,
                    hide_index=True,
                )

            if "Servico" in df_tl.columns:
                section_header("Resumo por operador e serviço")
                cruzada = pd.crosstab(df_tl["Operador"], df_tl["Servico"], margins=True, margins_name="TOTAL")
                st.dataframe(cruzada, use_container_width=True)

        section_header("Tabela geral de operadores")
        st.dataframe(
            oper,
            use_container_width=True,
            hide_index=True,
        )

# =========================================================
# Bloco 23 — Animação do fluxo por minuto
# =========================================================

with tab6:
    section_header("Animação do fluxo por minuto")

    if exploded_f.empty:
        st.info("Não há dados suficientes para gerar a animação com os filtros atuais.")
    else:
        info_note(
            "Gera um vídeo minuto a minuto com a distribuição dos pacientes pelas etapas do fluxo "
            "para a unidade e data selecionadas."
        )

        col_a, col_b, col_c = st.columns([1.3, 1, 1])

        unidades_anim = sorted(exploded_f["Unidade"].dropna().unique().tolist())
        datas_anim = sorted(exploded_f["Minuto"].dropna().dt.date.unique())

        with col_a:
            unidade_anim = st.selectbox(
                "Unidade para animação",
                options=unidades_anim,
                key="anim_unidade",
            )

        with col_b:
            data_anim = st.selectbox(
                "Data para animação",
                options=datas_anim,
                format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
                key="anim_data",
            )

        with col_c:
            fps_anim = st.select_slider(
                "Velocidade (FPS)",
                options=[2, 3, 4, 5, 6],
                value=4,
                key="anim_fps",
            )

        if "video_fluxo_bytes" not in st.session_state:
            st.session_state["video_fluxo_bytes"] = None
            st.session_state["video_fluxo_nome"] = None

        if st.button("🎬 Gerar vídeo da animação", type="primary", use_container_width=False):
            with st.spinner("Gerando vídeo da animação..."):
                try:
                    video_bytes, nome_arquivo = gerar_video_fluxo_por_minuto(
                        exploded_f,
                        unidade_desejada=unidade_anim,
                        data_desejada=data_anim,
                        fps=fps_anim,
                    )
                    st.session_state["video_fluxo_bytes"] = video_bytes
                    st.session_state["video_fluxo_nome"] = nome_arquivo
                    st.success("Vídeo gerado com sucesso.")
                except Exception as e:
                    st.session_state["video_fluxo_bytes"] = None
                    st.session_state["video_fluxo_nome"] = None
                    st.error(f"Não foi possível gerar a animação: {e}")

        if st.session_state.get("video_fluxo_bytes") is not None:
            st.video(st.session_state["video_fluxo_bytes"])

            st.download_button(
                "⬇️ Baixar vídeo",
                data=st.session_state["video_fluxo_bytes"],
                file_name=st.session_state["video_fluxo_nome"],
                mime="video/mp4",
            )

# =========================================================
# Bloco 24 — Rodapé
# =========================================================

st.markdown(
    """
    <div class="footer-note">
        Dashboard de Fluxo de Atendimento · Análise de picos, gargalos e produtividade operacional
    </div>
    """,
    unsafe_allow_html=True,
)
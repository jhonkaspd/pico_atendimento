import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dashboard Executivo | Fluxo de Atendimento",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# PALETA — identidade Lab Vision / Unimed
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
# CSS — identidade visual completa
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

        [data-testid="stSidebar"] input {{ color: white !important; }}

        [data-testid="stSidebar"] .stDateInput > div > div {{
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            border-radius: 14px;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        /* ── Hero ── */
        .hero {{
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg,
                    rgba(0,75,82,0.98)   0%,
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

        /* ── Section title ── */
        .section-title {{
            margin-top: 0.9rem;
            margin-bottom: 0.7rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}

        .section-title .dot {{
            width: 10px; height: 10px;
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

        /* ── Caption box ── */
        .caption-box {{
            background: linear-gradient(180deg, rgba(193,208,185,0.22), rgba(255,255,255,0.76));
            border: 1px solid {COLORS["border"]};
            padding: 0.8rem 0.95rem;
            border-radius: 16px;
            color: {COLORS["muted"]};
            font-size: 0.82rem;
            margin-bottom: 0.85rem;
        }}

        /* ── KPI card ── */
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
            width: 38px; height: 38px;
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

        /* ── Insight card ── */
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

        /* ── Info note ── */
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

        /* ── Footer ── */
        .footer-note {{
            color: {COLORS["muted"]};
            font-size: 0.75rem;
            text-align: center;
            padding-top: 1rem;
            margin-top: 1rem;
            border-top: 1px solid {COLORS["border"]};
        }}

        /* ── Metrics nativos ── */
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.84);
            border: 1px solid {COLORS["border"]};
            border-radius: 16px;
            padding: 0.75rem 0.9rem;
        }}

        /* ── Expanders ── */
        div[data-testid="stExpander"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            background: rgba(255,255,255,0.76);
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}

        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.72);
            border-radius: 14px;
            border: 1px solid {COLORS["border"]};
            padding: 10px 16px;
            font-weight: 700;
            color: {COLORS["deep"]};
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(180deg, rgba(0,153,93,0.10), rgba(182,212,76,0.12));
            border-color: rgba(0,153,93,0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

# =========================================================
# Constantes
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
    "1.Espera Recepção": 10,
    "2.Recepção": 10,
    "3.Espera Coleta": 6,
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

DIAS_SEMANA_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MAPA_DIAS_PT   = {"Monday":"Seg","Tuesday":"Ter","Wednesday":"Qua",
                  "Thursday":"Qui","Friday":"Sex","Saturday":"Sáb","Sunday":"Dom"}

# =========================================================
# Helpers de formatação
# =========================================================
def _fmt_int(v):   return f"{int(round(v)):,}".replace(",",".")
def _fmt_float(v, casas=1):
    return f"{v:,.{casas}f}".replace(",","X").replace(".","," ).replace("X",".")
def _fmt_min(v):   return f"{_fmt_float(v, 1)} min"

# =========================================================
# Componentes visuais (mesmos do dashboard_lab_hu)
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
    accent_2    = accent_2 or COLORS["primary_light"]
    accent_soft = f"{accent}22"
    fill_pct    = max(0, min(fill, 1)) * 100
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
            font=dict(size=15, color=COLORS["deep"])
        )

    if legend == "default":
        base["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)"
        )
    elif legend is not None:
        base["legend"] = legend

    base.update(kwargs)
    return base


# =========================================================
# ETL helpers
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
        categories=["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"], ordered=True,
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
            add_etapa(row, "2.Recepção", "Bil_ChamadaRecepcao", "Bil_EncaminhaColeta",
                      "Operador_Recepcao", "Recepção")
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao",
                      "Operador_Coleta", "Coleta")

        elif tipo == "Totem":
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao",
                      "Operador_Coleta", "Coleta")

        else:
            ids_tipo_invalido.add(id_at)

        if len(etapas) == etapas_antes:
            ids_descartados.add(id_at)

    df_etapas = pd.DataFrame(etapas)

    if df_etapas.empty:
        raise ValueError(
            "A transformação não gerou etapas válidas. "
            "Verifique as colunas de data/hora e o TipoAtendimento."
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
    exploded["Data"]    = exploded["Minuto"].dt.date
    exploded["HoraMin"] = exploded["Minuto"].dt.strftime("%H:%M")
    exploded["Hora"]    = exploded["Minuto"].dt.hour

    simultaneos = (
        exploded.groupby(["Unidade","Minuto"])["ID"]
        .nunique().reset_index(name="PacientesSimultaneos")
    )
    simultaneos["Data"]    = simultaneos["Minuto"].dt.date
    simultaneos["Hora"]    = simultaneos["Minuto"].dt.hour
    simultaneos["HoraMin"] = simultaneos["Minuto"].dt.strftime("%H:%M")
    simultaneos = add_weekday_columns(simultaneos, "Minuto")
    return exploded, simultaneos


def apply_filters(df, unidades, etapas, servicos, operadores, periodo):
    out = df.copy()
    if unidades:   out = out[out["Unidade"].isin(unidades)]
    if etapas:     out = out[out["Etapa"].isin(etapas)]
    if servicos:   out = out[out["Servico"].isin(servicos)]
    if operadores: out = out[out["Operador"].isin(operadores)]
    if periodo and len(periodo) == 2:
        ini, fim = periodo
        ini = pd.to_datetime(ini)
        fim = pd.to_datetime(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        out = out[(out["Inicio"] >= ini) & (out["Inicio"] <= fim)]
    return out


def make_kpis(df_f, simultaneos_f):
    return {
        "registros": len(df_f),
        "atendimentos": df_f["ID"].nunique(),
        "unidades": df_f["Unidade"].nunique(),
        "operadores": df_f["Operador"].dropna().nunique(),
        "duracao_media": df_f["DuracaoMin"].mean(),
        "pico_max": simultaneos_f["PacientesSimultaneos"].max() if not simultaneos_f.empty else 0,
        "hora_pico": simultaneos_f.loc[
            simultaneos_f["PacientesSimultaneos"].idxmax(), "Minuto"
        ] if not simultaneos_f.empty else pd.NaT,
    }


def make_insights(df_f, simultaneos_f):
    insights = []
    if df_f.empty: return insights

    etapa_tempo = (
        df_f.groupby("Etapa", as_index=False)["DuracaoMin"]
        .mean().sort_values("DuracaoMin", ascending=False)
    )
    top_etapa = etapa_tempo.iloc[0]
    unid_volume = df_f.groupby("Unidade")["ID"].nunique().sort_values(ascending=False)
    top_unidade, top_val = unid_volume.index[0], unid_volume.iloc[0]

    conformidade = []
    for etapa, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa]
        if not base.empty:
            conformidade.append({
                "Etapa": etapa, "Conformidade": (base["DuracaoMin"] <= limite).mean()*100,
                "Limite": limite,
            })
    conf_df = pd.DataFrame(conformidade).sort_values("Conformidade")
    pior_conf = conf_df.iloc[0] if not conf_df.empty else None

    if not simultaneos_f.empty:
        picos_unid  = simultaneos_f.groupby("Unidade")["PacientesSimultaneos"].max().sort_values(ascending=False)
        unid_pico   = picos_unid.index[0]
        valor_pico  = picos_unid.iloc[0]
        momento_pico = simultaneos_f.loc[simultaneos_f["PacientesSimultaneos"].idxmax(),"Minuto"]
    else:
        unid_pico, valor_pico, momento_pico = "-", 0, pd.NaT

    insights.append({
        "title": "Maior gargalo médio",
        "text":  f"<b>{top_etapa['Etapa']}</b> lidera com tempo médio de <b>{_fmt_float(top_etapa['DuracaoMin'])} min</b>."
    })
    insights.append({
        "title": "Maior volume",
        "text":  f"<b>{top_unidade}</b> concentra <b>{_fmt_int(top_val)} atendimentos</b> no período filtrado."
    })
    if pior_conf is not None:
        insights.append({
            "title": "Maior risco de SLA",
            "text":  f"<b>{pior_conf['Etapa']}</b> tem conformidade de <b>{_fmt_float(pior_conf['Conformidade'])}%</b> para limite de {int(pior_conf['Limite'])} min."
        })
    if pd.notna(momento_pico):
        insights.append({
            "title": "Maior pressão operacional",
            "text":  f"Pico de <b>{_fmt_int(valor_pico)} pacientes simultâneos</b> em <b>{unid_pico}</b> às <b>{momento_pico.strftime('%d/%m %H:%M')}</b>."
        })
    return insights


# =========================================================
# Análises de pico
# =========================================================
def build_tabelas_pico(simultaneos_df):
    if simultaneos_df.empty:
        return None, None, None, None

    picos = (
        simultaneos_df.loc[
            simultaneos_df.groupby(["Unidade","Data"])["PacientesSimultaneos"].idxmax()
        ].reset_index(drop=True)
    )
    tabela_pico_dias    = picos.pivot(index="Unidade", columns="Data", values="PacientesSimultaneos")
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
        return pd.Series({"Cedo":"-","Tardio":"-","Mediana":"-","Média":"-"})
    horarios_str = tabela_horario_pico.loc[unidade].dropna()
    if horarios_str.empty:
        return pd.Series({"Cedo":"-","Tardio":"-","Mediana":"-","Média":"-"})
    horarios_dt  = pd.to_datetime(horarios_str, format="%H:%M")
    minutos_list = [h.hour*60+h.minute for h in horarios_dt]
    media_min    = sum(minutos_list)/len(minutos_list)
    return pd.Series({
        "Cedo":    horarios_dt.sort_values().iloc[0].strftime("%H:%M"),
        "Tardio":  horarios_dt.sort_values().iloc[-1].strftime("%H:%M"),
        "Mediana": horarios_dt.sort_values().iloc[len(horarios_dt)//2].strftime("%H:%M"),
        "Média":   f"{int(media_min//60):02d}:{int(media_min%60):02d}",
    })


def extrato_pico_por_data(data_sel, simultaneos_df, exploded_df):
    data_dt = pd.to_datetime(data_sel).date()
    picos = (
        simultaneos_df[simultaneos_df["Data"] == data_dt]
        .loc[lambda d: d.groupby("Unidade")["PacientesSimultaneos"].idxmax()]
        .reset_index(drop=True)
        [["Unidade","Minuto","PacientesSimultaneos"]]
        .rename(columns={"Minuto":"Horário do Pico","PacientesSimultaneos":"Qtd de Pacientes"})
    )
    if picos.empty:
        return picos

    picos["Horário do Pico_str"] = picos["Horário do Pico"].dt.strftime("%H:%M")

    def contar_etapas(row):
        ev = exploded_df[
            (exploded_df["Unidade"] == row["Unidade"]) &
            (exploded_df["Minuto"]  == row["Horário do Pico"])
        ]["Etapa"].value_counts()
        return pd.Series({
            "1.Espera Recepção": ev.get("1.Espera Recepção", 0),
            "2.Recepção":        ev.get("2.Recepção", 0),
            "3.Espera Coleta":   ev.get("3.Espera Coleta", 0),
            "4.Coleta":          ev.get("4.Coleta", 0),
        })

    etapas_cols = picos.apply(contar_etapas, axis=1)
    out = pd.concat([picos[["Unidade","Horário do Pico_str","Qtd de Pacientes"]], etapas_cols], axis=1)
    return out.rename(columns={"Horário do Pico_str":"Horário do Pico"}).sort_values("Unidade").reset_index(drop=True)


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


def fig_timeline_operadores(df_tl, unidade, data_sel, etapa_sel):
    if df_tl.empty:
        return None

    df_plot = df_tl.copy().sort_values(["Operador", "Inicio"]).reset_index(drop=True)

    # ordem dos operadores no eixo Y
    ordem_operadores = (
        df_plot.groupby("Operador")["Inicio"]
        .min()
        .sort_values()
        .index.tolist()
    )

    # cores por operador, para ficar parecido com o notebook
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

        # duração em MILISSEGUNDOS para eixo tipo date
        dur_ms = (sub["Fim"] - sub["Inicio"]).dt.total_seconds() * 1000

        # texto central nas barras
        labels = [
            f"{int(round(v))}min" if v >= 1 else ""
            for v in (sub["Fim"] - sub["Inicio"]).dt.total_seconds() / 60
        ]

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
                ((sub["Fim"] - sub["Inicio"]).dt.total_seconds() / 60).round(1),
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
# Sidebar
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
    uploaded = st.file_uploader(
        "Envie a planilha de fluxo",
        type=["xlsx","xls","csv"],
        help="Use a mesma estrutura do arquivo exportado do seu processo.",
    )

# =========================================================
# Hero (sem dados carregados)
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

try:
    df_raw = load_data(uploaded)
    df_transformado, qualidade_base = transformar_nova_base(df_raw)
    df = preprocess_data(df_transformado)
    exploded, simultaneos = build_minute_level(df)
except Exception as e:
    st.error(f"Não foi possível processar a base: {e}")
    st.stop()

# ── Filtros na sidebar após carregar ──
with st.sidebar:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("**Filtros**")

    min_date = pd.to_datetime(df["Inicio"]).min().date()
    max_date = pd.to_datetime(df["Inicio"]).max().date()

    col_dt1, col_dt2 = st.columns(2)
    with col_dt1:
        periodo_inicio = st.date_input("Início", value=min_date,
                                        min_value=min_date, max_value=max_date,
                                        format="DD/MM/YYYY", key="dt_ini")
    with col_dt2:
        periodo_fim = st.date_input("Fim", value=max_date,
                                     min_value=min_date, max_value=max_date,
                                     format="DD/MM/YYYY", key="dt_fim")

    unidades = st.multiselect("Unidade", sorted(df["Unidade"].dropna().unique().tolist()))

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:0.78rem;line-height:1.65;opacity:0.94;">
            <b>Base carregada</b><br>
            {min_date:%d/%m/%Y} até {max_date:%d/%m/%Y}<br><br>

            <b>Qualidade da base</b><br>
            Linhas origem: {_fmt_int(qualidade_base['total_linhas'])}<br>
            Atendimentos válidos: {_fmt_int(qualidade_base['atendimentos_validos'])}<br>
            Atendimentos descartados: {_fmt_int(qualidade_base['atendimentos_descartados'])}<br>
            Tipos inválidos: {_fmt_int(qualidade_base['tipos_invalidos'])}<br>
            Etapas geradas: {_fmt_int(qualidade_base['etapas_geradas'])}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Aplicar filtros ──
df_f = apply_filters(df, unidades, [], [], [], (periodo_inicio, periodo_fim))
if df_f.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

exploded_f, simultaneos_f = build_minute_level(df_f)

# ── Reescrever hero com dados reais ──
kpis = make_kpis(df_f, simultaneos_f)
periodo_ini_real = pd.to_datetime(df_f["Inicio"]).min()
periodo_fim_real = pd.to_datetime(df_f["Inicio"]).max()
titulo_unidade   = ", ".join(unidades) if unidades else "Todas as unidades"

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
            <span class="badge">🔁 Pico: {_fmt_int(kpis['pico_max'])} simultâneos</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

caption_box(
    "<b>Leitura executiva:</b> o painel identifica os momentos de maior pressão operacional, "
    "gargalos por etapa do fluxo e oportunidades de melhoria por unidade e operador."
)

# =========================================================
# KPI Cards (estilo Lab Vision)
# =========================================================
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(kpi_card(
        "Registros", _fmt_int(kpis["registros"]),
        f"{_fmt_int(kpis['atendimentos'])} atendimentos únicos",
        COLORS["deep"], icon="📋", fill=1, accent_2=COLORS["primary"],
    ), unsafe_allow_html=True)

with k2:
    st.markdown(kpi_card(
        "Unidades", _fmt_int(kpis["unidades"]),
        f"{_fmt_int(kpis['operadores'])} operadores ativos",
        COLORS["primary"], icon="🏢",
        fill=min(kpis["unidades"]/10, 1), accent_2=COLORS["primary_light"],
    ), unsafe_allow_html=True)

with k3:
    st.markdown(kpi_card(
        "Operadores", _fmt_int(kpis["operadores"]),
        "Profissionais no período filtrado",
        COLORS["info"], icon="👥",
        fill=min(kpis["operadores"]/50, 1), accent_2=COLORS["support_ice"],
    ), unsafe_allow_html=True)

with k4:
    st.markdown(kpi_card(
        "Tempo médio", _fmt_min(kpis["duracao_media"]) if pd.notna(kpis["duracao_media"]) else "—",
        "Duração média por etapa",
        COLORS["alert"], icon="⏱️",
        fill=min(kpis["duracao_media"]/20, 1) if pd.notna(kpis["duracao_media"]) else 0,
        accent_2=COLORS["warning"],
    ), unsafe_allow_html=True)

with k5:
    st.markdown(kpi_card(
        "Pico simultâneo", _fmt_int(kpis["pico_max"]),
        f"Pacientes ao mesmo tempo em atendimento",
        COLORS["danger"], icon="🔝",
        fill=min(kpis["pico_max"]/50, 1), accent_2=COLORS["danger_dark"],
    ), unsafe_allow_html=True)

with k6:
    hora_pico_str = kpis["hora_pico"].strftime("%d/%m %H:%M") if pd.notna(kpis["hora_pico"]) else "—"
    st.markdown(kpi_card(
        "Horário do pico", hora_pico_str,
        "Momento de maior pressão operacional",
        COLORS["danger_dark"], icon="🕐",
        fill=0.8, accent_2=COLORS["alert"],
    ), unsafe_allow_html=True)

# =========================================================
# Insight cards
# =========================================================
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
insights = make_insights(df_f, simultaneos_f)
insight_cols = st.columns(len(insights)) if insights else []
for col, ins in zip(insight_cols, insights):
    with col:
        insight_card(ins["title"], ins["text"])

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumo Executivo",
    "🔥 Picos de Atendimento",
    "Capacidade & Heatmaps",
    "Etapas & SLA",
    "Operadores"
])

# ── Tab 1: Resumo ──────────────────────────────────────────
with tab1:
    section_header("Volume e composição do fluxo de atendimento")

    a, b = st.columns([1.2, 1])
    with a:
        vol_dia = df_f.groupby("Data")["ID"].nunique().reset_index(name="Atendimentos")
        fig = go.Figure(go.Scatter(
            x=vol_dia["Data"], y=vol_dia["Atendimentos"],
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=6, color=COLORS["deep"]),
            fill="tozeroy", fillcolor=f"rgba(0,153,93,0.07)",
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
            y=unid["Unidade"], x=unid["Atendimentos"],
            orientation="h",
            marker_color=COLORS["primary"],
            text=unid["Atendimentos"], textposition="outside",
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
        cores_etapa = [COLORS["primary"] if v <= 6 else COLORS["alert"] if v <= 10 else COLORS["danger"]
                       for v in etapa["DuracaoMin"]]
        fig = go.Figure(go.Bar(
            y=etapa["Etapa"], x=etapa["DuracaoMin"],
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
        fig  = go.Figure(go.Pie(
            labels=tipo["TipoAtendimento"], values=tipo["Atendimentos"],
            hole=0.55,
            marker=dict(colors=[COLORS["primary"], COLORS["primary_light"],
                                 COLORS["support_ice"], COLORS["alert"]]),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value} atendimentos (%{percent})<extra></extra>",
        ))
        fig.update_layout(**plot_layout("Mix de tipo de atendimento"))
        st.plotly_chart(fig, use_container_width=True)


# ── Tab 2: Picos ───────────────────────────────────────────
with tab2:
    section_header("Análise de picos de atendimento por unidade")

    tabela_pico_dias, tabela_horario_pico, _, pico_total_por_dia = build_tabelas_pico(simultaneos_f)

    if tabela_pico_dias is None:
        st.info("Dados insuficientes para análise de picos com os filtros atuais.")
    else:
        cols_str = [str(c) for c in tabela_pico_dias.columns]

        fig_heat_unid = go.Figure(go.Heatmap(
            z=tabela_pico_dias.values,
            x=cols_str, y=list(tabela_pico_dias.index),
            colorscale=[
                [0.00, COLORS["surface_soft"]],
                [0.30, COLORS["support_mint"]],
                [0.60, COLORS["primary_light"]],
                [0.80, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            text=[[f"{int(v)}" if pd.notna(v) else "—" for v in row]
                  for row in tabela_pico_dias.values],
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorbar=dict(title="Pico"),
            hovertemplate="<b>%{y}</b><br>Data: %{x}<br>Pico: %{z:.0f} pacientes<extra></extra>",
        ))
        fig_heat_unid.update_layout(
            **plot_layout("Pico de pacientes simultâneos por unidade e dia",
                          height=max(300, len(tabela_pico_dias)*38+100)),
            xaxis=dict(title=None, tickangle=-35),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig_heat_unid, use_container_width=True)

        total_vals = [[float(pico_total_por_dia.get(c, 0)) for c in tabela_pico_dias.columns]]
        fig_heat_total = go.Figure(go.Heatmap(
            z=total_vals, x=cols_str, y=["Total"],
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
                margin=dict(l=8, r=8, t=50, b=8)
            ),
            xaxis=dict(title=None, tickangle=-35),
            yaxis=dict(title=None),            
        )
        st.plotly_chart(fig_heat_total, use_container_width=True)

        section_header("Horário de pico por unidade — estatísticas")

        estat = tabela_horario_pico.index.to_series().apply(
            lambda u: calcular_estatisticas_picos(u, tabela_horario_pico, tabela_pico_dias)
        )
        cols_dia    = [str(c) for c in tabela_horario_pico.columns]
        tabela_exib = tabela_horario_pico.copy()
        tabela_exib.columns = cols_dia
        tabela_exib = pd.concat([tabela_exib, estat], axis=1).reset_index()
        tabela_exib.columns.name = None

        def highlight_max_day(row, pico_dias):
            unidade = row.iloc[0]
            if unidade not in pico_dias.index:
                return [""] * len(row)
            dia_max = str(pico_dias.loc[unidade].idxmax())
            return [
                f"background-color: {COLORS['danger']}22; color: {COLORS['danger_dark']}; font-weight:bold"
                if col == dia_max else ""
                for col in row.index
            ]

        styled = tabela_exib.style.apply(
            lambda row: highlight_max_day(row, tabela_pico_dias.copy().rename(columns=str)),
            axis=1
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

        section_header("Extrato de pico por unidade — por data")

        datas_disponiveis = sorted(simultaneos_f["Data"].unique())
        data_sel = st.selectbox(
            "Selecione a data:",
            options=datas_disponiveis,
            format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
            key="extrato_data",
        )

        extrato = extrato_pico_por_data(data_sel, simultaneos_f, exploded_f)
        if extrato.empty:
            st.warning(f"Nenhum dado para {pd.to_datetime(data_sel).strftime('%d/%m/%Y')}.")
        else:
            st.dataframe(extrato, use_container_width=True, hide_index=True)
            info_note(
                "Distribuição dos pacientes simultâneos pelas etapas do fluxo no momento de pico de cada unidade."
            )


# ── Tab 3: Capacidade & Heatmaps ──────────────────────────
with tab3:
    section_header("Ocupação simultânea e pressão operacional")

    if simultaneos_f.empty:
        st.info("Dados insuficientes para calcular ocupação simultânea com os filtros atuais.")
    else:
        pico_hora = simultaneos_f.groupby("Hora")["PacientesSimultaneos"].mean().reset_index()
        fig = go.Figure(go.Bar(
            x=pico_hora["Hora"], y=pico_hora["PacientesSimultaneos"],
            marker_color=[COLORS["primary"] if v < pico_hora["PacientesSimultaneos"].quantile(0.75)
                          else COLORS["alert"] if v < pico_hora["PacientesSimultaneos"].max()
                          else COLORS["danger"]
                          for v in pico_hora["PacientesSimultaneos"]],
            text=[f"{v:.1f}" for v in pico_hora["PacientesSimultaneos"]],
            textposition="outside",
            hovertemplate="<b>%{x}h</b><br>Média: %{y:.1f} pacientes simultâneos<extra></extra>",
        ))
        fig.update_layout(
            **plot_layout("Média de pacientes simultâneos por hora"),
            xaxis=dict(title="Hora", showgrid=False, dtick=1),
            yaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True)

        a, b = st.columns([1, 1])
        with a:
            heat2 = simultaneos_f.groupby(["DiaSemanaLabel","Hora"])["PacientesSimultaneos"].mean().reset_index()
            ordem = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
            heat2["DiaSemanaLabel"] = pd.Categorical(heat2["DiaSemanaLabel"], categories=ordem, ordered=True)
            heat2_pivot = heat2.sort_values(["DiaSemanaLabel","Hora"]).pivot(
                index="DiaSemanaLabel", columns="Hora", values="PacientesSimultaneos"
            ).fillna(0)
            fig = go.Figure(go.Heatmap(
                z=heat2_pivot.values,
                x=[f"{h:02d}h" for h in heat2_pivot.columns],
                y=list(heat2_pivot.index),
                colorscale=[
                    [0.00, COLORS["surface_soft"]],
                    [0.35, COLORS["support_mint"]],
                    [0.65, COLORS["primary_light"]],
                    [0.82, COLORS["alert"]],
                    [1.00, COLORS["danger_dark"]],
                ],
                text=[[f"{v:.1f}" if v > 0 else "" for v in row] for row in heat2_pivot.values],
                texttemplate="%{text}",
                textfont=dict(size=9),
                colorbar=dict(title="Pacientes"),
                hovertemplate="%{y} · %{x}<br>Média: %{z:.1f} pacientes<extra></extra>",
            ))
            fig.update_layout(
                **plot_layout("Pressão operacional média por dia e hora"),
                xaxis=dict(title=None),
                yaxis=dict(title=None),
            )
            st.plotly_chart(fig, use_container_width=True)

        with b:
            top_picos = simultaneos_f.sort_values("PacientesSimultaneos", ascending=False).head(20).copy()
            top_picos["Momento"] = top_picos["Minuto"].dt.strftime("%d/%m/%Y %H:%M")
            section_header("Top 20 momentos de maior pico")
            st.dataframe(
                top_picos[["Unidade","Momento","PacientesSimultaneos"]]
                .rename(columns={"PacientesSimultaneos":"Qtd simultânea"}),
                use_container_width=True, hide_index=True,
            )


# ── Tab 4: Etapas & SLA ───────────────────────────────────
with tab4:
    section_header("Conformidade e análise de SLA por etapa")

    slas = []
    for etapa_nome, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa_nome]
        if base.empty: continue
        slas.append({
            "Etapa": etapa_nome, "SLA (min)": limite,
            "Tempo médio":    base["DuracaoMin"].mean(),
            "Conformidade %": (base["DuracaoMin"] <= limite).mean() * 100,
            "P95 (min)":      base["DuracaoMin"].quantile(0.95),
        })
    sla_df = pd.DataFrame(slas)

    a, b = st.columns([1, 1])
    with a:
        if not sla_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sla_df["Etapa"], y=sla_df["Tempo médio"],
                name="Tempo médio",
                marker_color=COLORS["primary"],
                text=[f"{v:.1f}" for v in sla_df["Tempo médio"]],
                textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=sla_df["Etapa"], y=sla_df["SLA (min)"],
                mode="lines+markers", name="Limite SLA",
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
            cores_conf = [COLORS["primary"] if v >= 85 else COLORS["alert"] if v >= 70
                          else COLORS["danger"] for v in sla_df["Conformidade %"]]
            fig = go.Figure(go.Bar(
                y=sla_df.sort_values("Conformidade %")["Etapa"],
                x=sla_df.sort_values("Conformidade %")["Conformidade %"],
                orientation="h",
                marker_color=cores_conf,
                text=[f"{v:.1f}%" for v in sla_df.sort_values("Conformidade %")["Conformidade %"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Conformidade: %{x:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                **plot_layout("Conformidade por etapa"),
                xaxis=dict(title=None, range=[0,110], ticksuffix="%",
                           showgrid=True, gridcolor=COLORS["grid"]),
                yaxis=dict(title=None, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

    c, d = st.columns([1, 1])
    with c:
        fig = go.Figure()
        for i, etapa_nome in enumerate(df_f["Etapa"].unique()):
            sub_vals = df_f[df_f["Etapa"] == etapa_nome]["DuracaoMin"]
            fig.add_trace(go.Box(
                y=sub_vals, name=etapa_nome,
                marker_color=[COLORS["primary"], COLORS["info"],
                               COLORS["alert"], COLORS["danger"]][i % 4],
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
                Volume=("ID", "nunique")
            )
            .query("Volume >= 20")
            .sort_values("TempoMedio", ascending=False)
            .reset_index()
        )
        fig = go.Figure(go.Bar(
            y=serv["Servico"], x=serv["TempoMedio"],
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
        st.dataframe(
            sla_df,
            use_container_width=True,
            hide_index=True,
        )
        info_note(
            "<b>SLA:</b> limite de tempo aceitável por etapa. "
            "<b>P95:</b> 95% dos atendimentos estão abaixo desse tempo. "
            "Conformidade abaixo de 70% indica risco operacional."
        )


# ── Tab 5: Operadores ─────────────────────────────────────
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
                y=oper_volume["Operador"], x=oper_volume["Atendimentos"],
                orientation="h",
                marker_color=COLORS["primary"],
                text=oper_volume["Atendimentos"], textposition="outside",
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
                    x=top_ef["Atendimentos"], y=top_ef["TempoMedio"],
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
                fig.add_hline(y=top_ef["TempoMedio"].median(), line_dash="dot",
                              line_color=COLORS["deep"], opacity=0.45)
                fig.add_vline(x=top_ef["Atendimentos"].median(), line_dash="dot",
                              line_color=COLORS["deep"], opacity=0.45)
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
                key="tl_d"
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
                    resumo_op.style.format({
                        "Pacientes únicos": "{:.0f}",
                        "Etapas executadas": "{:.0f}",
                        "Tempo Médio (min)": "{:.1f}",
                        "Conformidade da Etapa (%)": "{:.1f}",
                        "Total GAPs (min)": "{:.1f}",
                        "GAP Mín (min)": "{:.1f}",
                        "GAP Máx (min)": "{:.1f}",
                        "GAP Médio (min)": "{:.1f}",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )

            if "Servico" in df_tl.columns:
                section_header("Resumo por operador e serviço")
                cruzada = pd.crosstab(df_tl["Operador"], df_tl["Servico"], margins=True, margins_name="TOTAL")
                st.dataframe(cruzada, use_container_width=True)

        section_header("Tabela geral de operadores")
        st.dataframe(
            oper.style.format({
                "Atendimentos": "{:.0f}",
                "Etapas": "{:.0f}",
                "TempoMedio": "{:.1f}",
                "TempoTotalMin": "{:.1f}",
                "Unidades": "{:.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

# ── Rodapé ───────────────────────────────────────────────
st.markdown(
    """
    <div class="footer-note">
        Dashboard de Fluxo de Atendimento · Análise de picos, gargalos e produtividade operacional
    </div>
    """,
    unsafe_allow_html=True,
)
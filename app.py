
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
# Estilo
# =========================================================
st.markdown(
    """
    <style>
    .main {background-color: #08101f;}
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1324 0%, #111b31 100%);
    }
    .hero {
        padding: 1.2rem 1.4rem;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(135deg, rgba(18,32,58,1) 0%, rgba(25,54,95,1) 50%, rgba(22,103,147,1) 100%);
        border-radius: 22px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 18px 40px rgba(0,0,0,0.22);
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
        line-height: 1.1;
    }
    .hero p {
        margin: 0.35rem 0 0 0;
        color: rgba(255,255,255,0.82);
    }
    .section-card {
        padding: 1rem 1.15rem;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 0.8rem;
    }
    .insight-card {
        padding: 0.9rem 1rem;
        border-radius: 18px;
        background: rgba(18, 120, 184, 0.12);
        border: 1px solid rgba(88, 176, 236, 0.25);
        min-height: 120px;
    }
    .small-muted {
        color: #95a2bf;
        font-size: 0.9rem;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(12,18,34,0.95), rgba(17,27,49,0.95));
        border: 1px solid rgba(255,255,255,0.06);
        padding: 10px 14px;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    "Prioridade", "Servico", "tEtapa", "Unidade"
]

# =========================================================
# Helpers
# =========================================================
def _fmt_int(v):
    return f"{int(round(v)):,}".replace(",", ".")

def _fmt_float(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _fmt_min(v):
    return f"{_fmt_float(v, 1)} min"

def _get_pct_delta(current, baseline):
    if baseline in [0, np.nan] or pd.isna(baseline):
        return None
    return ((current / baseline) - 1) * 100

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

# =========================================================
# ETL | Nova base de atendimentos (1 linha por atendimento)
# Converte para o formato esperado pelo dashboard:
# 1 linha por etapa do atendimento
# =========================================================
COLUNAS_NOVA_BASE = [
    "Unidade",
    "ID",
    "Bil_Emissao",
    "Bil_ChamadaRecepcao",
    "Bil_EncaminhaColeta",
    "Bil_ChamadaColeta",
    "Bil_Finalizacao",
    "TipoAtendimento",
    "Operador_Recepcao",
    "Operador_Coleta",
    "ServicoOrdem1",
    "ServicoOrdem2",
]

def transformar_nova_base(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma a nova base (1 linha por atendimento) em uma base
    estruturada por etapas, compatível com o preprocess_data() atual.

    Regras:
    - Guichê:
        1.Espera Recepção = Bil_Emissao -> Bil_ChamadaRecepcao
        2.Recepção        = Bil_ChamadaRecepcao -> Bil_EncaminhaColeta
        3.Espera Coleta   = Bil_EncaminhaColeta -> Bil_ChamadaColeta
        4.Coleta          = Bil_ChamadaColeta -> Bil_Finalizacao

    - Totem:
        não existem as etapas de recepção
        3.Espera Coleta   = Bil_EncaminhaColeta -> Bil_ChamadaColeta
        4.Coleta          = Bil_ChamadaColeta -> Bil_Finalizacao
    """
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    df = df_raw.copy()

    # -----------------------------
    # 1) Validar colunas obrigatórias da nova base
    # -----------------------------
    faltantes = [c for c in COLUNAS_NOVA_BASE if c not in df.columns]
    if faltantes:
        raise ValueError(
            "A nova base não contém todas as colunas esperadas. "
            f"Colunas ausentes: {faltantes}"
        )

    # -----------------------------
    # 2) Padronização básica
    # -----------------------------
    for col in [
        "Bil_Emissao",
        "Bil_ChamadaRecepcao",
        "Bil_EncaminhaColeta",
        "Bil_ChamadaColeta",
        "Bil_Finalizacao",
    ]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in [
        "Unidade",
        "ID",
        "TipoAtendimento",
        "Operador_Recepcao",
        "Operador_Coleta",
        "ServicoOrdem1",
        "ServicoOrdem2",
    ]:
        df[col] = df[col].astype(str).str.strip()

    # Corrigir strings "nan" criadas pelo astype(str)
    df = df.replace({
        "nan": np.nan,
        "None": np.nan,
        "NaT": np.nan,
        "": np.nan,
    })

    # Normalizar TipoAtendimento
    df["TipoAtendimento"] = df["TipoAtendimento"].replace({
        "Guiche": "Guichê",
        "GUICHE": "Guichê",
        "guiche": "Guichê",
        "guichê": "Guichê",
        "totem": "Totem",
        "TOTEM": "Totem",
    })

    # Serviço principal:
    # prioriza ServicoOrdem2 e usa ServicoOrdem1 como fallback
    df["Servico"] = df["ServicoOrdem2"].where(
        df["ServicoOrdem2"].notna(),
        df["ServicoOrdem1"]
    )

    # fallback extra caso ambas venham vazias
    df["Servico"] = df["Servico"].fillna("Não informado")

    # Prioridade não existe na nova base; preencher fixo para compatibilidade
    df["Prioridade"] = "Normal"

    # -----------------------------
    # 3) Função auxiliar para criar cada etapa
    # -----------------------------
    etapas = []

    def adicionar_etapa(
        row,
        nome_etapa,
        inicio_col,
        fim_col,
        operador=None,
    ):
        inicio = row[inicio_col]
        fim = row[fim_col]

        # só cria etapa se ambos os tempos existirem
        if pd.isna(inicio) or pd.isna(fim):
            return

        # evita etapa com ordem temporal inválida
        if fim < inicio:
            return

        duracao_min = (fim - inicio).total_seconds() / 60

        etapas.append({
            "ID": row["ID"],
            "Inicio": inicio,
            "Fim": fim,
            "Etapa": nome_etapa,
            "TipoAtendimento": row["TipoAtendimento"],
            "Operador": row[operador] if operador else np.nan,
            "Prioridade": row["Prioridade"],
            "Servico": row["Servico"],
            "tEtapa": duracao_min,
            "Unidade": row["Unidade"],
        })

    # -----------------------------
    # 4) Explodir atendimentos em etapas
    # -----------------------------
    for _, row in df.iterrows():
        tipo = row["TipoAtendimento"]

        if tipo == "Guichê":
            adicionar_etapa(
                row,
                "1.Espera Recepção",
                "Bil_Emissao",
                "Bil_ChamadaRecepcao",
            )
            adicionar_etapa(
                row,
                "2.Recepção",
                "Bil_ChamadaRecepcao",
                "Bil_EncaminhaColeta",
                operador="Operador_Recepcao",
            )
            adicionar_etapa(
                row,
                "3.Espera Coleta",
                "Bil_EncaminhaColeta",
                "Bil_ChamadaColeta",
            )
            adicionar_etapa(
                row,
                "4.Coleta",
                "Bil_ChamadaColeta",
                "Bil_Finalizacao",
                operador="Operador_Coleta",
            )

        elif tipo == "Totem":
            adicionar_etapa(
                row,
                "3.Espera Coleta",
                "Bil_EncaminhaColeta",
                "Bil_ChamadaColeta",
            )
            adicionar_etapa(
                row,
                "4.Coleta",
                "Bil_ChamadaColeta",
                "Bil_Finalizacao",
                operador="Operador_Coleta",
            )

        else:
            # fallback:
            # se vier algum tipo não previsto, tenta construir ao menos coleta
            adicionar_etapa(
                row,
                "3.Espera Coleta",
                "Bil_EncaminhaColeta",
                "Bil_ChamadaColeta",
            )
            adicionar_etapa(
                row,
                "4.Coleta",
                "Bil_ChamadaColeta",
                "Bil_Finalizacao",
                operador="Operador_Coleta",
            )

    df_etapas = pd.DataFrame(etapas)

    if df_etapas.empty:
        raise ValueError(
            "A transformação da nova base não gerou etapas válidas. "
            "Verifique se as colunas de data/hora estão preenchidas corretamente."
        )

    # -----------------------------
    # 5) Ordenação final
    # -----------------------------
    ordem_etapas = {
        "1.Espera Recepção": 1,
        "2.Recepção": 2,
        "3.Espera Coleta": 3,
        "4.Coleta": 4,
    }

    df_etapas["OrdemEtapa"] = df_etapas["Etapa"].map(ordem_etapas).fillna(99)
    df_etapas = df_etapas.sort_values(
        ["Inicio", "ID", "OrdemEtapa"]
    ).drop(columns="OrdemEtapa")

    # Garantir colunas finais exatamente no formato esperado
    df_etapas = df_etapas[
        [
            "ID",
            "Inicio",
            "Fim",
            "Etapa",
            "TipoAtendimento",
            "Operador",
            "Prioridade",
            "Servico",
            "tEtapa",
            "Unidade",
        ]
    ].reset_index(drop=True)

    return df_etapas

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


def add_weekday_columns(df: pd.DataFrame, datetime_col: str, label_col: str = "DiaSemanaLabel") -> pd.DataFrame:
    """Adiciona colunas de dia da semana de forma robusta a partir de uma coluna datetime."""
    serie = pd.to_datetime(df[datetime_col], errors="coerce")
    dia_semana = serie.dt.day_name()
    df["DiaSemana"] = pd.Categorical(dia_semana, categories=DIAS_SEMANA_EN, ordered=True)
    df[label_col] = pd.Categorical(
        df["DiaSemana"].map(MAPA_DIAS_PT),
        categories=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        ordered=True,
    )
    return df

def preprocess_data(df_raw: pd.DataFrame):
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
def build_minute_level(df: pd.DataFrame):
    work = df.copy()
    work["Minuto"] = work.apply(
        lambda row: pd.date_range(
            start=row["Inicio"].floor("min"),
            end=(row["Fim"] - pd.Timedelta(seconds=1)).floor("min"),
            freq="min",
        ) if row["Fim"] > row["Inicio"] else pd.DatetimeIndex([row["Inicio"].floor("min")]),
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
    total_registros = len(df_f)
    atendimentos = df_f["ID"].nunique()
    unidades = df_f["Unidade"].nunique()
    operadores = df_f["Operador"].nunique()
    duracao_media = df_f["DuracaoMin"].mean()
    pico_max = simultaneos_f["PacientesSimultaneos"].max() if not simultaneos_f.empty else 0
    hora_pico = simultaneos_f.loc[simultaneos_f["PacientesSimultaneos"].idxmax(), "Minuto"] if not simultaneos_f.empty else pd.NaT
    return {
        "registros": total_registros,
        "atendimentos": atendimentos,
        "unidades": unidades,
        "operadores": operadores,
        "duracao_media": duracao_media,
        "pico_max": pico_max,
        "hora_pico": hora_pico,
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

    unid_volume = (
        df_f.groupby("Unidade")["ID"].nunique().sort_values(ascending=False)
    )
    top_unidade = unid_volume.index[0]
    top_unidade_val = unid_volume.iloc[0]

    conformidade = []
    for etapa, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa]
        if not base.empty:
            conformidade.append({
                "Etapa": etapa,
                "Conformidade": (base["DuracaoMin"] <= limite).mean() * 100,
                "Limite": limite,
                "Media": base["DuracaoMin"].mean(),
            })
    conf_df = pd.DataFrame(conformidade).sort_values("Conformidade")
    pior_conf = conf_df.iloc[0] if not conf_df.empty else None

    if not simultaneos_f.empty:
        picos_unid = simultaneos_f.groupby("Unidade")["PacientesSimultaneos"].max().sort_values(ascending=False)
        unid_pico = picos_unid.index[0]
        valor_pico = picos_unid.iloc[0]
        momento_pico = simultaneos_f.loc[
            simultaneos_f["PacientesSimultaneos"].idxmax(), "Minuto"
        ]
    else:
        unid_pico = "-"
        valor_pico = 0
        momento_pico = pd.NaT

    insights.append(
        f"**Maior gargalo médio:** {top_etapa['Etapa']} com tempo médio de **{_fmt_float(top_etapa['DuracaoMin'])} min**."
    )
    insights.append(
        f"**Maior volume:** {top_unidade} concentra **{_fmt_int(top_unidade_val)} atendimentos** no período filtrado."
    )
    if pior_conf is not None:
        insights.append(
            f"**Maior risco de SLA:** {pior_conf['Etapa']} tem conformidade de **{_fmt_float(pior_conf['Conformidade'])}%** para limite de {int(pior_conf['Limite'])} min."
        )
    if pd.notna(momento_pico):
        insights.append(
            f"**Maior pressão operacional:** pico de **{_fmt_int(valor_pico)} pacientes simultâneos** em **{unid_pico}**, às **{momento_pico.strftime('%d/%m %H:%M')}**."
        )
    return insights

def fig_template(fig, title=None):
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,16,31,0.35)",
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.07)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)")
    return fig

# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## Fonte de dados")
    uploaded = st.file_uploader(
        "Envie a planilha de fluxo",
        type=["xlsx", "xls", "csv"],
        help="Use a mesma estrutura do arquivo exportado do seu processo.",
    )
    st.caption("O app não expõe o código para os usuários finais. Basta compartilhar o link após publicar.")

st.markdown(
    """
    <div class="hero">
        <h1>Dashboard Executivo de Fluxo de Atendimento</h1>
        <p>Visão gerencial de volume, capacidade, gargalos, SLA e produtividade operacional por unidade, etapa e operador.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded is None:
    st.info("Envie a planilha na barra lateral para carregar o dashboard.")
    st.stop()

try:
    df_raw = load_data(uploaded)
    df_transformado = transformar_nova_base(df_raw)
    df = preprocess_data(df_transformado)
    exploded, simultaneos = build_minute_level(df)
except Exception as e:
    st.error(f"Não foi possível processar a base: {e}")
    st.stop()

with st.sidebar:
    st.markdown("## Filtros")
    min_date = pd.to_datetime(df["Inicio"]).min().date()
    max_date = pd.to_datetime(df["Inicio"]).max().date()

    periodo = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    unidades = st.multiselect("Unidade", sorted(df["Unidade"].dropna().unique().tolist()))
    etapas = st.multiselect("Etapa", sorted(df["Etapa"].dropna().unique().tolist()))
    servicos = st.multiselect("Serviço", sorted(df["Servico"].dropna().unique().tolist()))
    operadores = st.multiselect("Operador", sorted(df["Operador"].dropna().unique().tolist()))
    top_n = st.slider("Top N operadores / unidades", 5, 30, 12)

df_f = apply_filters(df, unidades, etapas, servicos, operadores, periodo)
if df_f.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

# Refiltrar estruturas derivadas
ids = set(df_f["ID"].unique())
exploded_f = exploded[exploded["ID"].isin(ids)].copy()
simultaneos_f = (
    exploded_f.groupby(["Unidade", "Minuto"])["ID"]
    .nunique()
    .reset_index(name="PacientesSimultaneos")
)
if not simultaneos_f.empty:
    simultaneos_f["Data"] = simultaneos_f["Minuto"].dt.date
    simultaneos_f["Hora"] = simultaneos_f["Minuto"].dt.hour
    simultaneos_f["HoraMin"] = simultaneos_f["Minuto"].dt.strftime("%H:%M")
    simultaneos_f = add_weekday_columns(simultaneos_f, "Minuto")

# =========================================================
# KPIs
# =========================================================
kpis = make_kpis(df_f, simultaneos_f)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Registros", _fmt_int(kpis["registros"]))
c2.metric("Atendimentos", _fmt_int(kpis["atendimentos"]))
c3.metric("Unidades", _fmt_int(kpis["unidades"]))
c4.metric("Operadores", _fmt_int(kpis["operadores"]))
c5.metric("Tempo médio", _fmt_min(kpis["duracao_media"]))
c6.metric(
    "Pico simultâneo",
    _fmt_int(kpis["pico_max"]),
    delta=kpis["hora_pico"].strftime("%d/%m %H:%M") if pd.notna(kpis["hora_pico"]) else None,
)

insights = make_insights(df_f, simultaneos_f)
i1, i2, i3, i4 = st.columns(4)
for col, txt in zip([i1, i2, i3, i4], insights + [""] * (4 - len(insights))):
    with col:
        st.markdown(f"<div class='insight-card'>{txt}</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumo Executivo", "Capacidade & Picos", "Etapas & SLA", "Operadores", "Base Filtrada"
])

# =========================================================
# Tab 1
# =========================================================
with tab1:
    a, b = st.columns([1.2, 1])
    with a:
        vol_dia = (
            df_f.groupby("Data")["ID"].nunique().reset_index(name="Atendimentos")
        )
        fig = px.line(vol_dia, x="Data", y="Atendimentos", markers=True)
        st.plotly_chart(fig_template(fig, "Volume diário de atendimentos"), use_container_width=True)

    with b:
        unid = (
            df_f.groupby("Unidade")["ID"].nunique().sort_values(ascending=False).head(top_n).reset_index(name="Atendimentos")
        )
        fig = px.bar(unid, x="Atendimentos", y="Unidade", orientation="h", text="Atendimentos")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} unidades por volume"), use_container_width=True)

    c, d = st.columns([1, 1.2])
    with c:
        etapa = df_f.groupby("Etapa", as_index=False)["DuracaoMin"].mean().sort_values("DuracaoMin", ascending=True)
        fig = px.bar(etapa, x="DuracaoMin", y="Etapa", orientation="h", text="DuracaoMin")
        fig.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
        st.plotly_chart(fig_template(fig, "Tempo médio por etapa"), use_container_width=True)

    with d:
        tipo = df_f.groupby(["TipoAtendimento"])["ID"].nunique().reset_index(name="Atendimentos")
        fig = px.pie(tipo, names="TipoAtendimento", values="Atendimentos", hole=0.55)
        st.plotly_chart(fig_template(fig, "Mix de tipo de atendimento"), use_container_width=True)

# =========================================================
# Tab 2
# =========================================================
with tab2:
    if simultaneos_f.empty:
        st.info("Sem granularidade suficiente para calcular ocupação simultânea com os filtros atuais.")
    else:
        a, b = st.columns([1.1, 1.1])

        heat = simultaneos_f.groupby(["Unidade", "Data"])["PacientesSimultaneos"].max().reset_index()
        heat_pivot = heat.pivot(index="Unidade", columns="Data", values="PacientesSimultaneos").fillna(0)
        fig = px.imshow(
            heat_pivot,
            aspect="auto",
            labels=dict(x="Data", y="Unidade", color="Pico"),
            text_auto=".0f",
        )
        st.plotly_chart(fig_template(fig, "Heatmap de pico de pacientes simultâneos por unidade e dia"), use_container_width=True)

        pico_hora = simultaneos_f.groupby("Hora")["PacientesSimultaneos"].mean().reset_index()
        fig2 = px.bar(pico_hora, x="Hora", y="PacientesSimultaneos", text="PacientesSimultaneos")
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig_template(fig2, "Média de pacientes simultâneos por hora"), use_container_width=True)

        c, d = st.columns([1, 1])
        heat2 = simultaneos_f.groupby(["DiaSemanaLabel", "Hora"])["PacientesSimultaneos"].mean().reset_index()
        ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        heat2["DiaSemanaLabel"] = pd.Categorical(heat2["DiaSemanaLabel"], categories=ordem, ordered=True)
        heat2 = heat2.sort_values(["DiaSemanaLabel", "Hora"])
        heat2_pivot = heat2.pivot(index="DiaSemanaLabel", columns="Hora", values="PacientesSimultaneos").fillna(0)
        fig3 = px.imshow(
            heat2_pivot,
            aspect="auto",
            labels=dict(x="Hora", y="Dia da semana", color="Pacientes"),
            text_auto=".1f"
        )
        st.plotly_chart(fig_template(fig3, "Pressão operacional média por dia da semana e hora"), use_container_width=True)

        top_picos = simultaneos_f.sort_values("PacientesSimultaneos", ascending=False).head(20).copy()
        top_picos["Momento"] = top_picos["Minuto"].dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(
            top_picos[["Unidade", "Momento", "PacientesSimultaneos"]].rename(columns={"PacientesSimultaneos": "Qtd simultânea"}),
            use_container_width=True,
            hide_index=True,
        )

# =========================================================
# Tab 3
# =========================================================
with tab3:
    a, b = st.columns([1, 1])
    with a:
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
        if not sla_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sla_df["Etapa"], y=sla_df["Tempo médio"], name="Tempo médio"))
            fig.add_trace(go.Scatter(x=sla_df["Etapa"], y=sla_df["SLA (min)"], mode="lines+markers", name="SLA"))
            st.plotly_chart(fig_template(fig, "Tempo médio x limite de SLA por etapa"), use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de SLA.")
    with b:
        if not sla_df.empty:
            fig = px.bar(sla_df.sort_values("Conformidade %"), x="Conformidade %", y="Etapa", orientation="h", text="Conformidade %")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig_template(fig, "Conformidade por etapa"), use_container_width=True)

    c, d = st.columns([1, 1])
    with c:
        box_df = df_f.copy()
        fig = px.box(box_df, x="Etapa", y="DuracaoMin", points=False)
        st.plotly_chart(fig_template(fig, "Distribuição de duração por etapa"), use_container_width=True)

    with d:
        serv = (
            df_f.groupby("Servico", as_index=False)["DuracaoMin"]
            .mean()
            .sort_values("DuracaoMin", ascending=False)
            .head(top_n)
        )
        fig = px.bar(serv, x="DuracaoMin", y="Servico", orientation="h", text="DuracaoMin")
        fig.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} serviços por tempo médio"), use_container_width=True)

    if not sla_df.empty:
        st.dataframe(
            sla_df.style.format({
                "Tempo médio": "{:.1f}",
                "Conformidade %": "{:.1f}",
                "P95 (min)": "{:.1f}"
            }),
            use_container_width=True,
            hide_index=True,
        )

# =========================================================
# Tab 4
# =========================================================
with tab4:
    oper = (
        df_f.groupby("Operador")
        .agg(
            Atendimentos=("ID", "nunique"),
            Registros=("ID", "size"),
            TempoMedio=("DuracaoMin", "mean"),
            TempoTotalMin=("DuracaoMin", "sum"),
            Unidades=("Unidade", "nunique"),
        )
        .reset_index()
    )
    if not oper.empty:
        oper = oper.sort_values(["Atendimentos", "TempoTotalMin"], ascending=[False, False])

    a, b = st.columns([1.1, 1])
    with a:
        top_oper = oper.head(top_n).sort_values("Atendimentos", ascending=True)
        fig = px.bar(top_oper, x="Atendimentos", y="Operador", orientation="h", text="Atendimentos")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} operadores por quantidade de atendimentos"), use_container_width=True)
    with b:
        top_ef = oper[oper["Atendimentos"] >= 10].sort_values("TempoMedio").head(top_n)
        if not top_ef.empty:
            fig = px.scatter(
                top_ef,
                x="Atendimentos",
                y="TempoMedio",
                size="TempoTotalMin",
                hover_name="Operador",
                text="Operador",
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig_template(fig, "Eficiência operacional | volume x tempo médio"), use_container_width=True)
        else:
            st.info("Selecione um período com mais volume para avaliar eficiência dos operadores.")

    serv_op = (
        df_f.groupby(["Operador", "Servico"])["ID"]
        .nunique()
        .reset_index(name="Atendimentos")
    )
    top_operadores = oper.head(min(top_n, max(len(oper), 1)))["Operador"].tolist()
    serv_op = serv_op[serv_op["Operador"].isin(top_operadores)]
    if not serv_op.empty:
        pivot = serv_op.pivot(index="Operador", columns="Servico", values="Atendimentos").fillna(0)
        fig = px.imshow(pivot, aspect="auto", labels=dict(x="Serviço", y="Operador", color="Qtd"))
        st.plotly_chart(fig_template(fig, "Matriz operador x serviço"), use_container_width=True)

    st.dataframe(
        oper.style.format({"TempoMedio": "{:.1f}", "TempoTotalMin": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )

# =========================================================
# Tab 5
# =========================================================
with tab5:
    base_export = df_f.copy()
    base_export["Inicio"] = base_export["Inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
    base_export["Fim"] = base_export["Fim"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(base_export, use_container_width=True, hide_index=True)
    csv = base_export.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar base filtrada em CSV",
        data=csv,
        file_name="base_filtrada_dashboard.csv",
        mime="text/csv",
    )

st.caption("Sugestão de publicação: GitHub + Streamlit Community Cloud para compartilhar por link sem expor o notebook do Colab.")

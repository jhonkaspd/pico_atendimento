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
# Estilo — identidade visual unificada (app + notebook)
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main {background-color: #08101f;}

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1324 0%, #111b31 100%);
    }

    /* ── Hero ── */
    .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 22px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 18px 40px rgba(102,126,234,0.28);
    }
    .hero h1 { margin: 0; font-size: 2rem; line-height: 1.1; }
    .hero p  { margin: 0.35rem 0 0 0; color: rgba(255,255,255,0.88); }

    /* ── Section headers (igual notebook: rosa→vermelho) ── */
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.75rem 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1.2rem 0 0.7rem 0;
        box-shadow: 0 5px 18px rgba(245,87,108,0.28);
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    /* ── Widget container (igual notebook: aqua→rosa) ── */
    .widget-container {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.1rem 1.3rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.10);
    }

    /* ── Info / warning / error boxes ── */
    .info-box {
        background: rgba(0,123,255,0.08);
        border-left: 5px solid #007bff;
        padding: 0.9rem 1rem;
        margin: 0.7rem 0;
        border-radius: 6px;
        color: #c9d9f5;
    }
    .warning-box {
        background: rgba(255,193,7,0.10);
        border-left: 5px solid #ffc107;
        color: #e0c060;
        padding: 0.9rem 1rem;
        margin: 0.7rem 0;
        border-radius: 6px;
    }

    /* ── Insight cards ── */
    .insight-card {
        padding: 0.9rem 1rem;
        border-radius: 18px;
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(118,75,162,0.30);
        min-height: 120px;
    }

    /* ── Metrics ── */
    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(12,18,34,0.95), rgba(17,27,49,0.95));
        border: 1px solid rgba(255,255,255,0.06);
        padding: 10px 14px;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }

    .small-muted { color: #95a2bf; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    "Prioridade", "Servico", "tEtapa", "Unidade"
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
# Helpers
# =========================================================
def _fmt_int(v):   return f"{int(round(v)):,}".replace(",",".")
def _fmt_float(v, casas=1):
    return f"{v:,.{casas}f}".replace(",","X").replace(".","," ).replace("X",".")
def _fmt_min(v):   return f"{_fmt_float(v, 1)} min"


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
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    df = df_raw.copy()
    faltantes = [c for c in COLUNAS_NOVA_BASE if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas ausentes na nova base: {faltantes}")

    for col in ["Bil_Emissao","Bil_ChamadaRecepcao","Bil_EncaminhaColeta",
                "Bil_ChamadaColeta","Bil_Finalizacao"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["Unidade","ID","TipoAtendimento","Operador_Recepcao",
                "Operador_Coleta","ServicoOrdem1","ServicoOrdem2"]:
        df[col] = df[col].astype(str).str.strip()

    df = df.replace({"nan": np.nan, "None": np.nan, "NaT": np.nan, "": np.nan})
    df["TipoAtendimento"] = df["TipoAtendimento"].replace({
        "Guiche":"Guichê","GUICHE":"Guichê","guiche":"Guichê","guichê":"Guichê",
        "totem":"Totem","TOTEM":"Totem",
    })
    df["Servico"] = df["ServicoOrdem2"].where(df["ServicoOrdem2"].notna(), df["ServicoOrdem1"])
    df["Servico"] = df["Servico"].fillna("Não informado")
    df["Prioridade"] = "Normal"

    etapas = []

    def add_etapa(row, nome, ini_col, fim_col, operador=None):
        ini, fim = row[ini_col], row[fim_col]
        if pd.isna(ini) or pd.isna(fim) or fim < ini:
            return
        etapas.append({
            "ID": row["ID"], "Inicio": ini, "Fim": fim, "Etapa": nome,
            "TipoAtendimento": row["TipoAtendimento"],
            "Operador": row[operador] if operador else np.nan,
            "Prioridade": row["Prioridade"], "Servico": row["Servico"],
            "tEtapa": (fim - ini).total_seconds() / 60, "Unidade": row["Unidade"],
        })

    for _, row in df.iterrows():
        tipo = row["TipoAtendimento"]
        if tipo == "Guichê":
            add_etapa(row, "1.Espera Recepção", "Bil_Emissao", "Bil_ChamadaRecepcao")
            add_etapa(row, "2.Recepção", "Bil_ChamadaRecepcao", "Bil_EncaminhaColeta", "Operador_Recepcao")
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao", "Operador_Coleta")
        else:
            add_etapa(row, "3.Espera Coleta", "Bil_EncaminhaColeta", "Bil_ChamadaColeta")
            add_etapa(row, "4.Coleta", "Bil_ChamadaColeta", "Bil_Finalizacao", "Operador_Coleta")

    df_etapas = pd.DataFrame(etapas)
    if df_etapas.empty:
        raise ValueError("A transformação não gerou etapas válidas. Verifique as colunas de data/hora.")

    ordem_etapas = {"1.Espera Recepção":1,"2.Recepção":2,"3.Espera Coleta":3,"4.Coleta":4}
    df_etapas["OrdemEtapa"] = df_etapas["Etapa"].map(ordem_etapas).fillna(99)
    df_etapas = df_etapas.sort_values(["Inicio","ID","OrdemEtapa"]).drop(columns="OrdemEtapa")
    return df_etapas[COLUNAS_OBRIGATORIAS].reset_index(drop=True)


def preprocess_data(df_raw):
    df = df_raw.copy()
    missing = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    df["Inicio"]  = pd.to_datetime(df["Inicio"], errors="coerce")
    df["Fim"]     = pd.to_datetime(df["Fim"],    errors="coerce")
    df["tEtapa"]  = pd.to_numeric(df["tEtapa"],  errors="coerce")

    df = df.dropna(subset=["ID","Inicio","Fim","Etapa","Unidade"]).copy()
    df = df[df["Fim"] >= df["Inicio"]].copy()

    df["Servico"]    = df["Servico"].replace(SERVICO_MAP)
    df["DuracaoMin"] = ((df["Fim"] - df["Inicio"]).dt.total_seconds() / 60).clip(lower=0)
    df["Data"]       = df["Inicio"].dt.date
    df["Hora"]       = df["Inicio"].dt.hour
    df = add_weekday_columns(df, "Inicio")
    df["MesRef"]     = df["Inicio"].dt.to_period("M").astype(str)
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
    exploded["Data"]   = exploded["Minuto"].dt.date
    exploded["HoraMin"]= exploded["Minuto"].dt.strftime("%H:%M")
    exploded["Hora"]   = exploded["Minuto"].dt.hour

    simultaneos = (
        exploded.groupby(["Unidade","Minuto"])["ID"]
        .nunique()
        .reset_index(name="PacientesSimultaneos")
    )
    simultaneos["Data"]   = simultaneos["Minuto"].dt.date
    simultaneos["Hora"]   = simultaneos["Minuto"].dt.hour
    simultaneos["HoraMin"]= simultaneos["Minuto"].dt.strftime("%H:%M")
    simultaneos = add_weekday_columns(simultaneos, "Minuto")
    return exploded, simultaneos


def apply_filters(df, unidades, etapas, servicos, operadores, periodo):
    out = df.copy()
    if unidades:  out = out[out["Unidade"].isin(unidades)]
    if etapas:    out = out[out["Etapa"].isin(etapas)]
    if servicos:  out = out[out["Servico"].isin(servicos)]
    if operadores: out = out[out["Operador"].isin(operadores)]
    if periodo and len(periodo) == 2:
        ini, fim = periodo
        ini = pd.to_datetime(ini)
        fim = pd.to_datetime(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        out = out[(out["Inicio"] >= ini) & (out["Inicio"] <= fim)]
    return out


def make_kpis(df_f, simultaneos_f):
    return {
        "registros":     len(df_f),
        "atendimentos":  df_f["ID"].nunique(),
        "unidades":      df_f["Unidade"].nunique(),
        "operadores":    df_f["Operador"].nunique(),
        "duracao_media": df_f["DuracaoMin"].mean(),
        "pico_max":      simultaneos_f["PacientesSimultaneos"].max() if not simultaneos_f.empty else 0,
        "hora_pico":     simultaneos_f.loc[simultaneos_f["PacientesSimultaneos"].idxmax(),"Minuto"]
                         if not simultaneos_f.empty else pd.NaT,
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
                "Limite": limite, "Media": base["DuracaoMin"].mean(),
            })
    conf_df = pd.DataFrame(conformidade).sort_values("Conformidade")
    pior_conf = conf_df.iloc[0] if not conf_df.empty else None

    if not simultaneos_f.empty:
        picos_unid = simultaneos_f.groupby("Unidade")["PacientesSimultaneos"].max().sort_values(ascending=False)
        unid_pico  = picos_unid.index[0]
        valor_pico = picos_unid.iloc[0]
        momento_pico = simultaneos_f.loc[simultaneos_f["PacientesSimultaneos"].idxmax(),"Minuto"]
    else:
        unid_pico, valor_pico, momento_pico = "-", 0, pd.NaT

    insights.append(f"**Maior gargalo médio:** {top_etapa['Etapa']} com tempo médio de **{_fmt_float(top_etapa['DuracaoMin'])} min**.")
    insights.append(f"**Maior volume:** {top_unidade} concentra **{_fmt_int(top_val)} atendimentos** no período filtrado.")
    if pior_conf is not None:
        insights.append(f"**Maior risco de SLA:** {pior_conf['Etapa']} tem conformidade de **{_fmt_float(pior_conf['Conformidade'])}%** para limite de {int(pior_conf['Limite'])} min.")
    if pd.notna(momento_pico):
        insights.append(f"**Maior pressão operacional:** pico de **{_fmt_int(valor_pico)} pacientes simultâneos** em **{unid_pico}**, às **{momento_pico.strftime('%d/%m %H:%M')}**.")
    return insights


def fig_template(fig, title=None):
    fig.update_layout(
        title=title, template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,16,31,0.35)",
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.07)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)")
    return fig


# =========================================================
# Análises de pico — funções do notebook
# =========================================================

def build_tabelas_pico(simultaneos_df):
    """
    Retorna (tabela_pico_dias, tabela_horario_pico, heatmap_total, total_por_dia)
    equivalente ao notebook.
    """
    if simultaneos_df.empty:
        return None, None, None, None

    picos_unidade_dia = (
        simultaneos_df.loc[
            simultaneos_df.groupby(["Unidade","Data"])["PacientesSimultaneos"].idxmax()
        ]
        .reset_index(drop=True)
    )

    tabela_pico_dias   = picos_unidade_dia.pivot(index="Unidade", columns="Data", values="PacientesSimultaneos")
    tabela_horario_pico = picos_unidade_dia.pivot(index="Unidade", columns="Data", values="HoraMin")

    # Total global por minuto → pico por dia
    total_por_minuto = (
        simultaneos_df.groupby("Minuto")["PacientesSimultaneos"].sum().reset_index()
    )
    total_por_minuto["Data"] = total_por_minuto["Minuto"].dt.date

    pico_total_por_dia = (
        total_por_minuto.loc[
            total_por_minuto.groupby("Data")["PacientesSimultaneos"].idxmax()
        ]
        .set_index("Data")["PacientesSimultaneos"]
    )

    heatmap_total = tabela_pico_dias.copy()
    heatmap_total.loc["Total"] = pico_total_por_dia

    return tabela_pico_dias, tabela_horario_pico, heatmap_total, pico_total_por_dia


def calcular_estatisticas_picos(unidade, tabela_horario_pico, tabela_pico_dias):
    """Pico mais cedo, mais tardio, mediana e média de horário para uma unidade."""
    if unidade not in tabela_horario_pico.index:
        return pd.Series({"Cedo":"-","Tardio":"-","Mediana":"-","Média":"-"})

    horarios_str = tabela_horario_pico.loc[unidade].dropna()
    if horarios_str.empty:
        return pd.Series({"Cedo":"-","Tardio":"-","Mediana":"-","Média":"-"})

    horarios_dt = pd.to_datetime(horarios_str, format="%H:%M")
    minutos_list = [h.hour*60+h.minute for h in horarios_dt]
    media_min = sum(minutos_list)/len(minutos_list)

    return pd.Series({
        "Cedo":    horarios_dt.sort_values().iloc[0].strftime("%H:%M"),
        "Tardio":  horarios_dt.sort_values().iloc[-1].strftime("%H:%M"),
        "Mediana": horarios_dt.sort_values().iloc[len(horarios_dt)//2].strftime("%H:%M"),
        "Média":   f"{int(media_min//60):02d}:{int(media_min%60):02d}",
    })


def extrato_pico_por_data(data_sel, simultaneos_df, exploded_df):
    """Tabela de pico por unidade + breakdown por etapa para uma data."""
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
        etapas_no_minuto = exploded_df[
            (exploded_df["Unidade"] == row["Unidade"]) &
            (exploded_df["Minuto"] == row["Horário do Pico"])
        ]["Etapa"].value_counts()
        return pd.Series({
            "1.Espera Recepção": etapas_no_minuto.get("1.Espera Recepção", 0),
            "2.Recepção":        etapas_no_minuto.get("2.Recepção", 0),
            "3.Espera Coleta":   etapas_no_minuto.get("3.Espera Coleta", 0),
            "4.Coleta":          etapas_no_minuto.get("4.Coleta", 0),
        })

    etapas_cols = picos.apply(contar_etapas, axis=1)
    out = pd.concat([picos[["Unidade","Horário do Pico_str","Qtd de Pacientes"]], etapas_cols], axis=1)
    out = out.rename(columns={"Horário do Pico_str":"Horário do Pico"})
    return out.sort_values("Unidade").reset_index(drop=True)


def calcular_resumo_operadores(df_filtrado):
    """Resumo por operador: primeira/última etapa, GAPs, conformidade."""
    tabela = []
    for operador, grupo in df_filtrado.groupby("Operador"):
        grupo = grupo.sort_values("Inicio").reset_index(drop=True)
        tempos = (grupo["Fim"] - grupo["Inicio"]).dt.total_seconds() / 60
        gaps = []
        for i in range(1, len(grupo)):
            gap = (grupo.loc[i,"Inicio"] - grupo.loc[i-1,"Fim"]).total_seconds() / 60
            if gap > 0:
                gaps.append(gap)
        tabela.append({
            "Operador": operador,
            "Hora da Primeira Etapa": grupo["Inicio"].min().strftime("%H:%M"),
            "Hora da Última Etapa":   grupo["Fim"].max().strftime("%H:%M"),
            "Qtde de Pacientes":      grupo.shape[0],
            "Tempo Médio (min)":      round(tempos.mean(), 1),
            "% Conf. Recep (≤10min)": round((tempos <= 10).mean() * 100, 1),
            "% Conf. Coleta (≤6min)": round((tempos <= 6).mean() * 100, 1),
            "Qtde de GAPs":           len(gaps),
            "Total GAPs (min)":       round(sum(gaps), 1) if gaps else 0,
            "GAP Mín (min)":          round(min(gaps), 1) if gaps else 0,
            "GAP Máx (min)":          round(max(gaps), 1) if gaps else 0,
            "GAP Médio (min)":        round(np.mean(gaps), 1) if gaps else 0,
        })
    return pd.DataFrame(tabela)


def fig_timeline_operadores(df_filtrado, unidade, data, etapa):
    """
    Retorna um gráfico Plotly de Gantt (timeline) de operadores.
    Equivalente ao matplotlib do notebook, mas interativo.
    """
    if df_filtrado.empty:
        return None

    operadores = sorted(df_filtrado["Operador"].dropna().unique())
    cores = px.colors.qualitative.Set3
    color_map = {op: cores[i % len(cores)] for i, op in enumerate(operadores)}

    fig = go.Figure()
    for op in operadores:
        sub = df_filtrado[df_filtrado["Operador"] == op]
        for _, row in sub.iterrows():
            dur_min = (row["Fim"] - row["Inicio"]).total_seconds() / 60
            label   = f"{int(dur_min)}min" if dur_min >= 1 else ""
            fig.add_trace(go.Bar(
                x=[(row["Fim"] - row["Inicio"])],
                base=[row["Inicio"]],
                y=[op],
                orientation="h",
                marker_color=color_map[op],
                marker_line_color="rgba(0,0,0,0.4)",
                marker_line_width=1,
                text=label,
                textposition="inside",
                hovertemplate=(
                    f"<b>{op}</b><br>"
                    f"Início: {row['Inicio'].strftime('%H:%M')}<br>"
                    f"Fim: {row['Fim'].strftime('%H:%M')}<br>"
                    f"Duração: {dur_min:.1f} min<br>"
                    f"ID: {row['ID']}<extra></extra>"
                ),
                showlegend=False,
            ))

    fig.update_layout(
        title=f"Timeline de Operadores — {unidade} | {etapa} | {data}",
        xaxis_type="date",
        xaxis_tickformat="%H:%M",
        barmode="overlay",
        height=max(300, len(operadores) * 45 + 120),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,16,31,0.35)",
        margin=dict(l=20, r=20, t=55, b=40),
        yaxis=dict(title="Operador", autorange="reversed"),
        xaxis=dict(title="Horário", gridcolor="rgba(255,255,255,0.07)"),
    )
    return fig


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## Fonte de dados")
    uploaded = st.file_uploader(
        "Envie a planilha de fluxo",
        type=["xlsx","xls","csv"],
        help="Use a mesma estrutura do arquivo exportado do seu processo.",
    )
    st.caption("Compartilhe o link após publicar — o código não fica exposto ao usuário final.")

# ── Hero Banner ──
st.markdown(
    """
    <div class="hero">
        <h1>📊 Dashboard de Análise de Pico de Atendimentos</h1>
        <p>Sistema inteligente de monitoramento e análise operacional — volume, capacidade, gargalos, SLA e produtividade.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded is None:
    st.info("Envie a planilha na barra lateral para carregar o dashboard.")
    st.stop()

try:
    df_raw        = load_data(uploaded)
    df_transformado = transformar_nova_base(df_raw)
    df            = preprocess_data(df_transformado)
    exploded, simultaneos = build_minute_level(df)
except Exception as e:
    st.error(f"Não foi possível processar a base: {e}")
    st.stop()

with st.sidebar:
    st.markdown("## Filtros")
    min_date = pd.to_datetime(df["Inicio"]).min().date()
    max_date = pd.to_datetime(df["Inicio"]).max().date()
    periodo  = st.date_input("Período", value=(min_date, max_date),
                              min_value=min_date, max_value=max_date)
    unidades = st.multiselect("Unidade", sorted(df["Unidade"].dropna().unique().tolist()))

df_f = apply_filters(df, unidades, [], [], [], periodo)
if df_f.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

ids         = set(df_f["ID"].unique())
exploded_f  = exploded[exploded["ID"].isin(ids)].copy()
simultaneos_f = (
    exploded_f.groupby(["Unidade","Minuto"])["ID"]
    .nunique().reset_index(name="PacientesSimultaneos")
)
if not simultaneos_f.empty:
    simultaneos_f["Data"]    = simultaneos_f["Minuto"].dt.date
    simultaneos_f["Hora"]    = simultaneos_f["Minuto"].dt.hour
    simultaneos_f["HoraMin"] = simultaneos_f["Minuto"].dt.strftime("%H:%M")
    simultaneos_f = add_weekday_columns(simultaneos_f, "Minuto")

top_n = 15

# =========================================================
# KPIs
# =========================================================
kpis = make_kpis(df_f, simultaneos_f)
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Registros",      _fmt_int(kpis["registros"]))
c2.metric("Atendimentos",   _fmt_int(kpis["atendimentos"]))
c3.metric("Unidades",       _fmt_int(kpis["unidades"]))
c4.metric("Operadores",     _fmt_int(kpis["operadores"]))
c5.metric("Tempo médio",    _fmt_min(kpis["duracao_media"]))
c6.metric("Pico simultâneo",_fmt_int(kpis["pico_max"]),
          delta=kpis["hora_pico"].strftime("%d/%m %H:%M") if pd.notna(kpis["hora_pico"]) else None)

insights = make_insights(df_f, simultaneos_f)
i1,i2,i3,i4 = st.columns(4)
for col, txt in zip([i1,i2,i3,i4], insights + [""]*max(0, 4-len(insights))):
    with col:
        st.markdown(f"<div class='insight-card'>{txt}</div>", unsafe_allow_html=True)

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Resumo Executivo",
    "🔥 Picos de Atendimento",
    "Capacidade & Heatmaps",
    "Etapas & SLA",
    "Operadores",
    "Base Filtrada",
])

# ── Tab 1: Resumo ──────────────────────────────────────────
with tab1:
    a, b = st.columns([1.2, 1])
    with a:
        vol_dia = df_f.groupby("Data")["ID"].nunique().reset_index(name="Atendimentos")
        fig = px.line(vol_dia, x="Data", y="Atendimentos", markers=True)
        st.plotly_chart(fig_template(fig, "Volume diário de atendimentos"), use_container_width=True)
    with b:
        unid = (df_f.groupby("Unidade")["ID"].nunique()
                .sort_values(ascending=False).head(top_n).reset_index(name="Atendimentos"))
        fig = px.bar(unid, x="Atendimentos", y="Unidade", orientation="h", text="Atendimentos")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} unidades por volume"), use_container_width=True)

    c, d = st.columns([1, 1.2])
    with c:
        etapa = df_f.groupby("Etapa", as_index=False)["DuracaoMin"].mean().sort_values("DuracaoMin")
        fig = px.bar(etapa, x="DuracaoMin", y="Etapa", orientation="h", text="DuracaoMin")
        fig.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
        st.plotly_chart(fig_template(fig, "Tempo médio por etapa"), use_container_width=True)
    with d:
        tipo = df_f.groupby("TipoAtendimento")["ID"].nunique().reset_index(name="Atendimentos")
        fig  = px.pie(tipo, names="TipoAtendimento", values="Atendimentos", hole=0.55)
        st.plotly_chart(fig_template(fig, "Mix de tipo de atendimento"), use_container_width=True)


# ── Tab 2: Picos de Atendimento (NOVA — equivalente ao notebook) ──
with tab2:
    st.markdown('<div class="section-header">🔥 Análise de Picos de Atendimento por Unidade</div>',
                unsafe_allow_html=True)

    tabela_pico_dias, tabela_horario_pico, heatmap_total, pico_total_por_dia = build_tabelas_pico(simultaneos_f)

    if tabela_pico_dias is None:
        st.info("Dados insuficientes para análise de picos com os filtros atuais.")
    else:
        # ── Heatmap duplo: por unidade + Total (igual notebook) ──
        st.markdown("#### Pico de Pacientes Simultâneos por Unidade e Dia")

        # Heatmap superior — por unidade
        cols_str = [str(c) for c in tabela_pico_dias.columns]
        fig_heat_unid = px.imshow(
            tabela_pico_dias.values,
            x=cols_str, y=list(tabela_pico_dias.index),
            aspect="auto", text_auto=".0f",
            color_continuous_scale="YlOrRd",
            labels=dict(x="Data", y="Unidade", color="Pico"),
        )
        fig_heat_unid.update_layout(
            title="Pico de Pacientes Simultâneos por Unidade e Dia",
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(8,16,31,0.35)", margin=dict(l=20,r=20,t=50,b=20),
            height=max(300, len(tabela_pico_dias)*38+100),
        )
        st.plotly_chart(fig_heat_unid, use_container_width=True)

        # Heatmap inferior — Total
        total_vals = [[float(pico_total_por_dia.get(c, 0)) for c in tabela_pico_dias.columns]]
        fig_heat_total = px.imshow(
            total_vals,
            x=cols_str, y=["Total"],
            aspect="auto", text_auto=".0f",
            color_continuous_scale="YlOrRd",
            labels=dict(x="Data", y="", color="Pico"),
        )
        fig_heat_total.update_layout(
            title="Total de Pacientes Simultâneos por Dia",
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(8,16,31,0.35)", margin=dict(l=20,r=20,t=45,b=20),
            height=150,
        )
        st.plotly_chart(fig_heat_total, use_container_width=True)

        # ── Tabela de horários de pico com estatísticas ──
        st.markdown('<div class="section-header">📋 Horário de Pico por Unidade — Estatísticas</div>',
                    unsafe_allow_html=True)

        estat = tabela_horario_pico.index.to_series().apply(
            lambda u: calcular_estatisticas_picos(u, tabela_horario_pico, tabela_pico_dias)
        )
        cols_dia = [str(c) for c in tabela_horario_pico.columns]
        tabela_exib = tabela_horario_pico.copy()
        tabela_exib.columns = cols_dia
        tabela_exib = pd.concat([tabela_exib, estat], axis=1).reset_index()
        tabela_exib.columns.name = None

        # Realça o dia com maior pico por unidade (vermelho claro)
        def highlight_max_day(row, pico_dias):
            unidade = row["Unidade"] if "Unidade" in row.index else row.iloc[0]
            if unidade not in pico_dias.index:
                return [""] * len(row)
            dia_max = str(pico_dias.loc[unidade].idxmax())
            styles = []
            for col in row.index:
                if col == dia_max:
                    styles.append("background-color: rgba(220,53,69,0.45); color: white; font-weight: bold")
                else:
                    styles.append("")
            return styles

        styled = tabela_exib.style.apply(
            lambda row: highlight_max_day(row, tabela_pico_dias.copy().rename(columns=str)),
            axis=1
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # ── Extrato diário interativo ──
        st.markdown('<div class="section-header">📋 Pico de Atendimento por Unidade e Distribuição da Demanda por Etapas</div>',
                    unsafe_allow_html=True)

        datas_disponiveis = sorted(simultaneos_f["Data"].unique())
        data_sel = st.selectbox(
            "Selecione a data:",
            options=datas_disponiveis,
            format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
            key="extrato_data",
        )

        extrato = extrato_pico_por_data(data_sel, simultaneos_f, exploded_f)
        if extrato.empty:
            st.warning(f"Nenhum dado encontrado para {pd.to_datetime(data_sel).strftime('%d/%m/%Y')}.")
        else:
            st.dataframe(extrato, use_container_width=True, hide_index=True)


# ── Tab 3: Capacidade & Heatmaps ──────────────────────────
with tab3:
    if simultaneos_f.empty:
        st.info("Sem granularidade suficiente para calcular ocupação simultânea com os filtros atuais.")
    else:
        pico_hora = simultaneos_f.groupby("Hora")["PacientesSimultaneos"].mean().reset_index()
        fig2 = px.bar(pico_hora, x="Hora", y="PacientesSimultaneos", text="PacientesSimultaneos")
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig_template(fig2, "Média de pacientes simultâneos por hora"), use_container_width=True)

        a, b = st.columns([1, 1])
        with a:
            heat2 = simultaneos_f.groupby(["DiaSemanaLabel","Hora"])["PacientesSimultaneos"].mean().reset_index()
            ordem = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
            heat2["DiaSemanaLabel"] = pd.Categorical(heat2["DiaSemanaLabel"], categories=ordem, ordered=True)
            heat2_pivot = heat2.sort_values(["DiaSemanaLabel","Hora"]).pivot(
                index="DiaSemanaLabel", columns="Hora", values="PacientesSimultaneos"
            ).fillna(0)
            fig3 = px.imshow(heat2_pivot, aspect="auto", text_auto=".1f",
                             labels=dict(x="Hora", y="Dia da semana", color="Pacientes"))
            st.plotly_chart(fig_template(fig3, "Pressão operacional média por dia da semana e hora"), use_container_width=True)

        with b:
            top_picos = simultaneos_f.sort_values("PacientesSimultaneos", ascending=False).head(20).copy()
            top_picos["Momento"] = top_picos["Minuto"].dt.strftime("%d/%m/%Y %H:%M")
            st.markdown("**Top 20 momentos de maior pico**")
            st.dataframe(
                top_picos[["Unidade","Momento","PacientesSimultaneos"]].rename(columns={"PacientesSimultaneos":"Qtd simultânea"}),
                use_container_width=True, hide_index=True,
            )


# ── Tab 4: Etapas & SLA ───────────────────────────────────
with tab4:
    a, b = st.columns([1, 1])
    slas = []
    for etapa_nome, limite in ETAPA_LIMITES.items():
        base = df_f[df_f["Etapa"] == etapa_nome]
        if base.empty: continue
        slas.append({
            "Etapa": etapa_nome, "SLA (min)": limite,
            "Tempo médio":   base["DuracaoMin"].mean(),
            "Conformidade %": (base["DuracaoMin"] <= limite).mean() * 100,
            "P95 (min)":     base["DuracaoMin"].quantile(0.95),
        })
    sla_df = pd.DataFrame(slas)

    with a:
        if not sla_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sla_df["Etapa"], y=sla_df["Tempo médio"], name="Tempo médio"))
            fig.add_trace(go.Scatter(x=sla_df["Etapa"], y=sla_df["SLA (min)"], mode="lines+markers", name="SLA"))
            st.plotly_chart(fig_template(fig, "Tempo médio x limite de SLA por etapa"), use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de SLA.")

    with b:
        if not sla_df.empty:
            fig = px.bar(sla_df.sort_values("Conformidade %"), x="Conformidade %", y="Etapa",
                         orientation="h", text="Conformidade %")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig_template(fig, "Conformidade por etapa"), use_container_width=True)

    c, d = st.columns([1, 1])
    with c:
        fig = px.box(df_f.copy(), x="Etapa", y="DuracaoMin", points=False)
        st.plotly_chart(fig_template(fig, "Distribuição de duração por etapa"), use_container_width=True)
    with d:
        serv = (df_f.groupby("Servico", as_index=False)["DuracaoMin"].mean()
                .sort_values("DuracaoMin", ascending=False).head(top_n))
        fig = px.bar(serv, x="DuracaoMin", y="Servico", orientation="h", text="DuracaoMin")
        fig.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} serviços por tempo médio"), use_container_width=True)

    if not sla_df.empty:
        st.dataframe(
            sla_df.style.format({"Tempo médio":"{:.1f}","Conformidade %":"{:.1f}","P95 (min)":"{:.1f}"}),
            use_container_width=True, hide_index=True,
        )


# ── Tab 5: Operadores (expandido com análises do notebook) ──
with tab5:
    st.markdown('<div class="section-header">👥 Análise de Operadores</div>', unsafe_allow_html=True)

    oper = (
        df_f.groupby("Operador")
        .agg(
            Atendimentos=("ID","nunique"),
            Registros=("ID","size"),
            TempoMedio=("DuracaoMin","mean"),
            TempoTotalMin=("DuracaoMin","sum"),
            Unidades=("Unidade","nunique"),
        )
        .reset_index()
        .sort_values(["Atendimentos","TempoTotalMin"], ascending=[False,False])
    )

    a, b = st.columns([1.1, 1])
    with a:
        top_oper = oper.head(top_n).sort_values("Atendimentos")
        fig = px.bar(top_oper, x="Atendimentos", y="Operador", orientation="h", text="Atendimentos")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig_template(fig, f"Top {top_n} operadores por quantidade de atendimentos"), use_container_width=True)
    with b:
        top_ef = oper[oper["Atendimentos"] >= 10].sort_values("TempoMedio").head(top_n)
        if not top_ef.empty:
            fig = px.scatter(top_ef, x="Atendimentos", y="TempoMedio", size="TempoTotalMin",
                             hover_name="Operador", text="Operador")
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig_template(fig, "Eficiência operacional | volume x tempo médio"), use_container_width=True)
        else:
            st.info("Selecione um período com mais volume para avaliar eficiência dos operadores.")

    # ── Matriz operador × serviço ──
    serv_op = (
        df_f.groupby(["Operador","Servico"])["ID"].nunique()
        .reset_index(name="Atendimentos")
    )
    top_operadores = oper.head(min(top_n, len(oper)))["Operador"].tolist()
    serv_op = serv_op[serv_op["Operador"].isin(top_operadores)]
    if not serv_op.empty:
        pivot = serv_op.pivot(index="Operador", columns="Servico", values="Atendimentos").fillna(0)
        fig   = px.imshow(pivot, aspect="auto", labels=dict(x="Serviço", y="Operador", color="Qtd"),
                          color_continuous_scale="Blues", text_auto=".0f")
        st.plotly_chart(fig_template(fig, "Matriz operador × serviço"), use_container_width=True)

    # ── Timeline interativa de operadores (equivalente ao notebook) ──
    st.markdown('<div class="section-header">🕐 Timeline de Operadores por Etapa e Data</div>',
                unsafe_allow_html=True)

    col_u, col_d, col_e = st.columns(3)
    with col_u:
        unidades_disp = sorted(df_f["Unidade"].dropna().unique())
        unid_sel = st.selectbox("Unidade", unidades_disp, key="tl_unidade")
    with col_d:
        datas_disp = sorted(df_f["Data"].unique())
        data_sel_tl = st.selectbox("Data", datas_disp,
                                   format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
                                   key="tl_data")
    with col_e:
        etapas_disp = sorted(df_f["Etapa"].dropna().unique())
        etapa_sel   = st.selectbox("Etapa", etapas_disp, key="tl_etapa")

    df_tl = df_f[
        (df_f["Unidade"] == unid_sel) &
        (df_f["Etapa"]   == etapa_sel) &
        (df_f["Data"]    == data_sel_tl) &
        df_f["Operador"].notna()
    ].copy()

    if df_tl.empty:
        st.info("Nenhum dado encontrado para essa combinação de filtros.")
    else:
        fig_tl = fig_timeline_operadores(df_tl, unid_sel, data_sel_tl, etapa_sel)
        if fig_tl:
            st.plotly_chart(fig_tl, use_container_width=True)

        # ── Tabela resumo por operador (igual notebook) ──
        st.markdown("**📋 Resumo por Operador**")
        resumo_op = calcular_resumo_operadores(df_tl)
        if not resumo_op.empty:
            st.dataframe(resumo_op.style.format({
                "Tempo Médio (min)":"{:.1f}",
                "% Conf. Recep (≤10min)":"{:.1f}",
                "% Conf. Coleta (≤6min)":"{:.1f}",
                "Total GAPs (min)":"{:.1f}",
                "GAP Mín (min)":"{:.1f}",
                "GAP Máx (min)":"{:.1f}",
                "GAP Médio (min)":"{:.1f}",
            }), use_container_width=True, hide_index=True)

        # ── Matriz operador × serviço para o filtro selecionado ──
        if "Servico" in df_tl.columns:
            st.markdown("**📊 Resumo por Operador e Serviço**")
            cruzada = pd.crosstab(df_tl["Operador"], df_tl["Servico"], margins=True, margins_name="TOTAL")
            st.dataframe(cruzada, use_container_width=True)

    # Tabela geral
    st.markdown("**Tabela geral de operadores**")
    st.dataframe(
        oper.style.format({"TempoMedio":"{:.1f}","TempoTotalMin":"{:.1f}"}),
        use_container_width=True, hide_index=True,
    )


# ── Tab 6: Base Filtrada ─────────────────────────────────
with tab6:
    base_export = df_f.copy()
    base_export["Inicio"] = base_export["Inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
    base_export["Fim"]    = base_export["Fim"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(base_export, use_container_width=True, hide_index=True)
    csv = base_export.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar base filtrada em CSV", data=csv,
        file_name="base_filtrada_dashboard.csv", mime="text/csv",
    )

st.caption("Publicação sugerida: GitHub + Streamlit Community Cloud para compartilhar por link sem expor o código.")
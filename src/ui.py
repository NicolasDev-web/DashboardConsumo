from __future__ import annotations

import html
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .constants import COLORS


def inject_mrv_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
          --mrv-green-900: {COLORS['green_900']};
          --mrv-green-700: {COLORS['green_700']};
          --mrv-green-500: {COLORS['green_500']};
          --mrv-text: {COLORS['text']};
          --mrv-surface-subtle: {COLORS['surface_subtle']};
          --mrv-border: {COLORS['border']};
        }}

        html, body, [class*="css"] {{ font-family: Averta, Manrope, "Avenir Next", Arial, sans-serif; }}
        .stApp {{ background: #F8FBF9; color: var(--mrv-text); }}
        [data-testid="stHeader"] {{ background: rgba(248, 251, 249, .92); }}
        [data-testid="stToolbar"] {{ visibility: hidden; height: 0; }}
        [data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid var(--mrv-border); }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{ color: var(--mrv-green-900); }}
        h1, h2, h3 {{ color: var(--mrv-text); letter-spacing: -0.025em; }}
        h1 {{ font-weight: 700; }}
        h2, h3 {{ font-weight: 600; }}

        .block-container {{ max-width: 1480px; padding-top: 1.6rem; padding-bottom: 3rem; }}
        .mrv-hero {{
          position: relative; overflow: hidden; min-height: 172px;
          padding: 28px 32px; margin-bottom: 24px; border-radius: 16px;
          background: var(--mrv-green-900); color: white;
        }}
        .mrv-hero::after {{
          content: ""; position: absolute; width: 230px; height: 230px;
          right: -58px; top: -78px; border: 34px solid rgba(130,234,91,.32);
          transform: rotate(20deg); border-radius: 54% 46% 58% 42%;
        }}
        .mrv-hero::before {{
          content: ""; position: absolute; width: 120px; height: 120px;
          right: 118px; bottom: -76px; background: rgba(0,211,141,.28);
          transform: rotate(34deg); border-radius: 22px;
        }}
        .mrv-hero h1 {{ color: white; font-size: clamp(2rem, 3vw, 3rem); margin: 0 0 10px; max-width: 760px; }}
        .mrv-hero p {{ color: rgba(255,255,255,.84); margin: 0; max-width: 760px; line-height: 1.55; }}
        .mrv-hero .meta {{ margin-top: 22px; font-size: .82rem; color: #CBEBDD; }}

        .mrv-section-title {{ margin: 12px 0 2px; font-size: 1.35rem; font-weight: 700; color: var(--mrv-text); }}
        .mrv-section-copy {{ margin: 0 0 14px; color: {COLORS['muted']}; font-size: .92rem; }}

        .mrv-kpi {{
          min-height: 124px; padding: 20px; background: #FFFFFF;
          border: 1px solid var(--mrv-border); border-top: 4px solid var(--mrv-green-900);
          border-radius: 12px;
        }}
        .mrv-kpi .label {{ color: {COLORS['muted']}; font-size: .84rem; margin-bottom: 12px; }}
        .mrv-kpi .value {{ color: var(--mrv-text); font-size: 1.9rem; line-height: 1; font-weight: 700; }}
        .mrv-kpi .note {{ color: {COLORS['muted']}; font-size: .76rem; margin-top: 10px; }}
        .mrv-kpi.stock {{ border-top-color: {COLORS['stock']}; }}
        .mrv-kpi.consumption {{ border-top-color: var(--mrv-green-500); }}

        .mrv-empty {{
          padding: 32px; border: 1px dashed #A9BDB5; border-radius: 12px;
          background: #FFFFFF; color: var(--mrv-text);
        }}
        .mrv-note {{
          padding: 14px 16px; border-left: 4px solid {COLORS['orange']};
          background: #FFF9E6; color: #5C4A00; border-radius: 0 8px 8px 0;
        }}
        .mrv-status-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--mrv-green-500); margin-right:8px; }}
        .mrv-breadcrumb {{
          margin: 8px 0 16px; color: {COLORS['muted']}; font-size: .84rem;
        }}
        .mrv-breadcrumb span {{ color: #A1B0AA; padding: 0 7px; }}
        .mrv-map-legend {{
          display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center;
          margin: 10px 0 2px; padding: 12px 14px; background: #FFFFFF;
          border: 1px solid var(--mrv-border); border-radius: 8px;
          color: {COLORS['text']}; font-size: .82rem;
        }}
        .mrv-map-legend span {{ display: inline-flex; gap: 7px; align-items: center; }}
        .mrv-map-legend i {{ display: inline-block; width: 14px; height: 14px; border-radius: 3px; }}
        .mrv-map-legend i.sold {{ background: var(--mrv-green-900); }}
        .mrv-map-legend i.stock {{ background: #DCE2DF; border: 1px solid #A8B6B0; }}
        .mrv-map-legend i.conflict {{ background: #FFFFFF; border: 3px solid {COLORS['orange']}; }}

        div[data-testid="stMetric"] {{ background:#FFFFFF; border:1px solid var(--mrv-border); padding:16px; border-radius:12px; }}
        div[data-testid="stDataFrame"] {{ border: 1px solid var(--mrv-border); border-radius: 10px; overflow: hidden; }}
        .stButton > button, .stDownloadButton > button {{ border-radius:8px; border:1px solid var(--mrv-green-900); min-height:40px; }}
        .stButton > button[kind="primary"] {{ background:var(--mrv-green-900); color:white; }}
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
        input:focus-visible, [role="combobox"]:focus-visible {{ outline:3px solid var(--mrv-green-500)!important; outline-offset:2px; }}
        [data-baseweb="select"] > div {{ border-radius:8px; }}
        hr {{ border-color: var(--mrv-border); }}

        @media (max-width: 760px) {{
          .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
          .mrv-hero {{ padding: 24px 20px; min-height: 190px; }}
          .mrv-hero::after {{ opacity: .55; }}
        }}
        @media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto!important; transition: none!important; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(snapshot_label: str) -> None:
    st.markdown(
        f"""
        <section class="mrv-hero">
          <h1>Consumo e estoque imobiliário</h1>
          <p>Leitura comercial do portfólio por empreendimento, bloco e andar. Consumo representa vendas observadas, não a demanda total de mercado.</p>
          <div class="meta"><span class="mrv-status-dot"></span>Snapshot ativo: {html.escape(snapshot_label)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, copy: str = "") -> None:
    st.markdown(f'<div class="mrv-section-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if copy:
        st.markdown(f'<div class="mrv-section-copy">{html.escape(copy)}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, note: str, variant: str = "") -> None:
    st.markdown(
        f"""
        <div class="mrv-kpi {html.escape(variant)}">
          <div class="label">{html.escape(label)}</div>
          <div class="value">{html.escape(value)}</div>
          <div class="note">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str) -> None:
    st.markdown(
        f'<div class="mrv-empty"><strong>{html.escape(title)}</strong><br>{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def br_int(value: int | float) -> str:
    return f"{int(value):,}".replace(",", ".")


def br_pct(value: float | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n.d."
    return f"{value * 100:.{decimals}f}%".replace(".", ",")


def plotly_layout(fig: go.Figure, height: int = 370, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Averta, Manrope, Arial", "color": COLORS["text"], "size": 12},
        margin=margin or {"l": 12, "r": 12, "t": 34, "b": 16},
        hoverlabel={"bgcolor": "#FFFFFF", "font_color": COLORS["text"]},
        separators=",.",
        legend={"orientation": "h", "y": 1.08, "x": 0},
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["border"])
    fig.update_yaxes(gridcolor="#E6EEEA", zeroline=False, linecolor=COLORS["border"])
    return fig


def sorted_unique(values: Iterable) -> list[str]:
    return sorted(str(value) for value in pd.Series(values).dropna().unique())

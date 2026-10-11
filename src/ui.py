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

        .block-container {{ max-width: 1480px; padding-top: 3.4rem; padding-bottom: 3rem; }}
        .mrv-header {{ margin: 0 0 18px; }}
        .mrv-header .eyebrow {{ color: {COLORS['muted']}; font-size: .82rem; margin-bottom: 6px; }}
        .mrv-header h1 {{ color: var(--mrv-green-900); font-size: clamp(1.6rem, 2.4vw, 2.1rem); margin: 0; padding: 0; line-height: 1.2; }}

        .mrv-insight {{
          padding: 20px 24px; margin: 0 0 18px; background: #FFFFFF;
          border: 1px solid var(--mrv-border); border-left: 6px solid var(--mrv-green-900);
          border-radius: 12px;
        }}
        .mrv-insight.attention {{ border-left-color: {COLORS['orange']}; }}
        .mrv-insight.positive {{ border-left-color: var(--mrv-green-500); }}
        .mrv-insight .headline {{ font-size: 1.22rem; line-height: 1.45; color: var(--mrv-text); }}
        .mrv-insight .headline strong {{ color: var(--mrv-green-900); }}
        .mrv-insight .detail {{ margin-top: 8px; color: {COLORS['muted']}; font-size: .92rem; line-height: 1.5; }}

        .mrv-strip {{
          display: flex; flex-wrap: wrap; gap: 8px 22px; padding: 12px 16px; margin: 4px 0 14px;
          background: #FFFFFF; border: 1px solid var(--mrv-border); border-radius: 10px; font-size: .9rem;
        }}
        .mrv-strip span {{ color: {COLORS['muted']}; }}
        .mrv-strip strong {{ color: var(--mrv-text); font-size: 1.02rem; margin-right: 4px; }}

        .mrv-share {{ display: grid; gap: 14px; padding: 18px 20px; background: #FFFFFF; border: 1px solid var(--mrv-border); border-radius: 12px; }}
        .mrv-share .row-top {{ display: flex; justify-content: space-between; gap: 12px; font-size: .95rem; }}
        .mrv-share .row-top b {{ color: var(--mrv-text); }}
        .mrv-share .row-top span {{ color: var(--mrv-text); white-space: nowrap; }}
        .mrv-share .track {{ height: 10px; margin: 6px 0 4px; background: #EEF3F1; border-radius: 6px; overflow: hidden; }}
        .mrv-share .fill {{ height: 100%; border-radius: 6px; }}
        .mrv-share .help {{ color: {COLORS['muted']}; font-size: .78rem; }}

        .mrv-performance {{ display:grid; gap:16px; }}
        .mrv-performance > div {{ padding:16px 18px; background:#FFFFFF; border:1px solid var(--mrv-border); border-radius:10px; }}
        .mrv-performance h4 {{ margin:0 0 10px; color:var(--mrv-text); font-size:.98rem; }}
        .mrv-performance ol {{ margin:0; padding:0; list-style:none; display:grid; gap:9px; }}
        .mrv-performance li {{ display:flex; justify-content:space-between; gap:12px; padding-top:9px; border-top:1px solid #E8EFEC; font-size:.86rem; }}
        .mrv-performance li:first-child {{ padding-top:0; border-top:0; }}
        .mrv-performance li span {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
        .mrv-performance li strong {{ color:var(--mrv-green-900); white-space:nowrap; font-size:.82rem; }}

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
        .mrv-kpi.attention {{ border-top-color: {COLORS['orange']}; }}

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
          .mrv-insight {{ padding: 16px 18px; }}
          .mrv-insight .headline {{ font-size: 1.08rem; }}
          .mrv-performance li {{ display:block; }}
          .mrv-performance li strong {{ display:block; margin-top:3px; }}
        }}
        @media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto!important; transition: none!important; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, snapshot_label: str) -> None:
    st.markdown(
        f"""
        <header class="mrv-header">
          <div class="eyebrow"><span class="mrv-status-dot"></span>Consumo e estoque · dados de {html.escape(snapshot_label)}</div>
          <h1>{html.escape(title)}</h1>
        </header>
        """,
        unsafe_allow_html=True,
    )


def strong(text: str) -> str:
    return f"<strong>{html.escape(str(text))}</strong>"


def insight(headline_html: str, detail_html: str = "", tone: str = "") -> None:
    """Frase de conclusão da tela. Os argumentos já devem chegar escapados."""
    detail = f'<div class="detail">{detail_html}</div>' if detail_html else ""
    st.markdown(
        f'<div class="mrv-insight {html.escape(tone)}"><div class="headline">{headline_html}</div>{detail}</div>',
        unsafe_allow_html=True,
    )


def summary_strip(items: list[tuple[str, str]]) -> None:
    """Resumo em linha (valor, rótulo), usado onde cards repetiriam informação."""
    body = "".join(f"<div><strong>{html.escape(value)}</strong><span>{html.escape(label)}</span></div>" for value, label in items)
    st.markdown(f'<div class="mrv-strip">{body}</div>', unsafe_allow_html=True)


def share_bars(rows: list[dict]) -> None:
    """Barras de participação: label, value, share (0–1), color e help opcionais."""
    parts = []
    for row in rows:
        share = 0 if row["share"] is None or pd.isna(row["share"]) else row["share"]
        width = max(share * 100, 0.8) if row["value"] else 0
        help_text = f'<div class="help">{html.escape(row["help"])}</div>' if row.get("help") else ""
        parts.append(
            f'<div><div class="row-top"><b>{html.escape(row["label"])}</b>'
            f'<span>{html.escape(br_int(row["value"]))} · {html.escape(br_pct(row["share"], 0))}</span></div>'
            f'<div class="track"><div class="fill" style="width:{width:.1f}%;background:{row["color"]}"></div></div>'
            f"{help_text}</div>"
        )
    st.markdown(f'<div class="mrv-share">{"".join(parts)}</div>', unsafe_allow_html=True)


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


def br_pp(difference: float) -> str:
    """Diferença entre duas proporções em pontos percentuais, com sentido explícito."""
    points = abs(difference) * 100
    if points < 0.05:
        return "igual à"
    direction = "acima da" if difference > 0 else "abaixo da"
    return f"{points:.1f} p.p. {direction}".replace(".", ",", 1)


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

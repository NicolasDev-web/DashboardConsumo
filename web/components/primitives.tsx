"use client";

import type { ReactNode } from "react";

import { integer, pct } from "@/lib/format";
import { isSensiaEnterprise } from "@/lib/brand";
import type { Kpis } from "@/lib/types";

export function Icon({ name }: { name: "overview" | "blocks" | "enterprise" | "velocity" | "quality" | "filter" | "download" | "expand" | "collapse" }) {
  const paths: Record<string, ReactNode> = {
    overview: <><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" /></>,
    blocks: <><path d="M4 19V9l5-4 5 4v10M14 19V6l3-2 3 2v13M2 20h20" /></>,
    enterprise: <><path d="M5 20V5h14v15M9 9h2M15 9h-2M9 13h2M15 13h-2M10 20v-3h4v3" /></>,
    velocity: <><path d="M4 18l5-6 4 3 7-9M16 6h4v4" /></>,
    quality: <><path d="M12 3l8 4v5c0 5-3.4 8-8 9-4.6-1-8-4-8-9V7zM8.5 12l2.2 2.2 4.8-5" /></>,
    filter: <><path d="M4 5h16M7 12h10M10 19h4" /></>,
    download: <><path d="M12 3v12M7 10l5 5 5-5M5 21h14" /></>,
    expand: <><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></>,
    collapse: <><path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" /></>,
  };
  return <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>;
}

export function Insight({ children, detail, tone = "default" }: { children: ReactNode; detail?: ReactNode; tone?: "default" | "positive" | "attention" }) {
  return <section className={`insight insight-${tone}`}><p>{children}</p>{detail ? <span>{detail}</span> : null}</section>;
}

export function BrandBadge({ name }: { name: string }) {
  return isSensiaEnterprise(name) ? <span className="brand-badge">Sensia</span> : null;
}

export function EnterpriseLabel({ name }: { name: string }) {
  return <span className="enterprise-label"><span>{name}</span><BrandBadge name={name} /></span>;
}

export function SummaryStrip({ items }: { items: Array<{ value: ReactNode; label: ReactNode }> }) {
  return <div className="summary-strip">{items.map((item, index) => <div key={index}><strong>{item.value}</strong><span>{item.label}</span></div>)}</div>;
}

export function SectionHeader({ title, copy, action }: { title: string; copy?: string; action?: ReactNode }) {
  return <div className="section-header"><div><h2>{title}</h2>{copy ? <p>{copy}</p> : null}</div>{action}</div>;
}

export function MetricToggle({ options, value, onChange, label = "Comparar por" }: { options: string[]; value: string; onChange: (value: string) => void; label?: string }) {
  return <div className="metric-toggle" role="group" aria-label={label}>{options.map((option) => <button type="button" key={option} className={value === option ? "active" : ""} aria-pressed={value === option} onClick={() => onChange(option)}>{option}</button>)}</div>;
}

export function ExpandButton({ expanded, label, onClick }: { expanded: boolean; label: string; onClick: () => void }) {
  return <button type="button" className="expand-button" onClick={onClick} aria-label={expanded ? "Sair da tela cheia" : `Abrir ${label} em tela cheia`}><Icon name={expanded ? "collapse" : "expand"} /><span>{expanded ? "Sair da tela cheia" : "Tela cheia"}</span></button>;
}

type BarItem = {
  id: string;
  label: ReactNode;
  value: number;
  valueLabel: string;
  detail?: string;
  tone?: "green" | "orange" | "neutral";
};

export function BarList({ items, onSelect, selected }: { items: BarItem[]; onSelect?: (id: string) => void; selected?: string }) {
  const max = Math.max(1, ...items.map((item) => item.value));
  return <div className="bar-list">{items.map((item) => {
    const width = item.value <= 0 ? 0 : Math.max(2, item.value / max * 100);
    const content = <><div className="bar-heading"><strong>{item.label}</strong><span>{item.valueLabel}</span></div><div className="bar-track" aria-hidden="true"><span className={`bar-fill ${item.tone ?? "green"}`} style={{ width: `${width}%` }} /></div>{item.detail ? <small>{item.detail}</small> : null}</>;
    return onSelect ? <button type="button" key={item.id} className={`bar-row ${selected === item.id ? "selected" : ""}`} aria-pressed={selected === item.id} onClick={() => onSelect(item.id)}>{content}</button> : <div key={item.id} className="bar-row">{content}</div>;
  })}</div>;
}

export function StockComposition({ groups }: { groups: Array<{ group: string; units: number; share: number }> }) {
  const colors: Record<string, string> = { "Em comercialização": "#079D56", Reservadas: "#FFB719", "Fora de venda": "#62766F", "Outros status": "#793F98" };
  return <div className="stock-composition">{groups.map((group) => <div key={group.group}><div><strong>{integer.format(group.units)}</strong><span>{group.group}</span><em>{pct(group.share, 0)} do estoque</em></div><div className="share-track"><span style={{ width: `${group.share * 100}%`, background: colors[group.group] }} /></div></div>)}</div>;
}

export function KpiSummary({ kpis }: { kpis: Kpis }) {
  return <SummaryStrip items={[
    { value: `${integer.format(kpis.sold)} vendidas`, label: `de ${integer.format(kpis.total)} unidades` },
    { value: `${integer.format(kpis.stock)} não vendidas`, label: "estoque atual" },
    { value: pct(kpis.consumption), label: "percentual vendido" },
  ]} />;
}

export function Loading({ label = "Preparando a leitura dos dados" }: { label?: string }) {
  return <div className="loading" role="status" aria-live="polite"><span aria-hidden="true" /><p>{label}</p></div>;
}

export function Empty({ title, copy }: { title: string; copy: string }) {
  return <div className="empty"><strong>{title}</strong><p>{copy}</p></div>;
}

export function TableShell({ children }: { children: ReactNode }) {
  return <div className="table-shell">{children}</div>;
}

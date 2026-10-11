"use client";

import { useEffect, useState } from "react";

import { Insight, Loading, SectionHeader, TableShell } from "@/components/primitives";
import { integer, pct } from "@/lib/format";
import type { DashboardData, FilterState } from "@/lib/types";

type QualityResponse = { total: number; rows: Array<Record<string, string | number | null>> };

function appendFilters(params: URLSearchParams, filters: FilterState) {
  params.set("date", filters.date);
  filters.cities.forEach((value) => params.append("city", value));
  filters.typologies.forEach((value) => params.append("typology", value));
  filters.statuses.forEach((value) => params.append("status", value));
}

export default function QualityView({ data, filters }: { data: DashboardData; filters: FilterState }) {
  const [issue, setIssue] = useState(data.quality.issues[0]?.key ?? "floorMissing");
  const [detail, setDetail] = useState<QualityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!data.quality.issues.some((item) => item.key === issue)) setIssue(data.quality.issues[0]?.key ?? "floorMissing");
  }, [data, issue]);
  useEffect(() => {
    if (!issue) return;
    const controller = new AbortController();
    const params = new URLSearchParams({ issue, limit: "200" });
    appendFilters(params, filters);
    setLoading(true);
    fetch(`/api/quality?${params}`, { signal: controller.signal }).then((response) => response.json()).then(setDetail).catch((error) => { if (error.name !== "AbortError") setDetail(null); }).finally(() => setLoading(false));
    return () => controller.abort();
  }, [issue, filters]);
  const top = data.quality.issues[0];
  return <div className="view-stack"><Insight tone={data.quality.cleanShare >= .95 ? "positive" : "attention"} detail={top ? `O ponto mais frequente é ${top.label.toLowerCase()} (${integer.format(top.count)} registros).` : undefined}><strong>{pct(data.quality.cleanShare)}</strong> dos registros não têm alertas. Os alertas não alteram os totais de vendas.</Insight>{data.quality.issues.length ? <section className="panel"><SectionHeader title="O que precisa de conferência" copy="Escolha um alerta para ver os registros relacionados." /><div className="issue-grid">{data.quality.issues.map((item) => <button key={item.key} className={issue === item.key ? "active" : ""} onClick={() => setIssue(item.key)}><span>{item.label}</span><strong>{integer.format(item.count)}</strong><small>{pct(item.share, 2)} do recorte</small></button>)}</div><div className="quality-detail"><h3>{data.quality.issues.find((item) => item.key === issue)?.label}</h3>{loading ? <Loading label="Carregando registros" /> : detail ? <><p>Mostrando até 200 de {integer.format(detail.total)} registros.</p><TableShell><table><thead><tr><th>Cidade</th><th>Empreendimento</th><th>Bloco</th><th>Unidade</th><th>Andar</th><th>Status oficial</th></tr></thead><tbody>{detail.rows.map((row) => <tr key={String(row.unitId)}><td>{row.city}</td><td>{row.enterprise}</td><td>{row.block}</td><td>{row.unit}</td><td>{row.floor ?? "—"}</td><td>{row.status}</td></tr>)}</tbody></table></TableShell></> : <p>Não foi possível carregar os registros.</p>}</div></section> : <section className="panel"><SectionHeader title="Nenhum alerta encontrado" copy="Todos os registros do recorte passaram pelas verificações atuais." /></section>}</div>;
}

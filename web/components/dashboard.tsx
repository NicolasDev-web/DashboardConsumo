"use client";

import { useEffect, useMemo, useState } from "react";

import BlocksView from "@/components/blocks-view";
import EnterpriseView from "@/components/enterprise-view";
import Filters from "@/components/filters";
import OverviewView from "@/components/overview-view";
import { Icon, Loading } from "@/components/primitives";
import QualityView from "@/components/quality-view";
import VelocityView from "@/components/velocity-view";
import { dateLabel } from "@/lib/format";
import type { DashboardData, EnterpriseData, FilterState, PageId, VelocityData } from "@/lib/types";

const NAVIGATION: Array<{ id: PageId; label: string; title: string }> = [
  { id: "overview", label: "Visão geral", title: "Como estão as vendas do portfólio?" },
  { id: "blocks", label: "Blocos e prumadas", title: "Como estão as vendas por bloco e prumada?" },
  { id: "enterprise", label: "Empreendimento", title: "Como está este empreendimento?" },
  { id: "velocity", label: "Velocidade", title: "Em que ritmo estamos vendendo?" },
  { id: "quality", label: "Qualidade dos dados", title: "Posso confiar nestes dados?" },
];

function paramsFor(filters: FilterState) {
  const params = new URLSearchParams();
  if (filters.date) params.set("date", filters.date);
  filters.cities.forEach((value) => params.append("city", value));
  filters.typologies.forEach((value) => params.append("typology", value));
  filters.statuses.forEach((value) => params.append("status", value));
  return params;
}

export default function Dashboard() {
  const [page, setPage] = useState<PageId>("overview");
  const [filters, setFilters] = useState<FilterState>({ date: "", cities: [], typologies: [], statuses: [] });
  const [data, setData] = useState<DashboardData | null>(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [error, setError] = useState("");
  const [enterpriseId, setEnterpriseId] = useState("");
  const [enterpriseBlocks, setEnterpriseBlocks] = useState<string[]>([]);
  const [enterprise, setEnterprise] = useState<EnterpriseData | null>(null);
  const [enterpriseLoading, setEnterpriseLoading] = useState(false);
  const [velocity, setVelocity] = useState<VelocityData | null>(null);
  const [velocityLoading, setVelocityLoading] = useState(false);
  const query = useMemo(() => paramsFor(filters).toString(), [filters]);

  useEffect(() => {
    const controller = new AbortController();
    setDashboardLoading(true);
    fetch(`/api/dashboard${query ? `?${query}` : ""}`, { signal: controller.signal })
      .then(async (response) => { const payload = await response.json(); if (!response.ok) throw new Error(payload.error); return payload as DashboardData; })
      .then((payload) => {
        setData(payload);
        setError("");
        if (!filters.date) setFilters((current) => ({ ...current, date: payload.meta.snapshotDate }));
        setEnterprise((current) => current && payload.options.enterprises.some((item) => item.id === current.enterprise.id) ? current : null);
        setEnterpriseId((current) => payload.options.enterprises.some((item) => item.id === current) ? current : payload.options.enterprises[0]?.id ?? "");
      })
      .catch((reason) => { if (reason.name !== "AbortError") setError(reason.message ?? "Não foi possível carregar o dashboard."); })
      .finally(() => { if (!controller.signal.aborted) setDashboardLoading(false); });
    return () => controller.abort();
  }, [query, filters.date]);

  useEffect(() => {
    if (!enterpriseId || !["blocks", "enterprise"].includes(page)) return;
    const controller = new AbortController();
    const params = paramsFor(filters);
    params.set("enterprise", enterpriseId);
    if (page === "enterprise") enterpriseBlocks.forEach((block) => params.append("block", block));
    setEnterpriseLoading(true);
    fetch(`/api/enterprise?${params}`, { signal: controller.signal })
      .then(async (response) => { const payload = await response.json(); if (!response.ok) throw new Error(payload.error); return payload as EnterpriseData; })
      .then((payload) => { setEnterprise(payload); setError(""); })
      .catch((reason) => { if (reason.name !== "AbortError") setError(reason.message ?? "Não foi possível carregar o empreendimento."); })
      .finally(() => { if (!controller.signal.aborted) setEnterpriseLoading(false); });
    return () => controller.abort();
  }, [enterpriseId, enterpriseBlocks, filters, page]);

  useEffect(() => {
    if (page !== "velocity" || velocity) return;
    const controller = new AbortController();
    setVelocityLoading(true);
    fetch("/api/velocity", { signal: controller.signal })
      .then(async (response) => { const payload = await response.json(); if (!response.ok) throw new Error(payload.error); return payload as VelocityData; })
      .then(setVelocity)
      .catch((reason) => { if (reason.name !== "AbortError") setVelocity(null); })
      .finally(() => { if (!controller.signal.aborted) setVelocityLoading(false); });
    return () => controller.abort();
  }, [page, velocity]);

  const active = NAVIGATION.find((item) => item.id === page)!;
  const clearFilters = () => setFilters((current) => ({ date: current.date, cities: [], typologies: [], statuses: [] }));
  const changeEnterprise = (value: string) => {
    setEnterpriseBlocks([]);
    setEnterprise(null);
    setEnterpriseId(value);
  };

  return <div className="app-shell">
    <a className="skip-link" href="#dashboard-content">Pular para o conteúdo</a>
    <aside className="sidebar">
      <div className="brand">
        <img className="brand-logo-full" src="/brand/mrv-logo-white.png" alt="MRV" />
        <img className="brand-logo-symbol" src="/brand/mrv-symbol.png" alt="" aria-hidden="true" />
        <div><strong>Consumo & estoque</strong><small>Gestão comercial</small></div>
      </div>
      <nav aria-label="Navegação principal">{NAVIGATION.map((item) => <button type="button" key={item.id} className={page === item.id ? "active" : ""} aria-current={page === item.id ? "page" : undefined} data-label={item.label} onClick={() => setPage(item.id)}><Icon name={item.id} /><span>{item.label}</span></button>)}</nav>
      <div className="sidebar-foot"><span>Aplicação web</span><small>Dados preparados localmente</small></div>
    </aside>
    <main id="dashboard-content" tabIndex={-1}>
      <header className="topbar"><div><h1>{active.title}</h1><p>{data ? `Dados de ${dateLabel(data.meta.snapshotDate)}` : "Carregando a base"}</p></div>{data ? <span className={`data-pill${dashboardLoading ? " updating" : ""}`} role="status" aria-live="polite">{dashboardLoading ? "Atualizando dados…" : `${data.meta.scopeRows.toLocaleString("pt-BR")} registros no recorte`}</span> : null}</header>
      {data ? <Filters filters={filters} options={data.options} onChange={setFilters} onClear={clearFilters} /> : null}
      <div className="content" aria-busy={dashboardLoading}>
        {error ? <div className="error-banner" role="alert"><strong>Não foi possível continuar</strong><span>{error}</span></div> : null}
        {dashboardLoading && !data ? <Loading /> : data ? <>
          {page === "overview" ? <OverviewView data={data} /> : null}
          {page === "blocks" ? <BlocksView options={data.options.enterprises} enterpriseId={enterpriseId} onEnterpriseChange={changeEnterprise} data={enterprise} loading={enterpriseLoading} /> : null}
          {page === "enterprise" ? <EnterpriseView options={data.options.enterprises} enterpriseId={enterpriseId} onEnterpriseChange={changeEnterprise} selectedBlocks={enterpriseBlocks} onSelectedBlocksChange={setEnterpriseBlocks} data={enterprise} loading={enterpriseLoading} /> : null}
          {page === "velocity" ? <VelocityView data={velocity} loading={velocityLoading} /> : null}
          {page === "quality" ? <QualityView data={data} filters={filters} /> : null}
        </> : null}
      </div>
    </main>
  </div>;
}

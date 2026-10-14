"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { BarList, BrandBadge, Empty, ExpandButton, Insight, Loading, MetricToggle, SectionHeader, SummaryStrip, TableShell } from "@/components/primitives";
import { csvDownload, integer, pct } from "@/lib/format";
import type { EnterpriseData, EnterpriseOption, UnitDetail } from "@/lib/types";

const STATUS_CODES: Record<string, string> = {
  VENDIDO: "VD",
  "EXCLUSIVO PLATAFORMA": "EX",
  "NÃO LANÇADO": "NL",
  "PRÉ VENDA": "PV",
  PERMUTADO: "PM",
  BLOQUEADO: "BL",
  "RESERVADO COM CONTRATO PRE ATIVO": "RC",
  LANÇADO: "LA",
  "RESERVA PARA PERMUTA": "RP",
  RESERVADO: "RE",
};

type HeatmapScope = "Menos vendidos" | "Mais vendidos" | "Todos";
type MirrorMode = "Vendida ou não" | "Status detalhado";
type Screen = "summary" | "ranking" | "heatmap" | "building";

const SCREENS: Array<{ id: Screen; label: string; title: string }> = [
  { id: "summary", label: "Resumo", title: "Resumo do empreendimento" },
  { id: "ranking", label: "Blocos", title: "Quais blocos venderam mais?" },
  { id: "heatmap", label: "Prumadas", title: "Como as prumadas se comparam?" },
  { id: "building", label: "Espelho", title: "Espelho do bloco" },
];

function EnterprisePicker({ options, value, onChange }: { options: EnterpriseOption[]; value: string; onChange: (value: string) => void }) {
  const selected = options.find((option) => option.id === value);
  return <label className="entity-picker"><span className="entity-picker-heading"><span>Empreendimento</span>{selected ? <BrandBadge name={selected.name} /> : null}</span><select value={value} onChange={(event) => onChange(event.target.value)}>{options.map((option) => <option key={option.id} value={option.id}>{option.name} · {option.city}</option>)}</select></label>;
}

function BlockStepper({ blocks, value, onChange, blurOnChange = false }: { blocks: EnterpriseData["blocks"]; value: string; onChange: (value: string) => void; blurOnChange?: boolean }) {
  const index = blocks.findIndex((block) => block.id === value);
  return <div className="block-stepper">
    <button type="button" className="step-button" onClick={() => index > 0 && onChange(blocks[index - 1].id)} disabled={index <= 0} aria-label="Bloco anterior">‹</button>
    <label><span>Bloco exibido</span><select className="inline-select" value={value} onChange={(event) => { onChange(event.target.value); if (blurOnChange) event.currentTarget.blur(); }}>{blocks.map((block) => <option key={block.id} value={block.id}>{block.label}</option>)}</select></label>
    <button type="button" className="step-button" onClick={() => index >= 0 && index < blocks.length - 1 && onChange(blocks[index + 1].id)} disabled={index < 0 || index >= blocks.length - 1} aria-label="Próximo bloco">›</button>
  </div>;
}

function Heatmap({ data, scope, selectedBlockId, onInspect }: { data: EnterpriseData; scope: HeatmapScope; selectedBlockId?: string; onInspect: (blockId: string) => void }) {
  const visibleBlocks = useMemo(() => {
    if (scope === "Todos") return data.blocks;
    if (scope === "Mais vendidos") return [...data.blocks].sort((a, b) => b.sold - a.sold || b.consumption - a.consumption).slice(0, 12);
    return [...data.blocks].sort((a, b) => a.sold - b.sold || a.consumption - b.consumption).slice(0, 12);
  }, [data.blocks, scope]);
  const visibleIds = new Set(visibleBlocks.map((block) => block.id));
  const stacks = [...new Set(data.stacks.filter((row) => visibleIds.has(row.blockId)).map((row) => row.stack))].sort((a, b) => a - b);
  if (!stacks.length) return <Empty title="Sem prumadas comparáveis" copy="As unidades não possuem andar e numeração suficientes para inferir a prumada." />;
  const baseline = data.kpis.consumption ?? 0;
  return <div className="heatmap-wrap">
    <div className="visual-key"><span><i className="key-line above" />Na média ou acima do empreendimento</span><span><i className="key-line below" />Abaixo da média</span></div>
    <div className="heatmap" style={{ gridTemplateColumns: `minmax(150px, 1.4fr) repeat(${stacks.length}, minmax(96px, 1fr))` }}>
      <div className="heat-corner">Bloco / prumada</div>
      {stacks.map((stack) => <div className="heat-head" key={stack}><span>Prumada</span><strong>{String(stack).padStart(2, "0")}</strong></div>)}
      {visibleBlocks.map((block) => <div className="heat-row" key={block.id} style={{ display: "contents" }}>
        <button type="button" className={`heat-label${block.id === selectedBlockId ? " selected" : ""}`} onClick={() => onInspect(block.id)} title="Abrir o espelho deste bloco"><strong>{block.label}</strong><span>{integer.format(block.sold)} de {integer.format(block.total)} vendidas</span><em>Ver espelho →</em></button>
        {stacks.map((stack) => {
          const cell = data.stacks.find((row) => row.blockId === block.id && row.stack === stack);
          if (!cell) return <div key={stack} className="heat-cell empty-cell" title="Sem unidades">—</div>;
          const tone = cell.consumption >= baseline ? "above" : "below";
          return <div key={stack} className={`heat-cell ${tone}${block.id === selectedBlockId ? " in-selected-row" : ""}`} title={`${cell.sold} vendidas de ${cell.total}`}>
            <div className="heat-value"><strong>{integer.format(cell.sold)}</strong><span>de {integer.format(cell.total)}</span></div>
            <small>{pct(cell.consumption, 0)} vendido</small>
            <div className="heat-meter"><i style={{ width: `${cell.consumption * 100}%` }} /></div>
          </div>;
        })}
      </div>)}
    </div>
    <p className="legend-note">Exibindo {visibleBlocks.length} bloco{visibleBlocks.length === 1 ? "" : "s"}. O número maior é a quantidade vendida; a régua mostra o percentual. Clique no nome de um bloco para abrir o espelho.</p>
  </div>;
}

function UnitDetailDrawer({ units, onClose }: { units: UnitDetail[]; onClose: () => void }) {
  const open = units.length > 0;
  const drawer = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
      if (event.key === "Tab") {
        event.preventDefault();
        drawer.current?.querySelector<HTMLButtonElement>(".drawer-close")?.focus();
      }
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKey);
    };
  }, [open, onClose]);
  if (!open) return null;
  const title = units.length > 1 ? `${units.length} unidades nesta posição` : `Unidade ${units[0].unit}`;
  return createPortal(<div className="unit-drawer-layer">
    <div className="unit-drawer-scrim" aria-hidden="true" onClick={onClose} />
    <aside className="unit-drawer" ref={drawer} role="dialog" aria-modal="true" aria-labelledby="unit-drawer-title">
      <div className="unit-drawer-handle" aria-hidden="true" />
      <header className="unit-drawer-heading"><div><span>Detalhes da unidade</span><h2 id="unit-drawer-title">{title}</h2></div><button type="button" className="drawer-close" onClick={onClose} autoFocus aria-label="Fechar detalhes">×</button></header>
      <div className="unit-drawer-body">
        {units.length > 1 ? <p className="data-note">Há mais de uma unidade registrada nesta combinação de andar e prumada.</p> : null}
        <div className="unit-detail-list">{units.map((unit) => <section className="unit-record" key={`${unit.blockId}-${unit.id}`}>
          <div className={`unit-record-status ${unit.sold ? "sold" : "stock"}`}><span>{unit.sold ? "Vendida" : "Não vendida"}</span><strong>{unit.status || "Status não informado"}</strong></div>
          <dl><div><dt>Bloco</dt><dd>{unit.block}</dd></div><div><dt>Unidade</dt><dd>{unit.unit}</dd></div><div><dt>Andar</dt><dd>{unit.floor == null ? "Não informado" : `${unit.floor}º`}</dd></div><div><dt>Prumada</dt><dd>{unit.stack == null ? "Não inferida" : String(unit.stack).padStart(2, "0")}</dd></div><div><dt>Tipologia</dt><dd>{unit.typology || "Não informada"}</dd></div><div><dt>Subtipologia</dt><dd>{unit.subtypology || "Não informada"}</dd></div><div><dt>Status oficial</dt><dd>{unit.status || "Não informado"}</dd></div><div><dt>Status CRM</dt><dd>{unit.statusCrm || "Não informado"}</dd></div></dl>
        </section>)}</div>
      </div>
    </aside>
  </div>, document.body);
}

function BuildingGrid({ data, blockId, mode, expanded, selectedUnitIds, onSelect }: { data: EnterpriseData; blockId: string; mode: MirrorMode; expanded: boolean; selectedUnitIds: string[]; onSelect: (ids: string[], trigger: HTMLButtonElement) => void }) {
  const blockUnits = data.units.filter((unit) => unit.blockId === blockId);
  const units = blockUnits.filter((unit) => unit.floor != null && unit.stack != null);
  const floorSales = new Map<number, { sold: number; total: number }>();
  blockUnits.forEach((unit) => {
    if (unit.floor == null) return;
    const row = floorSales.get(unit.floor) ?? { sold: 0, total: 0 };
    row.total += 1;
    if (unit.sold) row.sold += 1;
    floorSales.set(unit.floor, row);
  });
  const floors = [...floorSales.keys()].sort((a, b) => b - a);
  const stacks = [...new Set(units.map((unit) => unit.stack as number))].sort((a, b) => a - b);
  const block = data.blocks.find((item) => item.id === blockId);
  const missingFloors = blockUnits.filter((unit) => unit.floor == null).length;
  const invalidStacks = blockUnits.filter((unit) => unit.floor != null && unit.stack == null).length;
  const positions = new Map<string, number>();
  units.forEach((unit) => { const key = `${unit.floor}-${unit.stack}`; positions.set(key, (positions.get(key) ?? 0) + 1); });
  const collisions = [...positions.values()].filter((count) => count > 1).length;
  if (!units.length) return <Empty title="Sem mapa para este bloco" copy="As unidades precisam ter andar e numeração compatíveis com a regra de prumada." />;
  return <div className="building-wrap">
    {block ? <div className="building-summary"><div><span>Bloco selecionado</span><strong>{block.label}</strong></div><dl><div><dt>Vendidas</dt><dd>{integer.format(block.sold)}</dd></div><div><dt>Não vendidas</dt><dd>{integer.format(block.stock)}</dd></div><div><dt>Percentual vendido</dt><dd>{pct(block.consumption, 0)}</dd></div></dl></div> : null}
    <div className="building-frame">
      <div className="building-grid" style={{ gridTemplateColumns: `${expanded ? 92 : 82}px repeat(${stacks.length}, minmax(${expanded ? 92 : 76}px, 1fr)) minmax(${expanded ? 170 : 150}px, .9fr)` }}>
        <div className="building-corner">Andar</div>
        {stacks.map((stack) => <div key={stack} className="building-head"><span>Prumada</span><strong>{String(stack).padStart(2, "0")}</strong></div>)}
        <div className="building-head floor-sales-head"><span>Vendas</span><strong>do andar</strong></div>
        {floors.map((floor) => <div key={floor} className="building-row" style={{ display: "contents" }}>
          <div className="floor-label"><strong>{floor}º</strong><span>andar</span></div>
          {stacks.map((stack) => {
            const cell = units.filter((unit) => unit.floor === floor && unit.stack === stack);
            if (!cell.length) return <div key={stack} className="unit-cell missing">—</div>;
            const soldCount = cell.filter((unit) => unit.sold).length;
            const sold = soldCount === cell.length;
            const collision = cell.length > 1;
            const selected = cell.some((unit) => selectedUnitIds.includes(unit.id));
            const statusLabel = collision ? `${new Set(cell.map((unit) => STATUS_CODES[unit.status] ?? "OT")).size} status` : STATUS_CODES[cell[0].status] ?? "OT";
            return <button type="button" key={stack} className={`unit-cell ${sold ? "sold" : "stock"} ${collision ? "collision" : ""} ${selected ? "selected" : ""}`} title={`${cell.map((unit) => `${unit.unit}: ${unit.status}`).join("\n")}\nClique para ver os detalhes`} aria-pressed={selected} onClick={(event) => onSelect(cell.map((unit) => unit.id), event.currentTarget)}>
              <span className="unit-status" aria-hidden="true">{sold ? "✓" : "•"}</span>
              <strong>{collision ? `${cell.length} un.` : cell[0].unit}</strong>
              <span>{mode === "Status detalhado" ? statusLabel : collision ? `${soldCount} vendida${soldCount === 1 ? "" : "s"}` : sold ? "Vendida" : "Não vendida"}</span>
            </button>;
          })}
          <FloorSales sales={floorSales.get(floor)!} floor={floor} baseline={block?.consumption ?? 0} />
        </div>)}
      </div>
    </div>
    <div className="map-legend"><span><i className="dot sold" /> Vendida</span><span><i className="dot stock" /> Não vendida</span><span><i className="dot collision" /> Mais de uma unidade</span><span><i className="key-line" /> Andar na média do bloco ou acima</span><span><i className="key-line below" /> Andar abaixo da média do bloco</span></div>
    {mode === "Status detalhado" ? <details className="status-code-key"><summary>Entender as siglas dos status</summary><div>{[...new Set(blockUnits.map((unit) => unit.status))].sort((a, b) => a.localeCompare(b, "pt-BR")).map((status) => <span key={status}><b>{STATUS_CODES[status] ?? "OT"}</b>{status || "Não informado"}</span>)}</div></details> : null}
    {missingFloors || invalidStacks || collisions ? <p className="data-note">{[missingFloors ? `${missingFloors} sem andar informado` : "", invalidStacks ? `${invalidStacks} sem prumada inferida` : "", collisions ? `${collisions} posição${collisions === 1 ? "" : "ões"} com mais de uma unidade` : ""].filter(Boolean).join(" · ")}.</p> : null}
  </div>;
}

function FloorSales({ sales, floor, baseline }: { sales: { sold: number; total: number }; floor: number; baseline: number }) {
  const consumption = sales.total ? sales.sold / sales.total : 0;
  return <div className={`floor-sales ${consumption >= baseline ? "above" : "below"}`} title={`${floor}º andar: ${sales.sold} vendidas de ${sales.total} (${pct(consumption, 0)})`}>
    <div className="floor-sales-value"><strong>{integer.format(sales.sold)}</strong><span>de {integer.format(sales.total)}</span><em>{pct(consumption, 0)}</em></div>
    <div className="heat-meter"><i style={{ width: `${consumption * 100}%` }} /></div>
  </div>;
}

export default function BlocksView({ options, enterpriseId, onEnterpriseChange, data, loading }: { options: EnterpriseOption[]; enterpriseId: string; onEnterpriseChange: (value: string) => void; data: EnterpriseData | null; loading: boolean }) {
  const [metric, setMetric] = useState("Unidades vendidas");
  const [blockId, setBlockId] = useState("");
  const [heatmapScope, setHeatmapScope] = useState<HeatmapScope>("Menos vendidos");
  const [mirrorMode, setMirrorMode] = useState<MirrorMode>("Vendida ou não");
  const [selectedUnitIds, setSelectedUnitIds] = useState<string[]>([]);
  const [presentation, setPresentation] = useState<Screen | null>(null);
  const selectedUnitTrigger = useRef<HTMLButtonElement | null>(null);
  const summaryEntry = useRef<HTMLDivElement | null>(null);
  const rankingSection = useRef<HTMLElement | null>(null);
  const heatmapSection = useRef<HTMLElement | null>(null);
  const buildingSection = useRef<HTMLElement | null>(null);
  const presentationRoot = useRef<HTMLDivElement | null>(null);
  const nativeFullscreen = useRef(false);
  const drawerOpen = useRef(false);
  drawerOpen.current = selectedUnitIds.length > 0;
  const presentationScreen = useRef<Screen | null>(null);
  presentationScreen.current = presentation;
  useEffect(() => { if (data?.blocks.length && !data.blocks.some((block) => block.id === blockId)) setBlockId(data.blocks[data.blocks.length - 1].id); }, [data, blockId]);
  useEffect(() => { setSelectedUnitIds([]); }, [blockId, enterpriseId]);
  const blocksInOrder = useMemo(() => [...(data?.blocks ?? [])].sort((a, b) => a.label.localeCompare(b.label, "pt-BR", { numeric: true })), [data]);
  const blocksBySales = useMemo(() => [...(data?.blocks ?? [])].sort((a, b) => b.sold - a.sold || b.consumption - a.consumption || a.label.localeCompare(b.label, "pt-BR")), [data]);
  const mostSold = blocksBySales[0];
  const leastSold = [...blocksBySales].sort((a, b) => a.sold - b.sold || a.consumption - b.consumption || a.label.localeCompare(b.label, "pt-BR"))[0];
  const topStack = useMemo(() => [...(data?.stacks ?? [])].sort((a, b) => b.sold - a.sold || b.consumption - a.consumption || a.block.localeCompare(b.block, "pt-BR") || a.stack - b.stack)[0], [data]);
  const bars = useMemo(() => data?.blocks.map((row) => ({ id: row.id, label: row.label, value: metric === "Unidades vendidas" ? row.sold : row.consumption, valueLabel: metric === "Unidades vendidas" ? `${integer.format(row.sold)} vendidas` : `${pct(row.consumption, 0)} vendido`, detail: `total ${integer.format(row.total)} · ${pct(row.consumption, 0)} · ${integer.format(row.stock)} não vendidas`, tone: row.consumption >= (data.kpis.consumption ?? 0) ? "green" as const : "orange" as const })) ?? [], [data, metric]);
  const selectedUnits = data?.units.filter((unit) => unit.blockId === blockId && selectedUnitIds.includes(unit.id)) ?? [];
  const closeUnitDetails = useCallback(() => {
    setSelectedUnitIds([]);
    window.setTimeout(() => selectedUnitTrigger.current?.focus(), 0);
  }, []);
  const openUnitDetails = (ids: string[], trigger: HTMLButtonElement) => {
    selectedUnitTrigger.current = trigger;
    setSelectedUnitIds(ids);
  };
  const changeBlock = (value: string) => {
    setSelectedUnitIds([]);
    setBlockId(value);
  };
  const stepBlock = (offset: number) => {
    const next = blocksInOrder[blocksInOrder.findIndex((block) => block.id === blockId) + offset];
    if (next) changeBlock(next.id);
  };
  const moveScreen = (offset: number) => {
    const next = SCREENS[SCREENS.findIndex((screen) => screen.id === presentation) + offset];
    if (next) setPresentation(next.id);
  };
  const keyActions = useRef({ stepBlock, moveScreen });
  keyActions.current = { stepBlock, moveScreen };

  const focusEntry = useCallback((screen: Screen) => {
    window.requestAnimationFrame(() => {
      const entries = { summary: summaryEntry.current, ranking: rankingSection.current, heatmap: heatmapSection.current, building: buildingSection.current };
      entries[screen]?.querySelector<HTMLButtonElement>(".expand-button")?.focus();
    });
  }, []);
  const leavePresentation = useCallback(() => {
    const screen = presentationScreen.current;
    if (nativeFullscreen.current && document.fullscreenElement) document.exitFullscreen().catch(() => undefined);
    nativeFullscreen.current = false;
    setPresentation(null);
    if (screen) focusEntry(screen);
  }, [focusEntry]);
  const openPresentation = (screen: Screen) => {
    setPresentation(screen);
    window.requestAnimationFrame(() => presentationRoot.current?.querySelector<HTMLButtonElement>('[role="tab"][aria-selected="true"]')?.focus());
    if (!document.fullscreenElement && document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().then(() => { nativeFullscreen.current = true; }).catch(() => undefined);
    }
  };
  const presenting = presentation !== null;
  useEffect(() => {
    if (!presenting) return;
    document.documentElement.classList.add("has-fullscreen-panel");
    const handleKey = (event: KeyboardEvent) => {
      if (drawerOpen.current) return;
      if (event.key === "Escape") { leavePresentation(); return; }
      if (event.ctrlKey || event.altKey || event.metaKey) return;
      if ((event.target as HTMLElement | null)?.closest("select, input, textarea")) return;
      const actions = keyActions.current;
      if (event.key === "ArrowLeft") actions.stepBlock(-1);
      else if (event.key === "ArrowRight") actions.stepBlock(1);
      else if (event.key === "ArrowUp") actions.moveScreen(-1);
      else if (event.key === "ArrowDown") actions.moveScreen(1);
      else if (/^[1-4]$/.test(event.key)) setPresentation(SCREENS[Number(event.key) - 1].id);
      else return;
      event.preventDefault();
    };
    const handleNativeChange = () => {
      if (document.fullscreenElement || !nativeFullscreen.current) return;
      nativeFullscreen.current = false;
      if (drawerOpen.current) setSelectedUnitIds([]);
      else leavePresentation();
    };
    window.addEventListener("keydown", handleKey);
    document.addEventListener("fullscreenchange", handleNativeChange);
    return () => {
      document.documentElement.classList.remove("has-fullscreen-panel");
      window.removeEventListener("keydown", handleKey);
      document.removeEventListener("fullscreenchange", handleNativeChange);
    };
  }, [presenting, leavePresentation]);
  useEffect(() => () => { if (nativeFullscreen.current && document.fullscreenElement) document.exitFullscreen().catch(() => undefined); }, []);
  useEffect(() => {
    if (presentation) presentationRoot.current?.querySelector(".presentation-body .selected")?.scrollIntoView({ block: "nearest" });
  }, [presentation, blockId]);
  const inspectBlock = (value: string) => {
    changeBlock(value);
    if (presentation) {
      setPresentation("building");
      return;
    }
    window.requestAnimationFrame(() => buildingSection.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
  };

  if (!options.length) return <Empty title="Nenhum empreendimento disponível" copy="Ajuste os filtros para continuar." />;
  const ready = data;
  const summary = ready ? <>
    <Insight tone={(ready.kpis.consumption ?? 0) >= ready.baseline ? "positive" : "attention"} detail={mostSold && leastSold ? `${mostSold.label} é o mais vendido, com ${integer.format(mostSold.sold)} unidades; ${leastSold.label} é o menos vendido, com ${integer.format(leastSold.sold)}.` : undefined}><strong>{ready.enterprise.name}</strong> <BrandBadge name={ready.enterprise.name} /> vendeu <strong>{integer.format(ready.kpis.sold)} de {integer.format(ready.kpis.total)} unidades</strong> ({pct(ready.kpis.consumption)}).</Insight>
    <SummaryStrip items={[
      { value: `${integer.format(ready.kpis.sold)} vendidas`, label: `de ${integer.format(ready.kpis.total)} · ${pct(ready.kpis.consumption)}` },
      { value: mostSold?.label ?? "—", label: mostSold ? `mais vendido · ${integer.format(mostSold.sold)} de ${integer.format(mostSold.total)} · ${pct(mostSold.consumption, 0)}` : "mais vendido" },
      { value: leastSold?.label ?? "—", label: leastSold ? `menos vendido · ${integer.format(leastSold.sold)} de ${integer.format(leastSold.total)} · ${pct(leastSold.consumption, 0)}` : "menos vendido" },
      { value: topStack ? `Prumada ${String(topStack.stack).padStart(2, "0")}` : "—", label: topStack ? `${topStack.block} · ${integer.format(topStack.sold)} vendidas de ${integer.format(topStack.total)} · ${pct(topStack.consumption, 0)}` : "prumada mais vendida" },
    ]} />
  </> : null;
  const metricToggle = <MetricToggle options={["Unidades vendidas", "Percentual vendido"]} value={metric} onChange={setMetric} />;
  const scopeToggle = <MetricToggle options={["Menos vendidos", "Mais vendidos", "Todos"]} value={heatmapScope} onChange={(value) => setHeatmapScope(value as HeatmapScope)} />;
  const mirrorToggle = <MetricToggle options={["Vendida ou não", "Status detalhado"]} value={mirrorMode} onChange={(value) => setMirrorMode(value as MirrorMode)} />;
  const activeScreen = SCREENS.find((screen) => screen.id === presentation);

  return <div className="view-stack">
    <div className="picker-row" ref={summaryEntry}><EnterprisePicker options={options} value={enterpriseId} onChange={onEnterpriseChange} />{ready ? <ExpandButton expanded={false} label="o painel de blocos e prumadas" onClick={() => openPresentation("summary")} /> : null}</div>
    {loading && !ready ? <Loading label="Organizando blocos e prumadas" /> : !ready ? <Empty title="Não foi possível carregar os blocos" copy="Tente selecionar o empreendimento novamente ou ajuste os filtros." /> : <>
      {loading ? <div className="update-status" role="status">Atualizando o recorte do empreendimento…</div> : null}
      {summary}
      <section className="panel" ref={rankingSection}><SectionHeader title="Quais blocos venderam mais?" copy="Verde está na média ou acima do empreendimento; laranja, abaixo." action={<div className="section-actions">{metricToggle}<ExpandButton expanded={false} label="o ranking de blocos" onClick={() => openPresentation("ranking")} /></div>} /><BarList items={bars} onSelect={inspectBlock} selected={blockId} /></section>
      <section className="panel" ref={heatmapSection}><SectionHeader title="Como as prumadas se comparam?" copy="Veja quantas unidades cada prumada vendeu e use o percentual apenas como contexto." action={<div className="section-actions">{scopeToggle}<ExpandButton expanded={false} label="o comparativo de prumadas" onClick={() => openPresentation("heatmap")} /></div>} /><Heatmap data={ready} scope={heatmapScope} onInspect={inspectBlock} /></section>
      <section className="panel building-panel" ref={buildingSection}>
        <SectionHeader title="Espelho do bloco" copy="Cada linha mostra um andar com suas unidades por prumada e, no fim, quanto o andar já vendeu. Clique em um apartamento para abrir sua ficha." />
        <div className="building-toolbar"><BlockStepper blocks={blocksInOrder} value={blockId} onChange={changeBlock} /><div className="toolbar-actions">{mirrorToggle}<ExpandButton expanded={false} label="o espelho do bloco" onClick={() => openPresentation("building")} /></div></div>
        {blockId ? <BuildingGrid data={ready} blockId={blockId} mode={mirrorMode} expanded={false} selectedUnitIds={selectedUnitIds} onSelect={openUnitDetails} /> : null}
      </section>
      <details className="details-panel"><summary>Ver unidades e exportar</summary><div className="details-body"><button className="secondary-button" onClick={() => csvDownload(`unidades_${ready.enterprise.name}.csv`, ready.units.filter((unit) => !blockId || unit.blockId === blockId))}>Exportar CSV</button><TableShell><table><thead><tr><th>Bloco</th><th>Unidade</th><th>Andar</th><th>Prumada</th><th>Tipologia</th><th>Subtipologia</th><th>Status oficial</th><th>Status CRM</th><th>Vendida</th></tr></thead><tbody>{ready.units.filter((unit) => !blockId || unit.blockId === blockId).slice(0, 400).map((unit) => <tr key={`${unit.blockId}-${unit.id}`}><td>{unit.block}</td><td>{unit.unit}</td><td>{unit.floor ?? "—"}</td><td>{unit.stack ?? "—"}</td><td>{unit.typology || "—"}</td><td>{unit.subtypology || "—"}</td><td>{unit.status || "—"}</td><td>{unit.statusCrm || "—"}</td><td>{unit.sold ? "Sim" : "Não"}</td></tr>)}</tbody></table></TableShell></div></details>
      {presentation && activeScreen ? <div className="fullscreen-panel presentation" ref={presentationRoot} role="dialog" aria-modal="true" aria-label={`${ready.enterprise.name} em tela cheia`}>
        <header className="presentation-header">
          <div className="presentation-top">
            <div className="fullscreen-title"><span>{ready.enterprise.name}</span><strong>{activeScreen.title}</strong></div>
            <div className="presentation-tabs" role="tablist" aria-label="Painéis">{SCREENS.map((screen, index) => <button type="button" key={screen.id} id={`presentation-tab-${screen.id}`} role="tab" aria-selected={presentation === screen.id} aria-controls="presentation-body" className={presentation === screen.id ? "active" : ""} onClick={() => setPresentation(screen.id)}><kbd>{index + 1}</kbd>{screen.label}</button>)}</div>
            <ExpandButton expanded label="o painel" onClick={leavePresentation} />
          </div>
          {presentation !== "summary" ? <div className="presentation-controls"><BlockStepper blocks={blocksInOrder} value={blockId} onChange={changeBlock} blurOnChange />{presentation === "ranking" ? metricToggle : presentation === "heatmap" ? scopeToggle : mirrorToggle}</div> : null}
        </header>
        <div id="presentation-body" key={presentation} className={`presentation-body${presentation === "heatmap" || presentation === "building" ? " grid-screen" : ""}`} role="tabpanel" aria-labelledby={`presentation-tab-${presentation}`}>
          {presentation === "summary" ? <div className="presentation-summary">{summary}</div> : null}
          {presentation === "ranking" ? <BarList items={bars} onSelect={inspectBlock} selected={blockId} /> : null}
          {presentation === "heatmap" ? <Heatmap data={ready} scope={heatmapScope} selectedBlockId={blockId} onInspect={inspectBlock} /> : null}
          {presentation === "building" && blockId ? <BuildingGrid data={ready} blockId={blockId} mode={mirrorMode} expanded selectedUnitIds={selectedUnitIds} onSelect={openUnitDetails} /> : null}
        </div>
        <footer className="presentation-hints" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> trocar painel</span><span><kbd>←</kbd><kbd>→</kbd> trocar bloco</span><span><kbd>1</kbd>–<kbd>4</kbd> ir direto ao painel</span><span><kbd>Esc</kbd> sair</span></footer>
      </div> : null}
      <UnitDetailDrawer units={selectedUnits} onClose={closeUnitDetails} />
    </>}
  </div>;
}

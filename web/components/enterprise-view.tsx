"use client";

import { useMemo, useState } from "react";

import { BarList, BrandBadge, Empty, Insight, Loading, MetricToggle, SectionHeader, StockComposition, SummaryStrip, TableShell } from "@/components/primitives";
import { csvDownload, integer, pct } from "@/lib/format";
import type { EnterpriseData, EnterpriseOption } from "@/lib/types";

export default function EnterpriseView({ options, enterpriseId, onEnterpriseChange, selectedBlocks, onSelectedBlocksChange, data, loading }: {
  options: EnterpriseOption[];
  enterpriseId: string;
  onEnterpriseChange: (value: string) => void;
  selectedBlocks: string[];
  onSelectedBlocksChange: (value: string[]) => void;
  data: EnterpriseData | null;
  loading: boolean;
}) {
  const [metric, setMetric] = useState("Ainda não vendidas");
  const floors = useMemo(() => {
    if (!data) return [];
    const field = metric === "Ainda não vendidas" ? "stock" : metric === "Unidades vendidas" ? "sold" : "consumption";
    return [...data.floors].sort((a, b) => b[field] - a[field]);
  }, [data, metric]);
  if (!options.length) return <Empty title="Nenhum empreendimento disponível" copy="Ajuste os filtros para continuar." />;
  const selected = options.find((option) => option.id === enterpriseId);
  return <div className="view-stack"><label className="entity-picker"><span className="entity-picker-heading"><span>Empreendimento</span>{selected ? <BrandBadge name={selected.name} /> : null}</span><select value={enterpriseId} onChange={(event) => onEnterpriseChange(event.target.value)}>{options.map((option) => <option key={option.id} value={option.id}>{option.name} · {option.city}</option>)}</select></label>{loading || !data ? <Loading label="Lendo o empreendimento" /> : (() => {
    const groups = Object.fromEntries(data.stockGroups.map((group) => [group.group, group.units]));
    const mostStock = [...data.floors].sort((a, b) => b.stock - a.stock)[0];
    const leastSold = [...data.floors].sort((a, b) => a.consumption - b.consumption)[0];
    const unsold = data.units.filter((unit) => !unit.sold).sort((a, b) => a.block.localeCompare(b.block, "pt-BR") || (a.floor ?? 999) - (b.floor ?? 999));
    const difference = (data.kpis.consumption ?? 0) - data.baseline;
    return <>
      <div className="enterprise-subfilters"><span>Recorte do empreendimento</span><details className="filter-menu"><summary>{selectedBlocks.length ? `Blocos (${selectedBlocks.length})` : "Todos os blocos"}</summary><div className="filter-options"><button onClick={() => onSelectedBlocksChange([])} className={!selectedBlocks.length ? "active" : ""}>Todos os blocos</button>{data.blockOptions.map((block) => <label key={block.id}><input type="checkbox" checked={selectedBlocks.includes(block.id)} onChange={(event) => onSelectedBlocksChange(event.target.checked ? [...selectedBlocks, block.id] : selectedBlocks.filter((value) => value !== block.id))} /><span>{block.label}</span></label>)}</div></details>{selectedBlocks.length ? <button className="clear-filters" onClick={() => onSelectedBlocksChange([])}>Limpar recorte</button> : null}</div>
      <Insight tone={(data.kpis.consumption ?? 0) >= .95 ? "positive" : (data.kpis.consumption ?? 0) < .5 ? "attention" : "default"} detail={`Restam ${integer.format(data.kpis.stock)} unidades: ${integer.format(groups["Em comercialização"] ?? 0)} em comercialização, ${integer.format(groups.Reservadas ?? 0)} reservadas e ${integer.format(groups["Fora de venda"] ?? 0)} fora de venda.`}><strong>{data.enterprise.name}</strong> <BrandBadge name={data.enterprise.name} /> está <strong>{pct(data.kpis.consumption)}</strong> vendido, {Math.abs(difference * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} p.p. {difference >= 0 ? "acima" : "abaixo"} da média do filtro.</Insight>
      <SummaryStrip items={[
        { value: `${integer.format(data.kpis.sold)} vendidas`, label: `de ${integer.format(data.kpis.total)} unidades` },
        { value: `${integer.format(data.kpis.stock)} não vendidas`, label: `${integer.format(groups["Em comercialização"] ?? 0)} em comercialização` },
        { value: pct(data.kpis.consumption), label: "percentual vendido" },
        { value: mostStock ? `${mostStock.floor}º andar` : "—", label: mostStock ? `mais estoque · ${integer.format(mostStock.stock)} unidades` : "mais estoque" },
      ]} />
      <section className="panel"><SectionHeader title="Vendas e estoque por andar" copy="Compare números absolutos e percentual. Cada linha mantém o total como referência." action={<MetricToggle options={["Ainda não vendidas", "Unidades vendidas", "Percentual vendido"]} value={metric} onChange={setMetric} />} /><div className="split-main"><BarList items={floors.map((row) => ({ id: String(row.floor), label: `${row.floor}º andar`, value: metric === "Ainda não vendidas" ? row.stock : metric === "Unidades vendidas" ? row.sold : row.consumption, valueLabel: metric === "Ainda não vendidas" ? `${integer.format(row.stock)} não vendidas` : `${integer.format(row.sold)} vendidas`, detail: `${integer.format(row.sold)} vendidas · total ${integer.format(row.total)} · ${pct(row.consumption, 0)}`, tone: metric === "Ainda não vendidas" ? "orange" : "green" }))} /><div className="highlights"><article><span>Mais unidades não vendidas</span><strong>{mostStock ? `${mostStock.floor}º andar` : "—"}</strong><p>{mostStock ? `${integer.format(mostStock.stock)} unidades · ${pct(mostStock.stock / Math.max(1, data.kpis.stock), 0)} do estoque` : "Sem estoque"}</p></article><article><span>Menor percentual vendido</span><strong>{leastSold ? `${leastSold.floor}º andar` : "—"}</strong><p>{leastSold ? `${integer.format(leastSold.sold)} vendidas de ${integer.format(leastSold.total)} · ${pct(leastSold.consumption, 0)}` : "Sem dados"}</p></article></div></div></section>
      <details className="details-panel"><summary>Entender os status das unidades não vendidas</summary><div className="details-body"><StockComposition groups={data.stockGroups} /></div></details>
      {unsold.length ? <section className="panel"><SectionHeader title="Unidades não vendidas" copy="Detalhe operacional para investigar o estoque atual." action={<button className="secondary-button" onClick={() => csvDownload(`unidades_${data.enterprise.name}.csv`, data.units)}>Exportar todas</button>} /><TableShell><table><thead><tr><th>Bloco</th><th>Unidade</th><th>Andar</th><th>Tipologia</th><th>Status</th></tr></thead><tbody>{unsold.slice(0, 500).map((unit) => <tr key={unit.id}><td>{unit.block}</td><td>{unit.unit}</td><td>{unit.floor ?? "—"}</td><td>{unit.typology || "—"}</td><td>{unit.status}</td></tr>)}</tbody></table></TableShell>{unsold.length > 500 ? <p className="legend-note">Mostrando as primeiras 500 unidades. O CSV contém o recorte completo.</p> : null}</section> : null}
    </>;
  })()}</div>;
}

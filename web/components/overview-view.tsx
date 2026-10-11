"use client";

import { BarList, EnterpriseLabel, Insight, SectionHeader, StockComposition, SummaryStrip, TableShell } from "@/components/primitives";
import { csvDownload, integer, pct } from "@/lib/format";
import type { DashboardData } from "@/lib/types";

export default function OverviewView({ data }: { data: DashboardData }) {
  const { kpis } = data;
  const stockLeader = [...data.enterpriseProgress].sort((a, b) => b.stock - a.stock)[0];
  const lowProgress = data.progressSummary.find((row) => row.band === "Menos de 50% vendido");
  const highProgress = data.progressSummary.find((row) => row.band === "95% ou mais vendido");
  const topStock = [...data.enterpriseProgress].filter((row) => row.stock > 0).sort((a, b) => b.stock - a.stock).slice(0, 8);

  return <div className="view-stack">
    <Insight tone={kpis.consumption != null && kpis.consumption >= .8 ? "positive" : "attention"} detail={stockLeader ? `${stockLeader.name} concentra o maior estoque: ${integer.format(stockLeader.stock)} unidades.` : undefined}>
      O portfólio está <strong>{pct(kpis.consumption)}</strong> vendido. Restam <strong>{integer.format(kpis.stock)} unidades</strong>.
    </Insight>

    <SummaryStrip items={[
      { value: integer.format(kpis.sold), label: `vendidas de ${integer.format(kpis.total)}` },
      { value: integer.format(kpis.stock), label: "ainda não vendidas" },
      { value: lowProgress ? integer.format(lowProgress.enterprises) : "0", label: "empreendimentos abaixo de 50%" },
      { value: highProgress ? integer.format(highProgress.enterprises) : "0", label: "empreendimentos com 95% ou mais" },
    ]} />

    <div className="split-main">
      <section className="panel panel-main">
        <SectionHeader title="Onde está concentrado o estoque?" copy="Empreendimentos com mais unidades ainda não vendidas." />
        {topStock.length ? <BarList items={topStock.map((row) => ({ id: row.id, label: <EnterpriseLabel name={row.name} />, value: row.stock, valueLabel: `${integer.format(row.stock)} unidades`, detail: `${integer.format(row.sold)} vendidas de ${integer.format(row.total)} · ${pct(row.consumption, 0)}`, tone: row.consumption < .5 ? "orange" : "green" }))} /> : <p>Não há estoque neste recorte.</p>}
      </section>
      <section className="panel">
        <SectionHeader title="Do que é composto o estoque?" copy="Situação atual das unidades não vendidas." />
        <StockComposition groups={data.stockGroups} />
      </section>
    </div>

    <section className="panel">
      <SectionHeader title="Em que andares está o estoque?" copy="Número absoluto primeiro; percentual vendido como contexto." />
      <BarList items={[...data.floors].sort((a, b) => b.stock - a.stock).slice(0, 12).map((row) => ({ id: String(row.floor), label: `${row.floor}º andar`, value: row.stock, valueLabel: `${integer.format(row.stock)} não vendidas`, detail: `${integer.format(row.sold)} vendidas de ${integer.format(row.total)} · ${pct(row.consumption, 0)}`, tone: "orange" }))} />
      {data.floorBand ? <p className="comparison-note">Andares até o {data.floorBand.lowMax}º: <strong>{pct(data.floorBand.low.consumption)}</strong> vendido. A partir do {data.floorBand.highMin}º: <strong>{pct(data.floorBand.high.consumption)}</strong>.</p> : null}
    </section>

    <details className="details-panel"><summary>Ver todos os empreendimentos ({integer.format(data.enterpriseProgress.length)})</summary><div className="details-body"><button className="secondary-button" onClick={() => csvDownload(`empreendimentos_${data.meta.snapshotDate}.csv`, data.enterpriseProgress)}>Exportar CSV</button><TableShell><table><thead><tr><th>Empreendimento</th><th>Cidade</th><th>Vendidas</th><th>Total</th><th>Não vendidas</th><th>% vendido</th></tr></thead><tbody>{data.enterpriseProgress.map((row) => <tr key={row.id}><td><EnterpriseLabel name={row.name} /></td><td>{row.city}</td><td>{integer.format(row.sold)}</td><td>{integer.format(row.total)}</td><td>{integer.format(row.stock)}</td><td>{pct(row.consumption)}</td></tr>)}</tbody></table></TableShell></div></details>
  </div>;
}

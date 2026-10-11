"use client";

import { Empty, Insight, Loading, SectionHeader, SummaryStrip, TableShell } from "@/components/primitives";
import { csvDownload, dateLabel, integer, pct } from "@/lib/format";
import type { VelocityData } from "@/lib/types";

function Timeline({ data }: { data: VelocityData }) {
  const width = 860;
  const height = 240;
  const pad = 42;
  const values = data.timeline.map((row) => row.consumption);
  const min = Math.max(0, Math.min(...values) - .03);
  const max = Math.min(1, Math.max(...values) + .03);
  const points = values.map((value, index) => ({ x: pad + index * ((width - pad * 2) / Math.max(1, values.length - 1)), y: height - pad - ((value - min) / Math.max(.001, max - min)) * (height - pad * 2), value, date: data.timeline[index].snapshot_date }));
  return <div className="line-chart"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Evolução do percentual vendido"><line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} className="axis" /><polyline points={points.map((point) => `${point.x},${point.y}`).join(" ")} className="line" />{points.map((point) => <g key={point.date}><circle cx={point.x} cy={point.y} r="6" /><text x={point.x} y={point.y - 16} textAnchor="middle">{pct(point.value, 1)}</text><text x={point.x} y={height - 14} textAnchor="middle" className="date-text">{dateLabel(point.date, false)}</text></g>)}</svg></div>;
}

export default function VelocityView({ data, loading }: { data: VelocityData | null; loading: boolean }) {
  if (loading || !data) return <Loading label="Calculando a velocidade" />;
  if (data.timeline.length < 2) {
    const current = data.timeline[0];
    if (!current) return <Empty title="Nenhuma foto disponível" copy="Faça a primeira ingestão para iniciar o acompanhamento." />;
    return <div className="view-stack"><Insight detail="Na próxima atualização, rode a ingestão com a data em que a nova planilha foi extraída.">Ainda não dá para medir o ritmo, mas a primeira foto já está guardada: <strong>{dateLabel(current.snapshot_date)}</strong>.</Insight><SummaryStrip items={[
      { value: integer.format(current.sold), label: "vendidas nesta foto" },
      { value: integer.format(current.stock), label: "ainda não vendidas" },
      { value: pct(current.consumption), label: "percentual vendido" },
    ]} /><section className="panel"><SectionHeader title="Como a velocidade será calculada" /><ol className="method-list"><li>Compara cada unidade pelo <strong>{data.method.identity}</strong>.</li><li>{data.method.saleRule}</li><li>{data.method.monthlyRule}</li><li>{data.method.coverage}</li></ol></section></div>;
  }
  const latest = data.transitions[data.transitions.length - 1];
  return <div className="view-stack"><Insight tone={latest.net_sales > 0 ? "positive" : "attention"} detail={latest.reversals ? `${integer.format(latest.reversals)} vendas foram desfeitas; saldo líquido de ${integer.format(latest.net_sales)}.` : "Nenhuma venda desfeita no período."}>Entre {dateLabel(latest.previous_date, false)} e {dateLabel(latest.snapshot_date)} foram <strong>{integer.format(latest.new_sales)} novas vendas</strong>{latest.monthly_velocity != null ? `, ritmo equivalente a ${integer.format(Math.round(latest.monthly_velocity))} por mês.` : "."}</Insight><SummaryStrip items={[
    { value: latest.monthly_velocity == null ? "n.d." : integer.format(Math.round(latest.monthly_velocity)), label: "ritmo mensal" },
    { value: integer.format(latest.new_sales), label: `novas vendas em ${latest.days} dias` },
    { value: integer.format(latest.reversals), label: "vendas desfeitas" },
  ]} /><section className="panel"><SectionHeader title="Evolução do percentual vendido" copy="Cada ponto representa uma foto importada da base." /><Timeline data={data} /></section><section className="panel"><SectionHeader title="Vendas em cada período" action={<button className="secondary-button" onClick={() => csvDownload("transicoes_snapshots.csv", data.transitions)}>Exportar CSV</button>} /><div className="period-bars">{data.transitions.map((row) => <div key={row.snapshot_date}><span>{dateLabel(row.snapshot_date)}</span><div><i className="new-sales" style={{ width: `${Math.max(2, row.new_sales / Math.max(...data.transitions.map((item) => item.new_sales), 1) * 100)}%` }} /><strong>{integer.format(row.new_sales)} novas</strong></div><div><i className="reversals" style={{ width: `${Math.max(row.reversals ? 2 : 0, row.reversals / Math.max(...data.transitions.map((item) => item.new_sales), 1) * 100)}%` }} /><strong>{integer.format(row.reversals)} desfeitas</strong></div></div>)}</div></section><details className="details-panel"><summary>Ver todos os períodos</summary><div className="details-body"><TableShell><table><thead><tr><th>Data anterior</th><th>Data atual</th><th>Dias</th><th>Novas vendas</th><th>Desfeitas</th><th>Líquidas</th><th>Ritmo mensal</th></tr></thead><tbody>{data.transitions.map((row) => <tr key={row.snapshot_date}><td>{dateLabel(row.previous_date)}</td><td>{dateLabel(row.snapshot_date)}</td><td>{row.days}</td><td>{integer.format(row.new_sales)}</td><td>{integer.format(row.reversals)}</td><td>{integer.format(row.net_sales)}</td><td>{row.monthly_velocity == null ? "n.d." : integer.format(Math.round(row.monthly_velocity))}</td></tr>)}</tbody></table></TableShell></div></details></div>;
}

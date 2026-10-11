"use client";

import { dateLabel } from "@/lib/format";
import type { FilterState } from "@/lib/types";
import { Icon } from "@/components/primitives";

function MultiFilter({ label, options, values, onChange }: { label: string; options: string[]; values: string[]; onChange: (values: string[]) => void }) {
  const summary = values.length ? `${label} (${values.length})` : label;
  return <details className="filter-menu"><summary>{summary}</summary><div className="filter-options"><button onClick={() => onChange([])} className={!values.length ? "active" : ""}>Todos</button>{options.map((option) => <label key={option}><input type="checkbox" checked={values.includes(option)} onChange={(event) => onChange(event.target.checked ? [...values, option] : values.filter((value) => value !== option))} /><span>{option || "Não informado"}</span></label>)}</div></details>;
}

export default function Filters({ filters, options, onChange, onClear }: {
  filters: FilterState;
  options: { dates: string[]; cities: string[]; typologies: string[]; statuses: string[] };
  onChange: (filters: FilterState) => void;
  onClear: () => void;
}) {
  const active = filters.cities.length + filters.typologies.length + filters.statuses.length;
  return <div className="filters"><div className="filters-title"><Icon name="filter" /><span>Filtros</span>{active ? <b>{active}</b> : null}</div><label className="date-select"><span>Foto da base</span><select value={filters.date} onChange={(event) => onChange({ ...filters, date: event.target.value })}>{options.dates.map((date) => <option key={date} value={date}>{dateLabel(date)}</option>)}</select></label><MultiFilter label="Cidade" options={options.cities} values={filters.cities} onChange={(cities) => onChange({ ...filters, cities })} /><MultiFilter label="Tipologia" options={options.typologies} values={filters.typologies} onChange={(typologies) => onChange({ ...filters, typologies })} /><MultiFilter label="Status oficial" options={options.statuses} values={filters.statuses} onChange={(statuses) => onChange({ ...filters, statuses })} />{active ? <button className="clear-filters" onClick={onClear}>Limpar filtros</button> : null}</div>;
}

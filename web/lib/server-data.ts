import "server-only";

import fs from "node:fs";
import path from "node:path";

import type { DashboardData, EnterpriseData, Kpis, VelocityData } from "@/lib/types";

type Manifest = {
  schemaVersion: number;
  generatedAt: string;
  latestDate: string;
  snapshots: Array<{
    date: string;
    file: string;
    rowCount: number;
    sourceFile: string | null;
  }>;
};

type Unit = {
  enterpriseId: string;
  blockId: string;
  unitId: string;
  city: string;
  enterpriseName: string;
  blockName: string;
  unitName: string;
  typology: string;
  subtypology: string;
  statusRaw: string;
  status: string;
  statusCrm: string;
  reportedFloors: number | null;
  floor: number | null;
  sold: boolean;
  floorMissing: boolean;
  floorAboveReported: boolean;
  statusConflict: boolean;
  typologyMissing: boolean;
  subtypologyMissing: boolean;
  unknownStatus: boolean;
};

const DATA_DIR = path.join(process.cwd(), "data-generated");
const snapshotCache = new Map<string, { version: string; units: Unit[] }>();

const STATUS_GROUPS: Record<string, string> = {
  "EXCLUSIVO PLATAFORMA": "Em comercialização",
  LANÇADO: "Em comercialização",
  "PRÉ VENDA": "Em comercialização",
  RESERVADO: "Reservadas",
  "RESERVADO COM CONTRATO PRE ATIVO": "Reservadas",
  "NÃO LANÇADO": "Fora de venda",
  BLOQUEADO: "Fora de venda",
  PERMUTADO: "Fora de venda",
  "RESERVA PARA PERMUTA": "Fora de venda",
};

const PROGRESS_BANDS = [
  { label: "Menos de 50% vendido", min: 0 },
  { label: "50% a 80% vendido", min: 0.5 },
  { label: "80% a 95% vendido", min: 0.8 },
  { label: "95% ou mais vendido", min: 0.95 },
];

const ISSUE_DEFS = [
  { key: "floorMissing", label: "Andar não informado" },
  { key: "reportedFloorsMissing", label: "Pavimentos não informado" },
  { key: "floorAboveReported", label: "Andar superior aos pavimentos" },
  { key: "statusConflict", label: "Divergência na classificação de venda (oficial × CRM)" },
  { key: "typologyMissing", label: "Tipologia não informada" },
  { key: "subtypologyMissing", label: "Subtipologia não informada" },
  { key: "unknownStatus", label: "Status não reconhecido" },
] as const;

function readJson<T>(relativePath: string): T {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, relativePath), "utf8")) as T;
}

export function getManifest(): Manifest {
  return readJson<Manifest>("manifest.json");
}

function stringValue(value: unknown) {
  return value == null ? "" : String(value);
}

function loadSnapshot(date: string): Unit[] {
  const manifest = getManifest();
  const snapshot = manifest.snapshots.find((item) => item.date === date);
  if (!snapshot) throw new Error(`Snapshot ${date} não encontrado.`);
  const cached = snapshotCache.get(date);
  if (cached?.version === manifest.generatedAt) return cached.units;
  const payload = readJson<{ columns: string[]; rows: unknown[][] }>(snapshot.file);
  const index = Object.fromEntries(payload.columns.map((column, position) => [column, position]));
  const units = payload.rows.map((row): Unit => ({
    enterpriseId: stringValue(row[index.enterprise_id]),
    blockId: stringValue(row[index.block_id]),
    unitId: stringValue(row[index.unit_id]),
    city: stringValue(row[index.city]),
    enterpriseName: stringValue(row[index.enterprise_name]),
    blockName: stringValue(row[index.block_name]),
    unitName: stringValue(row[index.unit_name]),
    typology: stringValue(row[index.typology]),
    subtypology: stringValue(row[index.subtypology]),
    statusRaw: stringValue(row[index.status_unit_raw]),
    status: stringValue(row[index.status_unit_normalized]),
    statusCrm: stringValue(row[index.status_crm_raw]),
    reportedFloors: row[index.reported_floors] == null ? null : Number(row[index.reported_floors]),
    floor: row[index.floor] == null ? null : Number(row[index.floor]),
    sold: Boolean(row[index.is_sold]),
    floorMissing: Boolean(row[index.floor_missing]),
    floorAboveReported: Boolean(row[index.floor_above_reported]),
    statusConflict: Boolean(row[index.status_conflict]),
    typologyMissing: Boolean(row[index.typology_missing]),
    subtypologyMissing: Boolean(row[index.subtypology_missing]),
    unknownStatus: Boolean(row[index.unknown_status]),
  }));
  snapshotCache.set(date, { version: manifest.generatedAt, units });
  return units;
}

function unique(values: string[]) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR"));
}

function filterUnits(units: Unit[], params: URLSearchParams, includeEnterprise = true) {
  const cities = params.getAll("city");
  const typologies = params.getAll("typology");
  const statuses = params.getAll("status");
  const enterprise = includeEnterprise ? params.get("enterprise") : null;
  const blocks = includeEnterprise ? params.getAll("block") : [];
  return units.filter((unit) =>
    (!cities.length || cities.includes(unit.city)) &&
    (!typologies.length || typologies.includes(unit.typology)) &&
    (!statuses.length || statuses.includes(unit.status)) &&
    (!enterprise || unit.enterpriseId === enterprise) &&
    (!blocks.length || blocks.includes(unit.blockId)),
  );
}

function kpis(units: Unit[]): Kpis {
  const total = new Set(units.map((unit) => unit.unitId)).size;
  const sold = new Set(units.filter((unit) => unit.sold).map((unit) => unit.unitId)).size;
  return { total, sold, stock: total - sold, consumption: total ? sold / total : null };
}

function grouped<T extends Record<string, string | number | null>>(units: Unit[], key: (unit: Unit) => T) {
  const groups = new Map<string, { dimensions: T; units: Unit[] }>();
  for (const unit of units) {
    const dimensions = key(unit);
    const token = JSON.stringify(dimensions);
    const current = groups.get(token);
    if (current) current.units.push(unit);
    else groups.set(token, { dimensions, units: [unit] });
  }
  return [...groups.values()].map(({ dimensions, units: rows }) => ({ ...dimensions, ...kpis(rows) }));
}

function band(value: number) {
  return [...PROGRESS_BANDS].reverse().find((item) => value >= item.min)?.label ?? PROGRESS_BANDS[0].label;
}

function stockComposition(units: Unit[]) {
  const unsold = units.filter((unit) => !unit.sold);
  const total = unsold.length;
  const groupCounts = new Map<string, number>();
  const statusCounts = new Map<string, number>();
  for (const unit of unsold) {
    const group = STATUS_GROUPS[unit.status] ?? "Outros status";
    groupCounts.set(group, (groupCounts.get(group) ?? 0) + 1);
    statusCounts.set(unit.status, (statusCounts.get(unit.status) ?? 0) + 1);
  }
  const order = ["Em comercialização", "Reservadas", "Fora de venda", "Outros status"];
  const stockGroups = order
    .map((group) => ({ group, units: groupCounts.get(group) ?? 0, share: total ? (groupCounts.get(group) ?? 0) / total : 0 }))
    .filter((item) => item.units || item.group !== "Outros status");
  const stockStatuses = [...statusCounts.entries()]
    .map(([status, count]) => ({ status, units: count, share: total ? count / total : 0 }))
    .sort((a, b) => b.units - a.units);
  return { stockGroups, stockStatuses };
}

function floorRows(units: Unit[]) {
  return grouped(units.filter((unit) => unit.floor != null), (unit) => ({ floor: unit.floor }))
    .map((row) => ({ ...row, floor: Number(row.floor), consumption: row.consumption ?? 0 }))
    .sort((a, b) => a.floor - b.floor);
}

function issueMatch(unit: Unit, key: string) {
  if (key === "reportedFloorsMissing") return unit.reportedFloors == null;
  return Boolean(unit[key as keyof Unit]);
}

export function dashboardData(params: URLSearchParams): DashboardData {
  const manifest = getManifest();
  const date = params.get("date") ?? manifest.latestDate;
  const all = loadSnapshot(date);
  const filtered = filterUnits(all, params, false);
  const scopeKpis = kpis(filtered);
  const enterpriseProgress = grouped(filtered, (unit) => ({ id: unit.enterpriseId, city: unit.city, name: unit.enterpriseName }))
    .map((row) => ({ ...row, consumption: row.consumption ?? 0, band: band(row.consumption ?? 0) }))
    .sort((a, b) => b.consumption - a.consumption || b.sold - a.sold);
  const progressSummary = PROGRESS_BANDS.map(({ label }) => {
    const rows = enterpriseProgress.filter((row) => row.band === label);
    const stock = rows.reduce((sum, row) => sum + row.stock, 0);
    return { band: label, enterprises: rows.length, stock, stockShare: scopeKpis.stock ? stock / scopeKpis.stock : 0 };
  });
  const floors = floorRows(filtered);
  const low = kpis(filtered.filter((unit) => unit.floor != null && unit.floor <= 5));
  const high = kpis(filtered.filter((unit) => unit.floor != null && unit.floor >= 10));
  const { stockGroups, stockStatuses } = stockComposition(filtered);
  const affected = filtered.filter((unit) => ISSUE_DEFS.some((issue) => issueMatch(unit, issue.key))).length;
  const issues = ISSUE_DEFS.map((issue) => {
    const count = filtered.filter((unit) => issueMatch(unit, issue.key)).length;
    return { ...issue, count, share: filtered.length ? count / filtered.length : 0 };
  }).filter((issue) => issue.count > 0).sort((a, b) => b.count - a.count);
  const snapshot = manifest.snapshots.find((item) => item.date === date)!;
  return {
    meta: {
      snapshotDate: date,
      generatedAt: manifest.generatedAt,
      sourceFile: snapshot.sourceFile,
      rowCount: snapshot.rowCount,
      scopeRows: filtered.length,
    },
    options: {
      dates: manifest.snapshots.map((item) => item.date),
      cities: unique(all.map((unit) => unit.city)),
      typologies: unique(all.map((unit) => unit.typology)),
      statuses: unique(all.map((unit) => unit.status)),
      enterprises: grouped(filtered, (unit) => ({ id: unit.enterpriseId, name: unit.enterpriseName, city: unit.city }))
        .map((row) => ({ id: String(row.id), name: String(row.name), city: String(row.city) }))
        .sort((a, b) => a.name.localeCompare(b.name, "pt-BR")),
    },
    kpis: scopeKpis,
    progressSummary,
    enterpriseProgress,
    floors,
    floorBand: low.total && high.total ? { low, high, lowMax: 5, highMin: 10 } : null,
    stockGroups,
    stockStatuses,
    quality: {
      clean: filtered.length - affected,
      cleanShare: filtered.length ? 1 - affected / filtered.length : 0,
      affected,
      issues,
    },
  };
}

export function enterpriseData(params: URLSearchParams): EnterpriseData {
  const manifest = getManifest();
  const date = params.get("date") ?? manifest.latestDate;
  const all = loadSnapshot(date);
  const scope = filterUnits(all, params, false);
  const enterpriseId = params.get("enterprise");
  if (!enterpriseId) throw new Error("Selecione um empreendimento.");
  const enterpriseParams = new URLSearchParams(params);
  enterpriseParams.delete("block");
  const enterpriseUnits = filterUnits(all, enterpriseParams, true);
  const selected = filterUnits(all, params, true);
  if (!selected.length) throw new Error("Nenhuma unidade encontrada nesse recorte.");
  const first = selected[0];
  const nameCounts = new Map<string, number>();
  for (const row of grouped(enterpriseUnits, (unit) => ({ id: unit.blockId, name: unit.blockName }))) {
    nameCounts.set(String(row.name), (nameCounts.get(String(row.name)) ?? 0) + 1);
  }
  const blockOptions = grouped(enterpriseUnits, (unit) => ({ id: unit.blockId, name: unit.blockName }))
    .map((row) => ({
      id: String(row.id),
      label: (nameCounts.get(String(row.name)) ?? 0) > 1 ? `${row.name} · ${String(row.id).slice(0, 4)}` : String(row.name),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  const blocks = grouped(selected, (unit) => ({ id: unit.blockId, name: unit.blockName }))
    .map((row) => ({
      ...row,
      id: String(row.id),
      name: String(row.name),
      label: (nameCounts.get(String(row.name)) ?? 0) > 1 ? `${row.name} · ${String(row.id).slice(0, 4)}` : String(row.name),
      consumption: row.consumption ?? 0,
    }))
    .sort((a, b) => b.consumption - a.consumption || b.sold - a.sold);
  const stackUnits = selected.filter((unit) => {
    const value = Number(unit.unitName);
    const stack = value % 100;
    return unit.floor != null && Number.isFinite(value) && stack >= 1 && stack <= 12;
  });
  const stacks = grouped(stackUnits, (unit) => ({
    blockId: unit.blockId,
    block: unit.blockName,
    stack: Number(unit.unitName) % 100,
  })).map((row) => ({ ...row, blockId: String(row.blockId), block: String(row.block), stack: Number(row.stack), consumption: row.consumption ?? 0 }));
  const { stockGroups, stockStatuses } = stockComposition(selected);
  return {
    enterprise: { id: first.enterpriseId, name: first.enterpriseName, city: first.city },
    blockOptions,
    baseline: kpis(scope).consumption ?? 0,
    kpis: kpis(selected),
    blocks,
    stacks,
    floors: floorRows(selected),
    stockGroups,
    stockStatuses,
    units: selected.map((unit) => {
      const number = Number(unit.unitName);
      const inferred = number % 100;
      return {
        id: unit.unitId,
        blockId: unit.blockId,
        block: unit.blockName,
        unit: unit.unitName,
        floor: unit.floor,
        stack: unit.floor != null && Number.isFinite(number) && inferred >= 1 && inferred <= 12 ? inferred : null,
        typology: unit.typology,
        subtypology: unit.subtypology,
        status: unit.status,
        statusCrm: unit.statusCrm,
        sold: unit.sold,
      };
    }),
  };
}

export function qualityRows(params: URLSearchParams) {
  const manifest = getManifest();
  const date = params.get("date") ?? manifest.latestDate;
  const issue = params.get("issue") ?? "floorMissing";
  const offset = Math.max(0, Number(params.get("offset") ?? 0));
  const limit = Math.min(1000, Math.max(1, Number(params.get("limit") ?? 200)));
  const rows = filterUnits(loadSnapshot(date), params, false).filter((unit) => issueMatch(unit, issue));
  return {
    total: rows.length,
    offset,
    limit,
    rows: rows.slice(offset, offset + limit).map((unit) => ({
      unitId: unit.unitId,
      city: unit.city,
      enterprise: unit.enterpriseName,
      block: unit.blockName,
      unit: unit.unitName,
      floor: unit.floor,
      reportedFloors: unit.reportedFloors,
      status: unit.statusRaw,
      statusCrm: unit.statusCrm,
      typology: unit.typology,
      subtypology: unit.subtypology,
    })),
  };
}

export function velocityData(): VelocityData {
  return readJson<VelocityData>("velocity.json");
}

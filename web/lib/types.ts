export type PageId = "overview" | "blocks" | "enterprise" | "velocity" | "quality";

export type Kpis = {
  total: number;
  sold: number;
  stock: number;
  consumption: number | null;
};

export type MetricRow = Kpis & Record<string, string | number | boolean | null | string[]>;

export type FilterState = {
  date: string;
  cities: string[];
  typologies: string[];
  statuses: string[];
};

export type EnterpriseOption = {
  id: string;
  name: string;
  city: string;
};

export type DashboardData = {
  meta: {
    snapshotDate: string;
    generatedAt: string;
    sourceFile: string | null;
    rowCount: number;
    scopeRows: number;
  };
  options: {
    dates: string[];
    cities: string[];
    typologies: string[];
    statuses: string[];
    enterprises: EnterpriseOption[];
  };
  kpis: Kpis;
  progressSummary: Array<{
    band: string;
    enterprises: number;
    stock: number;
    stockShare: number;
  }>;
  enterpriseProgress: Array<{
    id: string;
    city: string;
    name: string;
    band: string;
    total: number;
    sold: number;
    stock: number;
    consumption: number;
  }>;
  floors: Array<{ floor: number; total: number; sold: number; stock: number; consumption: number }>;
  floorBand: null | { low: Kpis; high: Kpis; lowMax: number; highMin: number };
  stockGroups: Array<{ group: string; units: number; share: number }>;
  stockStatuses: Array<{ status: string; units: number; share: number }>;
  quality: {
    clean: number;
    cleanShare: number;
    affected: number;
    issues: Array<{ label: string; key: string; count: number; share: number }>;
  };
};

export type UnitDetail = {
  id: string;
  blockId: string;
  block: string;
  unit: string;
  floor: number | null;
  stack: number | null;
  typology: string;
  subtypology: string;
  status: string;
  statusCrm: string;
  sold: boolean;
};

export type BlockOption = {
  id: string;
  label: string;
};

export type EnterpriseData = {
  enterprise: EnterpriseOption;
  blockOptions: BlockOption[];
  baseline: number;
  kpis: Kpis;
  blocks: Array<{
    id: string;
    name: string;
    label: string;
    total: number;
    sold: number;
    stock: number;
    consumption: number;
  }>;
  stacks: Array<{
    blockId: string;
    block: string;
    stack: number;
    total: number;
    sold: number;
    stock: number;
    consumption: number;
  }>;
  floors: Array<{ floor: number; total: number; sold: number; stock: number; consumption: number }>;
  stockGroups: Array<{ group: string; units: number; share: number }>;
  stockStatuses: Array<{ status: string; units: number; share: number }>;
  units: UnitDetail[];
};

export type VelocityData = {
  timeline: Array<{ snapshot_date: string; total: number; sold: number; stock: number; consumption: number }>;
  transitions: Array<{
    previous_date: string;
    snapshot_date: string;
    days: number;
    new_sales: number;
    reversals: number;
    net_sales: number;
    monthly_velocity: number | null;
    consumption_change_pp: number;
    added_units: number;
    removed_units: number;
  }>;
  method: {
    identity: string;
    saleRule: string;
    monthlyRule: string;
    coverage: string;
  };
};

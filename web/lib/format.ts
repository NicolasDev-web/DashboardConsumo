export const integer = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

export function pct(value: number | null | undefined, digits = 1) {
  if (value == null || Number.isNaN(value)) return "n.d.";
  return new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function dateLabel(value: string, withYear = true) {
  const [year, month, day] = value.slice(0, 10).split("-");
  return withYear ? `${day}/${month}/${year}` : `${day}/${month}`;
}

export function csvDownload(fileName: string, rows: Array<Record<string, unknown>>) {
  if (!rows.length) return;
  const columns = Object.keys(rows[0]);
  const escape = (value: unknown) => {
    const text = value == null ? "" : String(value);
    return `"${text.replaceAll('"', '""')}"`;
  };
  const csv = [columns.map(escape).join(";"), ...rows.map((row) => columns.map((key) => escape(row[key])).join(";"))].join("\n");
  const blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

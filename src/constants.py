from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "consumo.duckdb"
INITIAL_WORKBOOK = ROOT_DIR / "Dados" / "Dados-Bloco.xlsx"

SHEET_NAME = "POC"
HEADER_ROW = 1

REQUIRED_COLUMNS = {
    "ID Empreendimento",
    "ID Bloco",
    "ID da Unidade",
    "Cidade",
    "Empreendimento",
    "Bloco",
    "Unidade",
    "Status Unidade",
    "Pavimentos",
    "Posição Vertical",
}

OPTIONAL_COLUMNS = {
    "Tipologia",
    "Subtipologia",
    "Status Unidade CRM",
}

KNOWN_STATUSES = {
    "VENDIDO",
    "EXCLUSIVO PLATAFORMA",
    "NÃO LANÇADO",
    "PRÉ VENDA",
    "PERMUTADO",
    "BLOQUEADO",
    "RESERVADO COM CONTRATO PRE ATIVO",
    "LANÇADO",
    "RESERVA PARA PERMUTA",
    "RESERVADO",
}

COLORS = {
    "green_900": "#006B3F",
    "green_700": "#079D56",
    "green_500": "#00D38D",
    "green_300": "#82EA5B",
    "text": "#1A4236",
    "orange": "#FFB719",
    "error": "#BA4726",
    "purple": "#793F98",
    "surface": "#FFFFFF",
    "surface_subtle": "#F5F9F7",
    "border": "#D8E2DE",
    "muted": "#62766F",
    "stock": "#6B7280",
    "missing": "#E5E7EB",
}


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


# Leitura simplificada do estoque não vendido. A classificação oficial de venda
# continua sendo apenas ``VENDIDO``; estes grupos servem para explicar o estoque.
STATUS_GROUPS = {
    "EXCLUSIVO PLATAFORMA": "Em comercialização",
    "LANÇADO": "Em comercialização",
    "PRÉ VENDA": "Em comercialização",
    "RESERVADO": "Reservadas",
    "RESERVADO COM CONTRATO PRE ATIVO": "Reservadas",
    "NÃO LANÇADO": "Fora de venda",
    "BLOQUEADO": "Fora de venda",
    "PERMUTADO": "Fora de venda",
    "RESERVA PARA PERMUTA": "Fora de venda",
}
STATUS_GROUP_ORDER = ["Em comercialização", "Reservadas", "Fora de venda", "Outros status"]
STATUS_GROUP_HELP = {
    "Em comercialização": "Lançado, pré-venda ou exclusivo plataforma",
    "Reservadas": "Reservado, com ou sem contrato pré-ativo",
    "Fora de venda": "Não lançado, bloqueado ou destinado a permuta",
    "Outros status": "Status ainda não catalogado",
}

# Faixas de avanço de vendas por empreendimento: (rótulo, limite inferior).
PROGRESS_BANDS = [
    ("Menos de 50% vendido", 0.0),
    ("50% a 80% vendido", 0.5),
    ("80% a 95% vendido", 0.8),
    ("95% ou mais vendido", 0.95),
]
LOW_PROGRESS_LABEL = PROGRESS_BANDS[0][0]

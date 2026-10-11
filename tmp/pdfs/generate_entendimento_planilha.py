from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "entendimento_da_planilha_consumo_e_vendas.pdf"

GREEN = colors.HexColor("#006B3F")
GREEN_LIGHT = colors.HexColor("#E7F4ED")
TEXT = colors.HexColor("#1A4236")
MUTED = colors.HexColor("#5F746C")
BORDER = colors.HexColor("#D8E2DE")
BG = colors.HexColor("#F7FAF8")
AMBER = colors.HexColor("#FFF3CC")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, "Dashboard de consumo e estoque imobiliário")
    canvas.drawRightString(192 * mm, 8 * mm, f"Página {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleMRV",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=GREEN,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="SubtitleMRV",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
)
styles.add(
    ParagraphStyle(
        name="HeadingMRV",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=TEXT,
        spaceBefore=11,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyMRV",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallMRV",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=11.5,
        textColor=TEXT,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeaderMRV",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.3,
        leading=11.5,
        textColor=colors.white,
    )
)
styles.add(
    ParagraphStyle(
        name="CalloutMRV",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=16,
        textColor=GREEN,
        leftIndent=9,
        rightIndent=9,
        spaceBefore=6,
        spaceAfter=6,
    )
)


def p(text, style="BodyMRV"):
    return Paragraph(text, styles[style])


def bullet(text):
    return p(f"- {text}")


doc = BaseDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=17 * mm,
    bottomMargin=19 * mm,
    title="Como a planilha foi entendida",
    author="Dashboard de consumo e estoque imobiliário",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates([PageTemplate(id="content", frames=[frame], onPage=footer)])

story = [
    p("Como a planilha foi entendida", "TitleMRV"),
    p(
        "Resumo simples das regras usadas no dashboard para interpretar vendas, estoque, blocos, andares e prumadas.",
        "SubtitleMRV",
    ),
]

callout = Table(
    [[p("REGRA PRINCIPAL", "SmallMRV"), p("Uma unidade só conta como vendida quando o campo <b>Status Unidade</b> é exatamente <b>VENDIDO</b>, desconsiderando diferenças entre maiúsculas, minúsculas e espaços nas pontas.", "CalloutMRV")]],
    colWidths=[35 * mm, 139 * mm],
)
callout.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]
    )
)
story.extend([callout, p("1. Estrutura que identifiquei", "HeadingMRV")])
story.extend(
    [
        bullet("Cada linha representa uma unidade imobiliária."),
        bullet("A aba utilizada é <b>POC</b>, com os nomes das colunas na segunda linha do arquivo."),
        bullet("Empreendimento, bloco e unidade são identificados pelos respectivos IDs. O ID da unidade precisa existir e não pode estar duplicado."),
        bullet("<b>Posição Vertical</b> foi entendida como o andar da unidade. <b>Pavimentos</b> informa quantos andares o bloco declara possuir."),
        bullet("Tipologia, subtipologia e Status Unidade CRM complementam a análise, mas não definem sozinhos uma venda."),
    ]
)

story.append(p("2. Como os status sao usados", "HeadingMRV"))
status_rows = [
    [p("Leitura no dashboard", "TableHeaderMRV"), p("Status considerados", "TableHeaderMRV"), p("Interpretação", "TableHeaderMRV")],
    [p("Vendida", "SmallMRV"), p("VENDIDO", "SmallMRV"), p("Entra no número de unidades vendidas.", "SmallMRV")],
    [p("Em comercialização", "SmallMRV"), p("EXCLUSIVO PLATAFORMA, LANÇADO, PRÉ VENDA", "SmallMRV"), p("Ainda não vendida, mas disponível ou em fase comercial.", "SmallMRV")],
    [p("Reservada", "SmallMRV"), p("RESERVADO; RESERVADO COM CONTRATO PRÉ ATIVO", "SmallMRV"), p("Ainda não é contada como venda concluída.", "SmallMRV")],
    [p("Fora de venda", "SmallMRV"), p("NÃO LANÇADO, BLOQUEADO, PERMUTADO, RESERVA PARA PERMUTA", "SmallMRV"), p("Ainda não vendida e não tratada como disponibilidade comercial comum.", "SmallMRV")],
]
status_table = Table(status_rows, colWidths=[34 * mm, 72 * mm, 68 * mm], repeatRows=1)
status_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.45, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.extend([status_table, Spacer(1, 3 * mm)])

note = Table(
    [[p("Importante: esses grupos servem para explicar as unidades ainda não vendidas. Eles não mudam a regra principal: somente VENDIDO entra como venda.", "BodyMRV")]],
    colWidths=[174 * mm],
)
note.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AMBER), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3B341")), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
story.append(note)

story.append(p("3. Como os numeros sao calculados", "HeadingMRV"))
calc_rows = [
    [p("Número mostrado", "TableHeaderMRV"), p("Cálculo usado", "TableHeaderMRV")],
    [p("Unidades vendidas", "SmallMRV"), p("Quantidade de IDs únicos com Status Unidade = VENDIDO.", "SmallMRV")],
    [p("Total do bloco", "SmallMRV"), p("Quantidade total de IDs únicos naquele bloco.", "SmallMRV")],
    [p("Percentual vendido", "SmallMRV"), p("Unidades vendidas dividido pelo total de unidades do recorte.", "SmallMRV")],
    [p("Ainda não vendidas", "SmallMRV"), p("Total de unidades menos unidades vendidas.", "SmallMRV")],
]
calc_table = Table(calc_rows, colWidths=[55 * mm, 119 * mm], repeatRows=1)
calc_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.45, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
story.extend([calc_table, p("Exemplo: <b>16 vendidas - total 20 - 80%</b> significa que o bloco possui 20 unidades, 16 estão com status VENDIDO e 4 ainda não foram vendidas.")])

story.append(p("4. Bloco, andar e prumada", "HeadingMRV"))
story.extend(
    [
        bullet("A comparação por bloco usa o ID Bloco e o nome informado na planilha."),
        bullet("O andar vem diretamente de <b>Posição Vertical</b>; o dashboard não tenta adivinhar um andar ausente."),
        bullet("A planilha não possui uma coluna explícita de prumada. Por isso, a prumada é deduzida pelos dois últimos dígitos do número da unidade: 101, 201 e 301 pertencem à prumada 01."),
        bullet("Somente finais entre 01 e 12, com andar informado, entram na comparação de prumadas. Casos fora dessa regra continuam nos totais gerais, mas ficam fora do mapa."),
    ]
)

story.append(p("5. Conferencias e limites", "HeadingMRV"))
story.extend(
    [
        bullet("Status Unidade CRM é usado para sinalizar divergências, mas o Status Unidade continua sendo a referência oficial."),
        bullet("A aplicação avisa quando falta andar, quando o andar supera o número de pavimentos ou quando existe mais de uma unidade na mesma posição do espelho."),
        bullet("Consumo representa vendas observadas na planilha. Ele não mede procura, visitas, leads, propostas perdidas ou demanda reprimida."),
        bullet("Com um único snapshot vemos a situação acumulada. Para saber quantas vendas aconteceram em um período, são necessários pelo menos dois snapshots com datas diferentes."),
    ]
)

story.append(Spacer(1, 4 * mm))
story.append(p("Ponto para confirmação", "HeadingMRV"))
story.append(
    p(
        "A principal validação de negócio é confirmar se <b>apenas VENDIDO</b> deve representar uma venda concluída e se os demais agrupamentos refletem corretamente a situação comercial usada pela equipe.",
        "CalloutMRV",
    )
)

doc.build(story)
print(OUTPUT)

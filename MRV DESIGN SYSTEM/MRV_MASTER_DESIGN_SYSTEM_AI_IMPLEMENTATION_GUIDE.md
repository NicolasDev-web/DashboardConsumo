# MRV MASTER DESIGN SYSTEM & AI IMPLEMENTATION GUIDE

**Versão derivada do material:** *Comunicação Comercial - Versão 02 / Março 2020*  
**Objetivo:** transformar as diretrizes de marca fornecidas em regras operacionais reutilizáveis por agentes de IA, designers e desenvolvedores.  
**Idioma operacional:** português.  
**Escopo:** identidade verbal, identidade visual, comunicação de empreendimentos, MRV Class e tradução controlada para interfaces digitais.

---

## 0. REGRA DE LEITURA DESTE GUIA

Toda decisão relevante é classificada com um dos três níveis abaixo:

- **[OFICIAL]**: a regra está explicitamente presente no material fornecido ou é um dado objetivo diretamente verificável no arquivo.
- **[INFERIDO]**: a regra não é declarada como norma, mas aparece de maneira consistente nos exemplos e composições.
- **[RECOMENDADO]**: extensão criada para preencher lacunas do material, sobretudo para UI/UX, dashboards, responsividade, acessibilidade, motion e componentes digitais.

### 0.1 Limite importante do material

[OFICIAL] O próprio manual informa que ele cobre a identidade MRV para **comunicações comerciais** e pede que o “Território de marca MRV” seja consultado em conjunto com o material. Portanto, este guia é a consolidação mais completa possível do arquivo fornecido, mas não deve declarar como “oficial” aquilo que o PDF não define.

[RECOMENDADO] Em caso de conflito entre:
1. uma regra oficial mais recente da MRV;
2. este guia;
3. uma recomendação digital deste guia;

a ordem de prioridade deve ser **1 > 2 > 3**.

---

# 1. DNA VISUAL DA MRV

## 1.1 Síntese

[INFERIDO] Uma interface ou peça “parece MRV” quando combina:

- **verde como âncora de identidade**, especialmente o verde escuro;
- superfícies claras e bastante espaço em branco;
- acentos vivos de laranja, roxo, rosa, amarelo e verdes claros;
- formas geométricas com cantos arredondados e pequenas distorções;
- elementos em linha e elementos preenchidos coexistindo;
- composição baseada em **intersecção/sobreposição**, em vez de elementos isolados aleatórios;
- linguagem humana, otimista e próxima;
- fotografia de pessoas em situações de vida real, convivência e realização;
- tipografia Averta com hierarquia forte e títulos de grande presença;
- estética institucional + comercial, sem parecer excessivamente burocrática;
- energia visual sem cair em excesso de efeitos, sombras ou futurismo.

## 1.2 Personalidade de marca

[OFICIAL] A personalidade declarada é: **engajada, corajosa, acolhedora e íntegra**.  
[OFICIAL] O território verbal trabalha três atitudes: **Mobiliza**, **Realiza** e **Valoriza**.  
[OFICIAL] A mensagem central parte da ideia de transformação iniciada na casa e ampliada para o mundo.

### Tradução visual

- **Engajada** → hierarquia clara, chamadas diretas e elementos de ação visíveis.
- **Corajosa** → uso confiante de cor, blocos grandes e acentos marcantes.
- **Acolhedora** → pessoas, cenas reais, cantos moderadamente arredondados, linguagem próxima.
- **Íntegra** → layouts limpos, legíveis, sem truques visuais, excesso de ornamentação ou efeitos.

## 1.3 Nível de minimalismo

[INFERIDO] O sistema não é minimalista “frio”. Ele é **limpo, expressivo e humano**.  
A base tende a ser branca ou verde, com poucos elementos gráficos de grande impacto. Quando há grande densidade comercial, a informação é segmentada por blocos, boxes e cores.

## 1.4 Como reconhecer visualmente uma interface MRV

Uma aplicação deve passar neste checklist rápido:

- [ ] Existe verde MRV em posição estrutural, não apenas decorativa?
- [ ] O verde escuro atua como fio condutor?
- [ ] O layout usa branco/respiro suficiente?
- [ ] A cor secundária aparece como apoio, sem competir com a marca?
- [ ] As formas gráficas parecem pertencer à mesma família do símbolo MRV?
- [ ] Há intersecção, sobreposição ou diálogo entre formas quando grafismos são usados?
- [ ] A tipografia é Averta ou fallback compatível claramente identificado como não oficial?
- [ ] O conteúdo evita aparência excessivamente corporativa/burocrática?
- [ ] O visual é otimista, acolhedor e realizador?
- [ ] Sombras, vidro, glow e efeitos 3D de interface não dominam a composição?
- [ ] O logo permanece intacto e legível?
- [ ] A interface continua funcional e acessível?

---

# 2. IDENTIDADE VERBAL APLICADA A PRODUTOS DIGITAIS

## 2.1 Princípios

[OFICIAL] A linguagem comercial deve:
- estimular a imaginação do cliente;
- conhecer o cliente além da compra;
- apresentar o produto como parte de uma vida maior;
- lidar com objeções destacando qualidade e visão de longo prazo;
- criar expectativa positiva;
- construir relação;
- atuar com proatividade e empatia.

## 2.2 Regra para microcopy

[RECOMENDADO] Em aplicações:
- prefira verbos de ação;
- fale de forma humana e direta;
- evite juridiquês e burocratês quando não forem necessários;
- explique erros com caminho de recuperação;
- não use tom infantil;
- não use entusiasmo artificial em rotinas operacionais;
- para sistemas internos, preserve clareza e objetividade antes do tom publicitário.

Exemplo:
- Genérico: “Erro 422: operação inválida.”
- MRV recomendado: “Não foi possível concluir esta alteração. Revise os campos destacados e tente novamente.”

---

# 3. PALETA DE CORES

## 3.1 Fonte cromática oficial

[OFICIAL] O manual afirma que o **verde escuro** deve ter presença constante e significativa na comunicação de empreendimentos.  
[OFICIAL] A paleta foi ampliada com versões mais neutras derivadas da paleta institucional.  
[OFICIAL] Os degradês definidos no material devem seguir **ângulo de 45°**.

### 3.2 Paleta consolidada

| Token | Nome | HEX | RGB derivado do HEX | HSL derivado do HEX | Papel | Confiança/Fonte |
|---|---|---:|---:|---:|---|---|
| `mrv-green-900` | Verde escuro MRV | `#006B3F` | `0, 107, 63` | `155°, 100%, 21%` | primary | [OFICIAL] p. 41 |
| `mrv-green-700` | Verde médio | `#079D56` | `7, 157, 86` | `152°, 91%, 32%` | primary | [OFICIAL] p. 41 |
| `mrv-green-500` | Verde vivo | `#00D38D` | `0, 211, 141` | `160°, 100%, 41%` | primary | [OFICIAL] p. 41 |
| `mrv-green-300` | Verde claro | `#82EA5B` | `130, 234, 91` | `104°, 77%, 64%` | primary | [OFICIAL] p. 41 |
| `mrv-green-neutral-500` | Verde neutro | `#91A582` | `145, 165, 130` | `94°, 16%, 58%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-green-neutral-200` | Verde neutro claro | `#CDE1B3` | `205, 225, 179` | `86°, 43%, 79%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-orange-500` | Laranja | `#FF8B22` | `255, 139, 34` | `29°, 100%, 57%` | accent | [OFICIAL] p. 41 |
| `mrv-orange-300` | Amarelo-laranja | `#FFB719` | `255, 183, 25` | `41°, 100%, 55%` | accent | [OFICIAL] p. 41 |
| `mrv-orange-neutral-100` | Pêssego neutro | `#FCD9B4` | `252, 217, 180` | `31°, 92%, 85%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-purple-700` | Roxo | `#793F98` | `121, 63, 152` | `279°, 41%, 42%` | accent | [OFICIAL] p. 41 |
| `mrv-purple-500` | Violeta | `#AC41D8` | `172, 65, 216` | `283°, 66%, 55%` | accent | [OFICIAL] p. 41 |
| `mrv-purple-neutral-300` | Roxo neutro | `#C595C3` | `197, 149, 195` | `303°, 29%, 68%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-pink-600` | Rosa | `#F7287C` | `247, 40, 124` | `336°, 93%, 56%` | accent | [OFICIAL] p. 41 |
| `mrv-pink-400` | Rosa claro | `#FF5AAD` | `255, 90, 173` | `330°, 100%, 68%` | accent | [OFICIAL] p. 41 |
| `mrv-pink-neutral-200` | Rosa neutro | `#F7CBDD` | `247, 203, 221` | `335°, 73%, 88%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-yellow-400` | Amarelo | `#FFF028` | `255, 240, 40` | `56°, 100%, 58%` | accent | [OFICIAL] p. 41 |
| `mrv-yellow-neutral-100` | Amarelo neutro | `#FFEDA6` | `255, 237, 166` | `48°, 100%, 83%` | neutral-expanded | [OFICIAL] p. 41 |
| `mrv-support-green-dark` | Verde de apoio escuro | `#1A4236` | `26, 66, 54` | `162°, 43%, 18%` | restricted-support | [OFICIAL] p. 42 |
| `mrv-support-orange-dark` | Laranja de apoio escuro | `#BA4726` | `186, 71, 38` | `13°, 66%, 44%` | restricted-support | [OFICIAL] p. 42 |
| `mrv-support-purple-dark` | Roxo de apoio escuro | `#4D3366` | `77, 51, 102` | `271°, 33%, 30%` | restricted-support | [OFICIAL] p. 42 |
| `mrv-support-pink-dark` | Rosa de apoio escuro | `#8F3B6B` | `143, 59, 107` | `326°, 42%, 40%` | restricted-support | [OFICIAL] p. 42 |
| `mrv-support-brown` | Marrom de apoio | `#916133` | `145, 97, 51` | `29°, 48%, 38%` | restricted-support | [OFICIAL] p. 42 |
| `mrv-class-green-950` | Verde profundo MRV Class | `#00331F` | `0, 51, 31` | `156°, 100%, 10%` | class-primary | [OFICIAL] p. 68 |

### 3.3 Observação de consistência do arquivo

[OFICIAL] Na página 41, o swatch com HEX `#FCD9B4` aparece acompanhado por um RGB textual que não corresponde matematicamente ao HEX.  
[RECOMENDADO] Para implementação digital, tratar o **HEX impresso como valor canônico** e derivar RGB/HSL automaticamente dele, evitando manter representações conflitantes.

## 3.4 Cores principais

[OFICIAL]
- `#006B3F` deve ser o principal verde estrutural.
- `#079D56`, `#00D38D` e `#82EA5B` formam a progressão verde de apoio.
- Laranja, roxo, rosa e amarelo pertencem à identidade e podem criar energia e diferenciação.

## 3.5 Cores de apoio com uso restrito

[OFICIAL] `#1A4236`, `#BA4726`, `#4D3366`, `#8F3B6B` e `#916133` são derivações mais escuras e devem atuar como apoio, principalmente em **textos** ou **logos de empreendimentos**, sem protagonismo cromático.

## 3.6 MRV Class

[OFICIAL]
- cores principais: branco + `#00331F`;
- verdes `#006B3F` e `#00D38D` permanecem como secundários;
- a sensação deve ser mais refinada e leve.

## 3.7 Paleta semântica para UI

> Esta subseção é [RECOMENDADO]. O manual não define estados digitais.

- `success`: `#006B3F`
- `success-emphasis`: `#079D56`
- `warning`: `#FFB719`, com texto escuro
- `error/destructive`: `#BA4726`
- `info`: `#793F98`
- `focus`: `#00D38D`
- `disabled-surface`: `rgba(26, 66, 54, 0.08)`
- `disabled-text`: `rgba(26, 66, 54, 0.45)`
- `border-subtle`: `rgba(26, 66, 54, 0.18)`
- `surface-subtle`: `rgba(0, 107, 63, 0.04)`

A estratégia acima reutiliza cores oficiais e transparência, evitando criar uma paleta cinza paralela desnecessária.

## 3.8 Regras de contraste

[RECOMENDADO]
- `#006B3F` com branco tem contraste alto e é apropriado para botões e textos invertidos.
- `#00331F` com branco é adequado para MRV Class.
- cores muito claras (`#82EA5B`, `#FFF028`, `#FFB719`, `#00D38D`) **não devem receber texto branco** em conteúdos importantes; usar `#1A4236` ou outro tom escuro aprovado.
- não depender apenas de cor para comunicar erro, sucesso ou tendência.

---

# 4. TIPOGRAFIA

## 4.1 Família oficial

[OFICIAL] A família tipográfica institucional é **Averta**.

[OFICIAL] O manual explicita:
- Averta Regular / Regular Italic;
- Averta Light / Light Italic;
- Averta Bold / Bold Italic;
- Averta Black / Black Italic.

[OFICIAL] Para MRV Class:
- versões Bold deixam de ser a linguagem principal;
- entram pesos mais leves;
- aparecem Averta Light, Regular e Extrathin.

[INFERIDO] O próprio PDF também utiliza pesos adicionais da família, incluindo Semibold e ExtraBold. Isso comprova uso no material, mas não deve ser transformado automaticamente em regra oficial de produto.

## 4.2 Fallbacks

[RECOMENDADO] Ordem de fallback quando Averta não estiver legalmente/licenciadamente disponível:

```css
font-family: "Averta", "Manrope", "Avenir Next", "Inter", Arial, sans-serif;
```

Nunca extraia ou redistribua arquivos de fonte do PDF.

## 4.3 Tracking

[OFICIAL]
- títulos/logos podem variar tracking de forma controlada;
- elementos da mesma hierarquia, na mesma peça, devem manter o mesmo tracking;
- **não alterar tracking de texto corrido**;
- na MRV Class, títulos e destaques usam caixa alta e tracking maior.

## 4.4 Escala tipográfica digital

> Valores abaixo são [RECOMENDADO], derivados da hierarquia visual do material.

| Papel | Desktop | Mobile | Peso MRV | Line-height | Tracking |
|---|---:|---:|---|---:|---:|
| Display | 56 px | 40 px | ExtraBold/Black | 1.05 | -0.02em |
| H1 | 40 px | 32 px | ExtraBold/Bold | 1.15 | -0.01em |
| H2 | 32 px | 28 px | Bold | 1.2 | 0 |
| H3 | 24 px | 22 px | Bold/Semibold | 1.3 | 0 |
| H4 | 20 px | 18 px | Semibold | 1.35 | 0 |
| Subtitle | 18 px | 17 px | Semibold | 1.45 | 0 |
| Body Large | 18 px | 17 px | Regular | 1.55 | 0 |
| Body | 16 px | 16 px | Regular | 1.5 | 0 |
| Body Small | 14 px | 14 px | Regular | 1.45 | 0 |
| Caption | 12 px | 12 px | Regular | 1.35 | 0 |
| Label | 13 px | 13 px | Semibold | 1.3 | 0.01em |
| Button | 15 px | 15 px | Bold/Semibold | 1.3 | 0 |
| Table | 14 px | 14 px | Regular | 1.4 | 0 |
| Navigation | 14 px | 14 px | Semibold | 1.4 | 0 |

### MRV Class

[RECOMENDADO]
- troque H1/H2 em Bold por Regular/Light;
- títulos preferencialmente em caixa alta com tracking entre `0.06em` e `0.12em`;
- evite Black/ExtraBold;
- preserve contraste por tamanho, respiro e cor, não por peso pesado.

## 4.5 Combinações a evitar

- [OFICIAL] fonte fora da família Averta em logos de empreendimentos.
- [OFICIAL] tracking exagerado.
- [OFICIAL] tracking alterado em texto corrido.
- [RECOMENDADO] mais de 3 pesos tipográficos em uma mesma tela operacional.
- [RECOMENDADO] serifas decorativas ou fontes futuristas como linguagem principal.

---

# 5. GRID, ESPAÇAMENTO E PROPORÇÕES

## 5.1 Padrão observado

[INFERIDO]
- o material usa áreas amplas de branco;
- títulos e conteúdo têm forte alinhamento;
- composições importantes ocupam blocos claramente separados;
- elementos de cor são usados para criar foco, não para preencher todas as superfícies;
- layouts promocionais densos são segmentados em boxes, cores e imagens.

## 5.2 Sistema de espaçamento

[RECOMENDADO] Use base de 4 px:

`4 / 8 / 12 / 16 / 24 / 32 / 40 / 48 / 64 / 80`

Tokens:
- `spacing.2xs = 4`
- `spacing.xs = 8`
- `spacing.sm = 12`
- `spacing.md = 16`
- `spacing.lg = 24`
- `spacing.xl = 32`
- `spacing.2xl = 48`
- `spacing.3xl = 64`

## 5.3 Grid de aplicação

[RECOMENDADO]
- Desktop: 12 colunas, gutter 24 px, margem 32-64 px.
- Tablet: 8 colunas, gutter 20 px, margem 24 px.
- Mobile: 4 colunas, gutter 16 px, margem 16 px.
- Sistemas internos densos podem usar containers fluidos; landing pages podem limitar conteúdo a 1200-1320 px.

## 5.4 Regra de densidade

- marketing/institucional → mais respiro;
- dashboards → densidade média;
- tabelas operacionais → densidade alta, mas agrupada;
- nunca reduzir respiro a ponto de o verde, títulos e estados perderem hierarquia.

---

# 6. FORMAS E GEOMETRIA

## 6.1 Gramática oficial/inferida

[OFICIAL] Os grafismos devem preservar a lógica de **intersecção/sobreposição** e não podem ser descaracterizados.  
[OFICIAL] Há formas combinadas, com parte preenchida e parte em linha.  
[OFICIAL] Em peças com muito conteúdo podem existir boxes com cantos arredondados e leves distorções, sempre com parcimônia.  
[OFICIAL] Em layouts com muitas imagens, cantos retos devem prevalecer para evitar repetição excessiva de formas.  
[OFICIAL] Em MRV Class, formas em linha podem aparecer isoladas, regulares, rotacionadas e sem distorção; o sistema é mais leve.

## 6.2 Raios digitais

> [RECOMENDADO]

- button: `8px`
- input/select: `8px`
- card: `12px`
- modal: `16px`
- toast: `10px`
- table container: `8px`
- badge: `6px` ou pill apenas quando a semântica pedir
- imagem de marketing: 0-16 px conforme composição; não arredondar todas as imagens

Evitar `24px+` como padrão universal.

---

# 7. SOMBRAS E PROFUNDIDADE

[INFERIDO] A linguagem base é predominantemente **flat**, dependente de cor, linha, composição e espaço, não de sombras.

[RECOMENDADO]

- `elevation.0`: nenhuma sombra;
- `elevation.1`: `0 1px 2px rgba(26,66,54,.08)`;
- `elevation.2`: `0 4px 12px rgba(26,66,54,.10)`;
- `elevation.3`: `0 12px 28px rgba(26,66,54,.14)` apenas modal/popover importante.

Não usar:
- glow;
- neon;
- glassmorphism como linguagem principal;
- sombras escuras grandes em todos os cards.

---

# 8. COMPONENTES DE UI

> O manual não especifica componentes de software. Esta seção é **[RECOMENDADO]**, construída para traduzir os códigos oficiais para produto digital.

## 8.1 Botões

### Primary
- fundo: `#006B3F`
- texto: branco
- altura: 44 px desktop, 48 px mobile
- padding horizontal: 16-24 px
- radius: 8 px
- fonte: Averta Semibold/Bold, 15 px
- hover: `#079D56`
- active: `#1A4236`
- focus: ring 2 px `#00D38D`
- ícone: 18-20 px

### Secondary
- fundo branco
- borda 1 px `#006B3F`
- texto `#006B3F`
- hover: `rgba(0,107,63,.06)`

### Tertiary/Ghost
- fundo transparente
- texto `#006B3F`
- hover `rgba(0,107,63,.06)`

### Destructive
- fundo `#BA4726`
- texto branco
- sempre acompanhado de texto/ícone que comunique o risco

### Disabled
- fundo `rgba(26,66,54,.08)`
- texto `rgba(26,66,54,.45)`
- sem sombra

### Loading
- preservar largura;
- spinner de 16-18 px;
- não substituir o rótulo por layout instável.

## 8.2 Inputs

- altura mínima: 44 px;
- mobile: 48 px;
- border: 1 px `rgba(26,66,54,.24)`;
- radius: 8 px;
- label acima do campo;
- focus: 2 px `#00D38D`;
- error: `#BA4726` + mensagem textual;
- placeholder não pode ser a única label;
- textarea com mínimo de 3 linhas.

Checkbox/radio/switch:
- estado ativo em `#006B3F`;
- focus visível;
- área clicável mínima de 44×44 px.

## 8.3 Cards

- fundo branco;
- borda sutil;
- sombra opcional no máximo elevation 1;
- radius 12 px;
- padding 16-24 px;
- um acento de cor pode identificar categoria;
- não transformar cada informação em card.

## 8.4 Modais

- largura desktop: 480-720 px;
- mobile: largura quase total;
- radius 16 px;
- overlay `rgba(0,51,31,.40)`;
- título forte;
- CTA principal à direita no desktop, empilhado no mobile;
- foco preso dentro do modal.

## 8.5 Dropdowns e menus

- branco;
- radius 8-10 px;
- elevation 2;
- item mínimo 40 px;
- selecionado com fundo verde translúcido e texto escuro.

## 8.6 Tooltips

- fundo `#1A4236`;
- texto branco;
- 12-13 px;
- no máximo 2-3 linhas;
- não colocar informação essencial exclusivamente em tooltip.

## 8.7 Badges

- status positivo: verde;
- aviso: amarelo/laranja com texto escuro;
- erro: `#BA4726`;
- informativo: roxo;
- usar baixa saturação/alpha para o fundo e tom escuro para texto.

## 8.8 Alerts

Estrutura:
- barra/ícone de estado;
- título curto;
- descrição;
- ação opcional.

Nunca depender somente da cor.

## 8.9 Tabs

- ativo: texto `#006B3F` + underline 2-3 px;
- inativo: `rgba(26,66,54,.65)`;
- evitar pill tabs gigantes como padrão.

## 8.10 Breadcrumbs

- 14 px;
- item atual em `#1A4236`;
- anteriores em verde clicável;
- usar em estruturas profundas, não em telas simples.

## 8.11 Sidebar

- fundo branco ou `#00331F/#006B3F` conforme contexto;
- ativo claramente destacado;
- ícones lineares customizados no espírito MRV;
- largura recomendada 240 px, colapsada 72 px;
- evitar sidebar preta genérica.

## 8.12 Header

- 56-64 px em sistema interno;
- logo com área de proteção;
- fundo branco ou verde escuro;
- ações secundárias não competem com o título da página.

## 8.13 Footer

- discreto;
- contatos/institucional;
- verde escuro ou branco;
- não usar grafismos excessivos.

## 8.14 Tabelas

- cabeçalho com forte contraste;
- linhas de 44-52 px;
- zebra apenas por alpha sutil;
- números alinhados à direita;
- texto à esquerda;
- filtros fora da tabela quando possível;
- ações de linha agrupadas;
- primeira coluna pode ser sticky;
- em mobile, priorizar colunas ou converter em cards somente quando necessário.

## 8.15 Paginação

- controles compactos;
- ativo em verde escuro;
- 36-40 px por controle;
- sempre informar faixa exibida em tabelas densas.

## 8.16 Filtros

- filtros principais visíveis;
- avançados em drawer/popover;
- chips apenas para filtros aplicados;
- botão “Limpar filtros” com baixa ênfase.

## 8.17 KPI cards

- valor > rótulo > contexto;
- valor 28-36 px;
- máximo de uma cor de destaque por KPI;
- tendência positiva/negativa deve ter ícone + texto, não só cor.

## 8.18 Empty states

- ilustração leve compatível com a marca;
- título objetivo;
- explicação;
- CTA;
- não usar mascotes infantis genéricos.

## 8.19 Loading

- skeleton com baixa opacidade;
- spinner verde;
- evitar animações chamativas.

## 8.20 Toasts

- largura 320-420 px;
- duração 4-6 s quando não crítico;
- ação opcional;
- ícone + estado + mensagem.

---

# 9. DASHBOARDS E SISTEMAS INTERNOS

## 9.1 Princípio

[RECOMENDADO] Um dashboard MRV não deve parecer um material promocional transformado em software.  
O correto é **traduzir os códigos**, não reproduzir banners comerciais dentro de uma ferramenta de trabalho.

## 9.2 Arquitetura visual

- fundo predominantemente claro;
- verde escuro no header/sidebar/ações principais;
- cards brancos;
- bordas sutis;
- acentos vivos reservados para dados e estados;
- títulos em Averta;
- grafismos de marca apenas em pontos institucionais, empty states ou onboarding;
- baixa sombra;
- consistência acima de variedade.

## 9.3 Alta densidade de dados

- usar espaçamento 8/12/16 dentro de blocos densos;
- manter 24/32 entre seções;
- usar agrupamento visual;
- evitar mais de 5 cores simultâneas;
- congelar cabeçalhos em tabelas;
- usar tooltips para detalhe secundário;
- não comprometer escaneabilidade com grafismos decorativos.

---

# 10. DATA VISUALIZATION

> [RECOMENDADO]

## 10.1 Ordem cromática sugerida

Para séries categóricas:
1. `#006B3F`
2. `#FF8B22`
3. `#793F98`
4. `#F7287C`
5. `#FFB719`

Séries adicionais devem preferir subtons/neutros antes de adicionar novas cores.

## 10.2 Charts

### Bar
- radius 2-4 px, não “pill”;
- grid horizontal leve;
- série principal verde.

### Line
- stroke 2-3 px;
- pontos apenas quando úteis;
- hover com foco claro.

### Donut
- usar para poucas categorias;
- evitar mais de 5 segmentos;
- legenda próxima.

### Stacked
- ordenar cores por importância;
- não usar tons quase indistinguíveis.

### Heatmap
- preferir escala verde monocromática;
- inserir valor textual quando contraste for limitado.

## 10.3 Regras

- fundo branco;
- grid `rgba(26,66,54,.10)`;
- labels `#1A4236`;
- legenda 12-14 px;
- tooltip branco com borda/sombra sutil;
- evitar 3D;
- evitar gradientes decorativos sem significado;
- jamais comunicar tendência só por cor.

---

# 11. ICONOGRAFIA

## 11.1 Regra oficial

[OFICIAL]
- o estilo reflete a construção da marca;
- combina partes preenchidas e partes em linha;
- utiliza intersecção;
- novos ícones devem se basear no grid **16×16** mostrado no manual;
- o exemplo de construção usa 160×160 px com células de 10 px;
- ícones podem ser usados como composição;
- subtons e combinações de cor são permitidos com moderação e sem comprometer contraste/harmonia.

## 11.2 MRV Class

[OFICIAL]
- linhas notavelmente mais finas;
- mesmas cores da identidade Class;
- grid 16×16 preservado.

## 11.3 Biblioteca digital

[RECOMENDADO] Para prototipagem, Lucide/Phosphor podem servir apenas como base estrutural.  
Para telas finais de marca:
- normalize stroke;
- introduza preenchimento parcial quando fizer sentido;
- adapte geometria ao sistema MRV;
- evite misturar 3 bibliotecas na mesma aplicação.

Tamanho padrão de UI: 20/24 px.

---

# 12. IMAGENS E FOTOGRAFIA

## 12.1 MRV

[INFERIDO]
- foco em pessoas;
- convivência;
- família;
- cotidiano;
- ambientes habitáveis;
- sensação positiva e próxima;
- composição espontânea, não excessivamente posada.

## 12.2 MRV Class

[OFICIAL]
- estética um pouco mais sofisticada;
- maior presença de branco;
- diferenciação sutil;
- mantém os pilares: **otimista, acolhedor e realizador**.

## 12.3 Regras de aplicação

- não aplicar bordas arredondadas em todas as fotos;
- com muitas imagens, preferir cantos retos;
- evitar fotografia corporativa de escritório como padrão de experiência de marca;
- evitar filtros agressivos;
- evitar saturação artificial;
- manter legibilidade quando texto sobrepõe imagem.

---

# 13. ILUSTRAÇÃO

As regras mais detalhadas estão na seção MRV Class do material.

[OFICIAL]
- ilustração reforça lado positivo e descontraído;
- expressões faciais/corporais ajudam a construir o conceito;
- priorizar relações entre pessoas;
- buscar traços brasileiros e identificação;
- considerar diversidade;
- manter atuação espontânea e natural;
- evitar personagens excessivamente estáticos ou agitados;
- cenário não deve ser vazio demais nem complexo demais;
- evitar ambiente burocrático/corporativo;
- retratar realidade do consumidor;
- leves distorções de proporção são permitidas, sem tornar a cena irreal;
- evitar estilo infantil ou editorial/moda adulto;
- 3D é permitido;
- ultra-realismo 3D deve ser evitado, pois se aproxima de fotografia.

---

# 14. LOGOTIPO E MARCA

## 14.1 Área de proteção

[OFICIAL] A área de proteção é construída com **2x**, em que `x` deriva da distância entre a forma e a parte tipográfica da marca.

## 14.2 Prioridade de versões

[OFICIAL]
1. versão principal com degradês + lettering verde escuro;
2. versão secundária quando houver limitação para degradês;
3. P&B apenas quando nenhuma versão anterior for possível;
4. monocromática quando houver necessidade de uma cor.

## 14.3 Box

[OFICIAL]
- uso restrito a comunicações comerciais/parceiros quando não há controle de layout/cores;
- utilizar arquivo original;
- nunca recriar o box manualmente;
- versão recortada somente no canto inferior direito;
- não cortar/deslocar;
- manter box branco e logo principal positivo.

## 14.4 Fundos

[OFICIAL]
- versão principal positiva sobre branco;
- versão principal negativa sobre verde escuro;
- demais fundos: versão monocromática;
- evitar fundos próximos às cores da marca ou que prejudiquem leitura.

## 14.5 Tamanho mínimo

[OFICIAL]
- impresso: **20 mm**
- digital: **70 px**

## 14.6 Usos indevidos

[OFICIAL]
- não alterar cor;
- não distorcer;
- não alterar diagramação;
- não adicionar elementos/efeitos;
- não criar versões não previstas.

## 14.7 Parcerias

[OFICIAL] O alinhamento e dimensionamento consideram a base tipográfica do logo e distância definida pela medida `y`, com exemplos usando `3y` entre marcas.

---

# 15. RESPONSIVIDADE

> O manual não define breakpoints. Tudo abaixo é [RECOMENDADO].

## 15.1 Breakpoints

- `sm`: 480 px
- `md`: 768 px
- `lg`: 1024 px
- `xl`: 1280 px
- `2xl`: 1440 px

## 15.2 Desktop

- sidebar + header em sistemas internos;
- grid de 12 colunas;
- dashboards até 4 KPIs por linha;
- tabelas completas.

## 15.3 Tablet

- sidebar colapsável;
- 2 KPIs por linha;
- filtros em drawer;
- redução de grafismos decorativos.

## 15.4 Mobile

- navegação em drawer/bottom nav conforme produto;
- 1 KPI por linha quando informação exigir contexto;
- ações primárias com 48 px de altura;
- modais viram bottom sheet/fullscreen quando necessário;
- tabelas devem priorizar colunas, scroll horizontal controlado ou detalhe por linha;
- manter logo acima do mínimo oficial de 70 px quando exibido.

## 15.5 O que nunca deve mudar

- cores oficiais;
- integridade do logo;
- hierarquia de ação;
- legibilidade;
- foco visível;
- identidade tipográfica;
- caráter acolhedor/objetivo.

---

# 16. ACESSIBILIDADE

> [RECOMENDADO], com prioridade sobre escolhas puramente estéticas.

- WCAG AA como mínimo;
- texto normal: contraste ≥ 4.5:1;
- texto grande: ≥ 3:1;
- focus sempre visível;
- área de toque mínima 44×44 px;
- não usar verde/rosa isoladamente para significado;
- gráficos precisam de labels, padrões ou ícones;
- respeitar `prefers-reduced-motion`;
- zoom 200% sem perda funcional;
- ordem de foco coerente;
- labels persistentes em formulários.

Combinações seguras:
- branco sobre `#006B3F`;
- branco sobre `#00331F`;
- branco sobre `#1A4236`;
- texto `#1A4236` sobre cores claras como `#82EA5B`, `#FFB719`, `#FFF028`, `#00D38D`.

---

# 17. MOTION E ANIMAÇÕES

> [RECOMENDADO]

## 17.1 Princípios

- movimento funcional;
- sensação rápida, positiva e fluida;
- nada de bounce excessivo;
- nada de parallax pesado em sistemas internos;
- não animar grandes áreas só por estética.

## 17.2 Tokens

- `motion.fast = 120ms`
- `motion.base = 180ms`
- `motion.slow = 240ms`
- `motion.emphasis = 320ms`
- easing padrão: `cubic-bezier(.2,.8,.2,1)`

## 17.3 Uso

- hover: 120-180 ms;
- dropdown/modal: 180-240 ms;
- drawer: 240-320 ms;
- skeleton: discreto;
- feedback de sucesso: microanimação curta;
- `prefers-reduced-motion`: remover translação/escala não essencial.

---

# 18. DESIGN TOKENS

## 18.1 Tokens CSS essenciais

```css
:root {
  --mrv-green-900: #006B3F;
  --mrv-green-700: #079D56;
  --mrv-green-500: #00D38D;
  --mrv-green-300: #82EA5B;

  --mrv-orange-500: #FF8B22;
  --mrv-orange-300: #FFB719;
  --mrv-purple-700: #793F98;
  --mrv-purple-500: #AC41D8;
  --mrv-pink-600: #F7287C;
  --mrv-pink-400: #FF5AAD;
  --mrv-yellow-400: #FFF028;

  --mrv-text-primary: #1A4236;
  --mrv-class-green-950: #00331F;

  --mrv-surface: #FFFFFF;
  --mrv-surface-subtle: rgba(0, 107, 63, .04);
  --mrv-border-subtle: rgba(26, 66, 54, .18);

  --mrv-radius-button: 8px;
  --mrv-radius-card: 12px;
  --mrv-radius-modal: 16px;

  --mrv-space-1: 4px;
  --mrv-space-2: 8px;
  --mrv-space-3: 12px;
  --mrv-space-4: 16px;
  --mrv-space-6: 24px;
  --mrv-space-8: 32px;
  --mrv-space-12: 48px;
  --mrv-space-16: 64px;
}
```

## 18.2 Mapeamento para frameworks

### Tailwind
- `colors.mrv.green.900 -> #006B3F`
- `fontFamily.mrv -> Averta`
- `borderRadius.mrvCard -> 12px`
- `spacing` baseado em 4 px

### React
- consumir tokens por CSS variables ou theme object;
- evitar hardcode de HEX em componentes;
- expor variantes `primary|secondary|ghost|destructive`.

### Figma
- criar Variables Collections:
  - `Brand/Color`
  - `Semantic/Color`
  - `Typography`
  - `Spacing`
  - `Radius`
  - `Elevation`
- marcar semantic colors como derivadas dos brand tokens.

### Flutter
- `ColorScheme.primary = #006B3F`
- `ColorScheme.secondary = #00D38D`
- `fontFamily = Averta`
- `ThemeData` com radius e component themes derivados dos tokens.

---

# 19. REGRAS DE DECISÃO PARA AGENTES DE IA

Quando um agente receber uma aplicação existente para converter ao padrão MRV, seguir exatamente esta sequência:

## 19.1 Analisar estrutura existente
- mapear páginas;
- componentes;
- navegação;
- estados;
- densidade;
- fluxos críticos;
- responsividade.

## 19.2 Identificar o que destoa
Marcar:
- cores não MRV;
- fontes;
- sombras;
- radius;
- ícones;
- cards;
- gráficos;
- excesso de decoração;
- logo incorreto.

## 19.3 Preservar lógica e funcionalidade
Nunca quebrar:
- regra de negócio;
- cálculo;
- dados;
- integração;
- navegação;
- acessibilidade existente.

## 19.4 Substituir cores
- aplicar `#006B3F` como âncora;
- reduzir cores não MRV;
- migrar estados para aliases semânticos.

## 19.5 Ajustar tipografia
- Averta primeiro;
- fallback apenas se necessário;
- reconstruir hierarquia;
- não alterar tracking de body.

## 19.6 Corrigir espaçamento
- normalizar em base 4 px;
- eliminar valores arbitrários;
- aumentar respiro macro.

## 19.7 Adequar componentes
- bordas/radius;
- estados;
- alturas;
- sombras;
- foco.

## 19.8 Adequar ícones
- uma família;
- 20/24 px;
- stroke consistente;
- customização MRV em pontos de marca.

## 19.9 Adequar gráficos
- paleta MRV;
- labels claros;
- sem 3D;
- sem rainbow desnecessário.

## 19.10 Responsividade
- não apenas encolher;
- reordenar;
- priorizar;
- colapsar navegação;
- preservar área de toque.

## 19.11 Revisar consistência
Comparar componentes repetidos e remover divergências.

## 19.12 Validar acessibilidade
Contraste, teclado, foco, labels, leitores de tela e reduced motion.

---

# 20. MATRIZ “ELEMENTO ATUAL → ELEMENTO MRV”

| Elemento atual | Conversão MRV |
|---|---|
| Botão azul genérico | botão `#006B3F`, Averta, radius 8, foco `#00D38D` |
| Card com sombra forte | card branco, borda sutil, elevation 0-1 |
| Sidebar preta | branca ou verde MRV, ativo claramente identificado |
| Roboto genérica | Averta; fallback somente quando necessário |
| Dashboard multicolor | verde como série principal + acentos oficiais controlados |
| Tabela Bootstrap padrão | cabeçalho MRV, linhas 44-52 px, borda sutil |
| Alert vermelho saturado | `#BA4726` + ícone + mensagem |
| Input sem label | label persistente + foco verde |
| Ícones misturados | uma família, 20/24 px, stroke consistente |
| Imagens todas arredondadas | mistura controlada; cantos retos em galerias densas |
| Glassmorphism | superfície branca/verde, flat, borda/sombra mínima |
| Gradiente azul-roxo | remover; usar paleta MRV e gradiente de 45° somente quando coerente |
| CTA neon | verde escuro ou acento oficial |
| Header preto | branco/verde escuro MRV |
| KPI com 5 cores | uma cor principal + estado semântico |
| Modal pesado | branco, radius 16, overlay verde profundo translúcido |

---

# 21. O QUE NÃO FAZER

## 21.1 Anti-patterns diretamente sustentados pelo material

- [OFICIAL] alterar cor do logo;
- [OFICIAL] distorcer logo;
- [OFICIAL] alterar diagramação do logo;
- [OFICIAL] adicionar efeitos ao logo;
- [OFICIAL] recriar box do logo manualmente;
- [OFICIAL] usar versão de box fora das situações previstas;
- [OFICIAL] ignorar área de proteção;
- [OFICIAL] comprometer legibilidade do logo no fundo;
- [OFICIAL] usar cores de apoio escuras como protagonistas;
- [OFICIAL] exagerar tracking;
- [OFICIAL] alterar tracking de texto corrido;
- [OFICIAL] excesso de formas;
- [OFICIAL] excesso de cantos arredondados em composições com muitas imagens;
- [OFICIAL] grafismos descaracterizados/sem sobreposição quando a identidade normal exige a relação entre formas;
- [OFICIAL] ilustração infantil demais ou editorial adulta demais;
- [OFICIAL] acting estático ou exageradamente agitado;
- [OFICIAL] cenário corporativo/burocrático como linguagem de ilustração;
- [OFICIAL] 3D ultra-realista em substituição a fotografia.

## 21.2 Anti-patterns digitais

[RECOMENDADO]
- glassmorphism como base;
- dark mode preto puro com neon;
- border-radius exagerado;
- 4+ níveis de sombra;
- gradientes inventados;
- cores fora da paleta sem justificativa;
- animação chamativa;
- interface “futurista de IA” genérica;
- todos os blocos virarem cards;
- ícones multicoloridos sem regra;
- layout promocional aplicado diretamente em ferramenta operacional;
- excesso de rosa/amarelo/roxo competindo com o verde;
- usar logo como padrão decorativo;
- usar imagem de fundo atrás de texto sem contraste.

---

# 22. MRV CLASS - SUBSISTEMA

MRV Class não é uma nova marca desconectada; é uma variação mais sofisticada.

## 22.1 Chaves de diferenciação

[OFICIAL]
- branco com presença maior;
- verde profundo `#00331F`;
- pesos tipográficos mais leves;
- títulos em caixa alta com tracking maior;
- elementos gráficos em linha;
- formas isoladas regulares/rotacionadas;
- linhas mais finas;
- imagens com cantos retos;
- até duas formas por composição;
- fotografia mais clara e refinada;
- ícones com linhas mais finas.

## 22.2 Regra de decisão

Use MRV Class apenas quando a aplicação/material pertence explicitamente à Linha Class.  
Não misture os códigos de Class com o sistema MRV padrão por preferência estética.

---

# 23. CHECKLIST FINAL — “ESTA APLICAÇÃO REALMENTE PARECE MRV?”

## Marca
- [ ] logo original;
- [ ] versão correta;
- [ ] área de proteção;
- [ ] mínimo 70 px digital;
- [ ] fundo compatível.

## Cor
- [ ] verde escuro é âncora;
- [ ] cores secundárias são apoio;
- [ ] sem cores aleatórias;
- [ ] contraste acessível;
- [ ] estados não dependem só de cor.

## Tipografia
- [ ] Averta;
- [ ] hierarquia consistente;
- [ ] body sem tracking alterado;
- [ ] pesos limitados;
- [ ] Class usa pesos leves quando aplicável.

## Forma
- [ ] grafismos coerentes;
- [ ] sem excesso;
- [ ] radius moderado;
- [ ] intersecção quando identidade normal usa grafismos;
- [ ] Class com formas leves/isoladas.

## Componentes
- [ ] botões consistentes;
- [ ] inputs com labels;
- [ ] foco visível;
- [ ] cards sem sombra excessiva;
- [ ] tabelas escaneáveis;
- [ ] filtros claros.

## Dados
- [ ] verde é série principal;
- [ ] até ~5 cores por visual;
- [ ] sem 3D;
- [ ] labels/legenda acessíveis;
- [ ] tendência não depende só de cor.

## Imagens
- [ ] pessoas/cenas coerentes;
- [ ] aparência acolhedora;
- [ ] sem saturação exagerada;
- [ ] cantos não arredondados indiscriminadamente.

## Mobile
- [ ] não é desktop encolhido;
- [ ] 44×44 px mínimo de toque;
- [ ] navegação adaptada;
- [ ] tabelas priorizadas;
- [ ] logo legível.

## Acessibilidade
- [ ] WCAG AA;
- [ ] teclado;
- [ ] foco;
- [ ] labels;
- [ ] reduced motion;
- [ ] zoom 200%.

## Consistência geral
- [ ] parece MRV sem depender do logo?
- [ ] é humana, otimista, acolhedora e objetiva?
- [ ] evita aparência de template genérico?
- [ ] recomendações digitais estão claramente separadas das regras oficiais?

---

# 24. CONTRATO OPERACIONAL PARA AGENTES

Ao aplicar este guia, o agente deve obedecer às seguintes regras:

1. **Não inventar regra oficial.**
2. **Não modificar logo.**
3. **Não criar cores de marca novas sem necessidade.**
4. **Preservar lógica e funcionalidade antes de redesenhar.**
5. **Tratar o verde escuro como âncora.**
6. **Usar cor secundária de maneira seletiva.**
7. **Usar Averta como fonte oficial.**
8. **Reduzir efeitos visuais genéricos.**
9. **Preferir composição, espaço, cor e tipografia a sombras.**
10. **Manter grafismos coerentes com a lógica da marca.**
11. **Respeitar diferenças entre MRV padrão e MRV Class.**
12. **Validar acessibilidade antes de concluir.**
13. **Ao preencher lacunas, marcar a decisão como [RECOMENDADO].**
14. **Ao deduzir padrões de exemplos, marcar como [INFERIDO].**
15. **Se uma nova diretriz oficial contradizer este guia, a nova diretriz vence.**

---

# 25. RESUMO DE IMPLEMENTAÇÃO EM UMA FRASE

> **Use uma base clara e organizada, ancore a experiência no verde escuro MRV, utilize Averta, mantenha cores secundárias como acentos controlados, preserve a geometria/intersecção da marca, trabalhe com pessoas e situações reais e evite efeitos digitais genéricos que substituam a identidade por tendência.**

---

## Referências internas do material analisado

- p. 1: escopo e obrigação de consulta ao território de marca;
- p. 2-19: estratégia e identidade verbal comercial;
- p. 20-38: identidade visual, logo e iconografia;
- p. 39-66: identidade de empreendimentos, cores, logos, boas práticas e selos;
- p. 67-93: MRV Class, cores, tipografia, grafismos, fotografia, ilustração, ícones e boas práticas;
- p. 94: encerramento.

**Fim do MRV MASTER DESIGN SYSTEM & AI IMPLEMENTATION GUIDE.**

# Dashboard de consumo e estoque imobiliário

Dashboard de vendas por empreendimento, bloco, prumada e andar. A versão principal fica em `web/`, usa Next.js e foi preparada para rodar no Vercel sem servidor Python e sem autenticação.

O Streamlit original continua preservado em `app.py` para conferência local. A planilha e o DuckDB ficam no computador; o Vercel recebe somente os arquivos JSON já validados e gerados pelo pipeline.

## Rodar a versão web localmente

```powershell
python -m pipeline.ingest --export-only
cd web
npm install
npm run dev
```

Abra `http://localhost:3000`.

## Atualizar os dados

Para importar uma nova foto e atualizar os arquivos usados pelo site:

```powershell
python -m pipeline.ingest --file "Dados\nova-base.xlsx" --date 2026-10-15
```

Se já existir uma foto na mesma data e a intenção for substituí-la:

```powershell
python -m pipeline.ingest --file "Dados\nova-base.xlsx" --date 2026-10-15 --replace
```

O comando valida a planilha, atualiza `data/consumo.duckdb` e recria `web/data-generated/`. Depois, revise as alterações, rode os testes e envie os arquivos gerados ao GitHub. O próximo deploy do Vercel passa a usar a nova foto.

## Publicar no Vercel

1. Importe este repositório no Vercel.
2. Defina **Root Directory** como `web`.
3. Mantenha o preset **Next.js** e os comandos automáticos detectados pelo Vercel.
4. Não é necessário cadastrar variáveis de ambiente.
5. Publique o projeto.

Como não há login, a URL publicada e os dados exibidos nela ficam acessíveis a qualquer pessoa que possua o endereço.

## Verificações

```powershell
pytest -q
cd web
npm run verify
```

## Estrutura

- `pipeline/ingest.py`: importa, valida e gera os dados estáticos da aplicação.
- `web/app/api/`: recorta e agrega os dados no servidor Next.js.
- `web/components/`: telas e componentes do dashboard.
- `web/data-generated/`: snapshots versionados consumidos pelo deploy.
- `src/` e `app.py`: aplicação Streamlit preservada.

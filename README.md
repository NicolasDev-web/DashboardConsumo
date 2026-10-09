# Dashboard de consumo e estoque imobiliário

Aplicação local em Streamlit construída a partir do SDD do projeto e estilizada com os tokens do MRV Design System.

## Executar

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Na primeira abertura, informe a data do snapshot e clique em **Carregar base inicial**. A planilha original não é alterada; os snapshots validados são persistidos localmente em `data/consumo.duckdb`.

## Funcionalidades

- visão geral com KPIs, concentração de estoque e leitura por andar;
- comparação de blocos e espelho operacional de unidades por andar e prumada inferida;
- detalhe do empreendimento e exportação do recorte;
- velocidade de vendas entre snapshots;
- painel de qualidade e histórico de importações;
- filtros encadeados e exportações CSV UTF-8 com BOM.

## Testes

```powershell
pytest -q
```

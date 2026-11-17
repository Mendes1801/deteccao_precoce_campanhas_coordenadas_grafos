# Entrega N2 — Inteligência Artificial

**Projeto:** Detecção precoce de campanhas coordenadas em redes sociais por meio da evolução de grafos temporais

Universidade Presbiteriana Mackenzie

**Disciplina:** Inteligência Artificial — 7ºK SI
**Professor:** Prof. Dr. Leandro Zerbinatti

## Integrantes
- Camila N. Carniel — RA: **10338558-0**
- Bruno G. Ramalho — RA: **1042649-1**

> E-mails não foram fornecidos e, portanto, não foram incluídos.

## Artefatos

- [Relatório atualizado](Relatório%20do%20Projeto.md)
- [Notebook: EDA inicial](notebooks/01_eda_inicial_len.ipynb)
- [Notebook: EDA aprofundada e grafos parciais](notebooks/02_eda_aprofundada_len.ipynb)
- [Módulos Python reutilizáveis](../../src/len_eda/)
- [Testes automatizados](../../tests/)
- [Configuração de exclusão da duplicata](../../config/len_small_exclusions.csv)
- [Instruções gerais e comandos de reprodução](../../README.md)

O código-fonte e os módulos compartilhados ficam no repositório público, enquanto o relatório, os roteiros, os slides e os notebooks desta entrega estão reunidos na pasta `IA_7K_SI_Camila&Bruno/`. Os módulos Python contêm cabeçalhos com integrantes, síntese e histórico de alterações.

## Dataset

O projeto usa o **Large Engagement Networks (LEN)**, especificamente o subconjunto LEN-small disponibilizado pelos autores. Cada arquivo JSON representa um grafo direcionado de interações: nós correspondem a usuários e arestas armazenam relações como retuítes, respostas ou citações, com timestamp e `Interaction_Count`. O rótulo do arquivo indica `campaign` ou `noncampaign`. Os vetores de atributos de alta dimensão são ignorados nesta análise porque sua disponibilidade temporal não foi validada.

- Fonte oficial e documentação: [Large Engagement Network](https://erdemub.github.io/large-engagement-network/)
- Publicação de referência: Gopalakrishnan et al. (2025), [DOI 10.1609/icwsm.v19i1.35839](https://doi.org/10.1609/icwsm.v19i1.35839)
- Download: obter o pacote LEN-small conforme as instruções dos autores e colocá-lo localmente em `small_encoder_final/`.
- Reprodução da tabela de estados parciais:

```bash
len-features \
  --data-dir small_encoder_final \
  --exclusions config/len_small_exclusions.csv \
  --output outputs/partial_graph_features.csv

len-evaluate \
  --features outputs/partial_graph_features.csv \
  --mode events \
  --output outputs/partial_graph_metrics.csv
```

O dataset oficial LEN-small está presente localmente na pasta `small_encoder_final/` e o `.gitignore` não exclui mais essa pasta. A amostra contém 104 arquivos; a configuração documenta uma duplicata byte a byte, restando 103 grafos únicos locais (52 campanhas e 51 não campanhas). A documentação do LEN-small descreve 100 grafos; a diferença de três arquivos continua registrada no relatório. Antes de redistribuir os dados brutos, conferir os termos e a licença da fonte oficial.

## Publicação e vídeo

- Repositório público: [Mendes1801/deteccao_precoce_campanhas_coordenadas_grafos](https://github.com/Mendes1801/deteccao_precoce_campanhas_coordenadas_grafos)
- Vídeo público no YouTube (máximo de 5 minutos): **[inserir URL após publicação]**

# Entrega N2 — Inteligência Artificial

**Projeto:** Detecção precoce de campanhas coordenadas em redes sociais por meio da evolução de grafos temporais

**Instituição:** Universidade Presbiteriana Mackenzie, Faculdade de Computação e Informática

**Disciplina:** Inteligência Artificial — 7ºK SI, Noite
**Professor:** Prof. Dr. Leandro Zerbinatti

## Integrantes

- Camila Nunes Carniel — RA: **[preencher]** — e-mail: **[preencher]**
- Bruno Germanetti — RA: **[preencher]** — e-mail: **[preencher]**

> Os RAs e e-mails precisam ser preenchidos pelos integrantes antes da publicação final. Não foram inferidos para evitar dados incorretos.

## Artefatos

- [Relatório atualizado](Relatório%20do%20Projeto.md)
- [Notebook: EDA inicial](../notebooks/01_eda_inicial_len.ipynb)
- [Notebook: EDA aprofundada e grafos parciais](../notebooks/02_eda_aprofundada_len.ipynb)
- [Módulos Python reutilizáveis](../src/len_eda/)
- [Testes automatizados](../tests/)
- [Configuração de exclusão da duplicata](../config/len_small_exclusions.csv)
- [Instruções gerais e comandos de reprodução](../README.md)

O código-fonte e os notebooks ficam na raiz do mesmo repositório público para evitar cópias divergentes dentro da pasta do relatório. Os módulos Python contêm cabeçalhos com integrantes, síntese e histórico de alterações; os identificadores pessoais permanecem pendentes até confirmação dos integrantes.

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
```

Os arquivos brutos não estão versionados neste repositório: a pasta local é ignorada pelo Git e não está presente nesta cópia do workspace. A amostra inspecionada continha 104 arquivos; a configuração documenta uma duplicata byte a byte, restando 103 grafos únicos locais (52 campanhas e 51 não campanhas). A documentação do LEN-small descreve 100 grafos; a diferença de três arquivos continua pendente e está registrada no relatório. Antes de redistribuir os dados, conferir os termos e a licença da fonte oficial.

## Publicação e vídeo

- Repositório público: [Mendes1801/deteccao_precoce_campanhas_coordenadas_grafos](https://github.com/Mendes1801/deteccao_precoce_campanhas_coordenadas_grafos)
- Vídeo público no YouTube (máximo de 5 minutos): **[inserir URL após publicação]**

O endereço do vídeo também deve ser inserido no relatório após a publicação. O vídeo deve apresentar a equipe, a instituição, a disciplina e o professor; explicar o problema, os fundamentos de IA utilizados e a solução; demonstrar o artefato e a área pública do GitHub.

## Histórico desta entrega

- 11/11/2026 — Grupo — Complementação do pacote N2, documentação do dataset, links de artefatos e pendências de publicação.

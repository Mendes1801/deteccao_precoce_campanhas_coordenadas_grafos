# Rede de votos dos deputados

Este diretório contém uma demonstração de análise de concordância entre votos
nominais de deputados federais. O script consulta a API de Dados Abertos da
Câmara, monta uma rede não direcionada e detecta comunidades com Louvain.

## Requisitos

Na raiz do projeto, crie e ative o ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

As dependências usadas pela análise são `requests`, `networkx` e `pandas`, já
declaradas no `pyproject.toml`.

## Execução

Execute a partir da raiz do projeto:

```bash
python DEPUTADOS/rede_votacoes.py
```

```bash
python DEPUTADOS/rede_votacoes.py \
  --limite-votacoes 10 \
  --pasta-saida /tmp/grafos-deputados-teste
```

## Exportar dados de votação

Para baixar todos os metadados das votações e os votos nominais de um ano pela
API da Câmara, execute:

```bash
python DEPUTADOS/exportar_votacoes.py --ano 2026
```

O exportador consulta a API mês a mês (o endpoint limita o intervalo por
consulta), segue todas as páginas e salva os registros completos em
`DEPUTADOS/dados/votacoes_2026.jsonl` e
`DEPUTADOS/dados/votos_nominais_2026.jsonl`. Cada linha é um objeto JSON;
`idVotacao` relaciona cada voto nominal à votação correspondente. Os arquivos
finais só são substituídos quando a coleta termina com sucesso. A API retorna
os dados disponíveis no momento da consulta; votações futuras ainda não
realizadas não aparecerão nos arquivos. Se a listagem incluir uma votação cujo
endpoint nominal retorne HTTP 404, os metadados dela são preservados e o caso é
informado no terminal; outros erros interrompem a coleta.

## Arquivos gerados

Os resultados completos são gravados em `DEPUTADOS/grafos/`:

- `rede_deputados.graphml`: grafo para análise em NetworkX e outras ferramentas.
- `rede_deputados.gexf`: grafo para visualização, por exemplo, no Gephi.
- `rede_deputados.jpg`: imagem do grafo com cores por comunidade e tamanho dos
   nós proporcional ao grau.
- `grafo_influencia_bastidor.jpg`: visualização com as dez maiores
   intermediações destacadas por estrelas.
- `ranking_influencia_estrutural.csv`: métricas de ponte e ranking de todos os
   deputados.
- `comunidades_deputados.csv`: deputado, partido, comunidade detectada e grau
  (número de conexões do deputado no grafo).

Os dois arquivos de grafo incluem o partido de cada nó, o número da comunidade,
o peso de cada aresta e os parâmetros do período analisado. A saída do terminal
também lista o tamanho e a composição partidária das comunidades.

## Como o código funciona

1. `criar_sessao` configura a sessão HTTP e retentativas para erros temporários
   da API, inclusive limites de requisição.
2. `obter_paginas` segue o link `next` da API até reunir todas as páginas. Isso
   evita limitar a análise aos primeiros resultados retornados.
3. `coletar_votacoes` consulta as votações do período e registra, para cada
   deputado, seu voto e partido. Votações sem votos nominais são ignoradas.
4. `construir_grafo` cria um nó por deputado e compara cada par nas votações em
   que os dois têm um voto registrado. Só considera o par se houver pelo menos
   cinco votações em comum. O peso da aresta é calculado assim:

   ```text
   concordância = votações com o mesmo tipo de voto / votações em comum
   ```

   Os tipos de voto são comparados literalmente: por exemplo, `Sim` com `Sim`
   concorda, enquanto `Sim` com `Não` não concorda. Um deputado sem voto
   registrado naquela votação não entra no cálculo daquele par; ausência não é
   considerada discordância. Uma aresta é criada quando a taxa é maior ou igual
   a 70%, e seu atributo `weight` recebe essa taxa. Por exemplo, 7 votos iguais
   em 10 votações comuns resultam em concordância de 0,70 e criam uma aresta;
   6 em 10 resultam em 0,60 e não criam.
5. `detectar_comunidades` aplica Louvain com semente fixa para tornar os
   resultados reproduzíveis e grava a comunidade como atributo dos nós.
6. `salvar_grafos` exporta a rede nos formatos GraphML e GEXF e salva a tabela
   CSV com os resultados por deputado.

## Análise de influência estrutural

Com o GraphML já gerado, calcule as métricas sem refazer as consultas à API:

```bash
python DEPUTADOS/analisar_influencia.py
```

O ranking usa intermediação ponderada (betweenness): para calcular caminhos,
cada aresta recebe distância `1 / concordância`, de modo que conexões com maior
concordância sejam mais curtas. Também informa o grau, a quantidade e a fração de
conexões com outras comunidades e a força total dessas conexões. A lista é
ordenada principalmente pela intermediação; as outras medidas ajudam a
interpretar a posição de cada deputado.

Não há informação de cargos de liderança ou de articulação informal nessa base;
nenhum parlamentar é incluído ou excluído por ocupar esses cargos. Portanto, o
ranking identifica posições estruturais de ponte na rede de votos, não comprova
influência de bastidor, poder causal ou atividade política fora das votações.

## Visualização interativa

Com o grafo GraphML já gerado, crie a visualização interativa em HTML:

```bash
python DEPUTADOS/pyvis_exploracao.py
```

O arquivo `DEPUTADOS/grafos/rede_deputados_pyvis.html` pode ser aberto
diretamente em um navegador. A página usa recursos JavaScript carregados de uma
CDN, portanto precisa de conexão com a internet para exibir a rede.

## Interpretação e limitações

O grafo representa semelhança de votos no período escolhido, não prova
coordenação política. Como a taxa considera somente votações em comum, ela não
mede participação geral nem similaridade sobre votações em que um dos deputados
esteve ausente. O mínimo de cinco votações compartilhadas reduz comparações com
pouca evidência, mas não elimina esse limite. Comunidades Louvain são grupos
estruturais da rede e não equivalem necessariamente a partidos ou blocos formais.

Os parâmetros estão no início de `rede_votacoes.py`: `DATA_INICIO`, `DATA_FIM`,
`LIMIAR_CONCORDANCIA` e `MIN_VOTACOES_JUNTOS`.
# Etapa 1 — Configuração inicial e EDA do LEN

**Data de conclusão:** 09/09/2026  
**Status:** concluída e congelada como registro da preparação inicial dos dados.

## Objetivo da etapa

Preparar um ambiente reproduzível para abrir o LEN-small, verificar sua estrutura
e produzir uma primeira tabela de métricas por grafo. Nesta etapa não foram
treinados classificadores, baselines ou GNNs.

## Ambiente utilizado

| Componente | Versão/valor | Finalidade |
| --- | --- | --- |
| Sistema operacional | Linux 6.18.13-arch1-1 (x86_64) | Ambiente local de execução |
| Python | 3.14.3 | Linguagem principal |
| Ambiente virtual | `.venv` | Isolamento das bibliotecas do projeto |
| ijson | 3.5.1 | Leitura incremental dos JSONs grandes |
| pandas | 3.0.5 | Organização e análise das tabelas |
| NetworkX | 3.6.1 | Apoio à análise de grafos |
| Matplotlib | 3.11.1 | Geração de gráficos |
| Seaborn | 0.13.2 | Visualização estatística |
| JupyterLab | 4.6.3 | Execução dos notebooks |
| pytest | 9.1.1 | Testes automatizados |

As dependências aceitas pelo projeto estão registradas em `pyproject.toml`. Para
usar o ambiente, deve-se ativá-lo com `source .venv/bin/activate`.

## O que foi feito

1. Foi criado o ambiente virtual Python e instaladas as bibliotecas necessárias
   para a primeira fase de análise exploratória.
2. Foi implementado um leitor incremental para os JSONs do LEN. Ele evita
   carregar os vetores textuais completos na memória e produz uma linha de
   resumo para cada grafo.
3. Foi criada a tabela `outputs/len_small_summary.csv`, contendo métricas como
   número de nós e arestas, densidade, graus, reciprocidade, componentes,
   duração e cobertura temporal.
4. Foi criado o notebook `notebooks/01_eda_inicial_len.ipynb` para abrir a
   tabela, comparar as classes, gerar gráficos simples e verificar a qualidade
   dos dados. Cada bloco de código possui uma explicação em Markdown.
5. Foi criado um teste automatizado para o leitor de grafos. O teste foi
   executado com sucesso.

## Principais informações encontradas

| Informação verificada | Resultado encontrado | Implicação para a pesquisa |
| --- | --- | --- |
| Arquivos locais | 104 grafos JSON | O pacote local deve ser conferido antes do split experimental |
| Classes | 53 campanhas e 51 não campanhas | A classificação binária é possível, mas a amostra precisa ser congelada |
| Nós totais | 212.231 | Os grafos possuem tamanho suficiente para exigir leitura eficiente |
| Arestas totais | 289.975 | A estrutura de interação é rica para métricas de rede e tempo |
| Tipo dos grafos | Todos direcionados e não multigrafos | As métricas devem respeitar a direção das interações |
| Timestamps | 100% das arestas possuem timestamp | É possível ordenar eventos e criar grafos parciais |
| Ordem temporal no arquivo | Nenhum arquivo já está ordenado | As arestas devem ser ordenadas por `timestamp` antes de cada experimento temporal |
| Integridade básica | Sem IDs de nós duplicados ou endpoints ausentes | Não foi detectado problema estrutural nesses critérios |
| Atributos vetoriais | `node_attr` com 772 posições e `edge_attr` com 776 | Esses vetores foram ignorados nesta EDA e exigem validação temporal antes de uso |
| Valores fora do JSON padrão | Alguns arquivos possuem `NaN` | O leitor converte `NaN` para nulo somente durante a leitura; os dados brutos não foram alterados |

Também foi identificado um par de arquivos byte a byte idêntico:
`#SesimiziDuyanVarMi___2023-03-23_campaign_fulldata.json` e
`#SesimiziDuyanVarMı___2023-03-23_campaign_fulldata.json`.

O pacote local possui 104 arquivos, enquanto a documentação do LEN-small
descreve 100 grafos, sendo 51 campanhas e 49 não campanhas. Essa diferença não
foi corrigida nesta etapa; ela deverá ser resolvida e documentada antes da
definição dos conjuntos de treino, validação e teste.

## Cuidados metodológicos registrados

- O LEN mantém somente a interação mais recente entre cada par ordenado de
  usuários. Portanto, os grafos parciais representarão as arestas retidas pela
  base, e não todo o fluxo original de interações.
- As arestas precisam ser ordenadas explicitamente por `timestamp` antes da
  geração das janelas temporais.
- O atributo `kcore` não deve ser usado nos grafos parciais, pois foi calculado
  sobre o grafo completo e pode introduzir informação futura no experimento.
- A divisão entre treino, validação e teste deverá ocorrer por campanha antes da
  criação das janelas temporais, evitando vazamento entre diferentes estágios
  de uma mesma rede.

## Observação inicial sobre os atributos e o primeiro treinamento

Os nós e as arestas possuem, respectivamente, os atributos vetoriais
`node_attr` e `edge_attr`. A base informa que eles representam características
numéricas dos perfis e das interações, mas a composição detalhada e a ordem de
cada posição desses vetores ainda não foram verificadas nesta etapa. Portanto,
eles não serão usados inicialmente.

Como primeira estratégia de treinamento, pretende-se considerar apenas os
campos `source`, `target`, `timestamp` e `Interaction_Count` das arestas. Com
eles será possível reconstruir os grafos parciais e calcular características
estruturais e temporais, como número de usuários ativos, número de interações,
graus, densidade, componentes, reciprocidade e velocidade de crescimento.

Os dados dos nós serão descartados no primeiro baseline. Essa decisão busca
reduzir o processamento e impedir que usuários que só aparecem em estágios
posteriores da rede sejam incluídos antecipadamente no modelo. A utilidade dos
atributos de nós e dos vetores `node_attr` e `edge_attr` poderá ser testada em
uma etapa posterior, desde que sua disponibilidade temporal seja comprovada e
que seu uso não introduza vazamento de informação futura.

## Estrutura produzida

| Local | Conteúdo |
| --- | --- |
| `.venv/` | Ambiente virtual utilizado nesta etapa |
| `src/len_eda/summary.py` | Leitor incremental e cálculo das métricas iniciais |
| `tests/test_summary.py` | Teste automatizado do leitor |
| `outputs/len_small_summary.csv` | Tabela derivada com uma linha por grafo |
| `notebooks/01_eda_inicial_len.ipynb` | Notebook da EDA inicial |
| `docs/guia_ambiente_e_fluxo.md` | Guia de uso do ambiente e organização dos próximos experimentos |

O notebook `01` deve ser mantido como registro da EDA inicial. Cada nova
pergunta de pesquisa deverá ser desenvolvida em um notebook novo e numerado;
por exemplo, validação temporal, geração de grafos parciais, extração de
features e treinamento de baseline.

## Próxima etapa prevista

Definir a lista canônica de grafos do LEN-small e criar o procedimento de
ordenação temporal e geração de grafos parciais nas frações de 10%, 20%, ...,
100%. Somente depois disso deverão ser extraídas as features estruturais e
temporais usadas pelo primeiro baseline.

## Referência da base

GOPALAKRISHNAN, A. A.; HOSSAIN, J.; ELMAS, T.; SARIYÜCE, A. E. *Large
Engagement Networks for Classifying Coordinated Campaigns and Organic Twitter
Trends*. Proceedings of the International AAAI Conference on Web and Social
Media, v. 19, n. 1, p. 688–702, 2025. DOI: 10.1609/icwsm.v19i1.35839.

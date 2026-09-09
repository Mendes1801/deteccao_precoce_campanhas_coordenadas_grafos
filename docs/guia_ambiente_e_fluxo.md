# Guia do ambiente e do fluxo de pesquisa

Este documento descreve o estado atual do projeto e a forma recomendada de
avancar a pesquisa sem misturar experimentos ou perder a reprodutibilidade.

## Estado atual

O ambiente local foi criado em `.venv/` com Python 3.14.3. As dependencias
instaladas para esta fase sao `ijson`, `pandas`, `NetworkX`, `Matplotlib`,
`Seaborn`, `JupyterLab` e `pytest`. As faixas de versao que o projeto aceita
estao registradas em `pyproject.toml`; as versoes efetivamente validadas foram:

| Biblioteca | Versao instalada |
| --- | --- |
| ijson | 3.5.1 |
| pandas | 3.0.5 |
| NetworkX | 3.6.1 |
| Matplotlib | 3.11.1 |
| Seaborn | 0.13.2 |
| JupyterLab | 4.6.3 |
| pytest | 9.1.1 |

Nao ha nenhum processo em execucao continua. O comando `len-summary` so le o
dataset quando voce o chama; o JupyterLab so inicia quando voce executa
`jupyter lab`. Nenhum classificador, baseline ou GNN foi treinado nesta etapa.

## O que ja foi executado

1. O pacote `small_encoder_final` foi inspecionado sem modificar os arquivos
   originais.
2. Foi criado o comando `len-summary`, que le os JSONs de modo incremental e
   ignora os grandes vetores de texto durante a EDA inicial.
3. O comando foi executado sobre os 104 arquivos locais e gerou
   `outputs/len_small_summary.csv`, com uma linha por grafo.
4. O leitor verificou 212.231 nos e 289.975 arestas no pacote local. Todos os
   grafos sao direcionados, possuem timestamps em todas as arestas e nao
   apresentam endpoints ausentes ou IDs de nos duplicados.
5. O teste automatizado em `tests/test_summary.py` passou. O notebook inicial
   tambem foi executado integralmente para validar suas celulas.

O CSV dentro de `outputs/` e um resultado derivado: ele pode ser apagado e
recriado com o mesmo comando. Por isso, essa pasta e ignorada pelo Git.

## Estrutura do projeto

```text
small_encoder_final/       dados brutos do LEN; nao editar
src/len_eda/               codigo reutilizavel para leitura e metricas
tests/                     testes do codigo reutilizavel
notebooks/                 analises exploratorias numeradas
outputs/                   tabelas, figuras e resultados reproduziveis
docs/                      decisoes e guias metodologicos
pyproject.toml             dependencias e configuracao do projeto
```

A separacao tem uma funcao pratica: notebook serve para contar a historia de
uma analise; `src/` serve para codigo que precisara ser repetido, testado ou
usado por mais de um notebook.

## Como usar o ambiente

No terminal, a partir da raiz do projeto:

```bash
source .venv/bin/activate
pytest
```

Para refazer a tabela inicial sobre todos os grafos:

```bash
len-summary \
  --data-dir small_encoder_final \
  --output outputs/len_small_summary.csv
```

Para um teste rapido, sem processar todo o conjunto:

```bash
len-summary --data-dir small_encoder_final --limit 5
```

Para abrir a EDA inicial:

```bash
jupyter lab notebooks/01_eda_inicial_len.ipynb
```

Se o CSV ainda nao existir, a segunda celula de codigo do notebook o cria
automaticamente. Isso pode levar alguns minutos, porque os arquivos somam
cerca de 5,4 GB.

## Regra para os notebooks

O notebook `01_eda_inicial_len.ipynb` e a referencia da primeira EDA. Ele deve
ser preservado como registro do que foi observado inicialmente; sao aceitaveis
correcoes claras, explicacoes e pequenos ajustes, mas analises de novas
perguntas nao devem ser acumuladas nele.

Para cada objetivo novo, crie um notebook numerado e com nome descritivo. Por
exemplo:

```text
02_validacao_temporal_len.ipynb
03_grafos_parciais_por_janela.ipynb
04_features_estruturais_e_temporais.ipynb
05_baseline_logistic_regression.ipynb
```

Em cada notebook novo:

1. Comece com uma celula Markdown que declare a pergunta, a hipotese e quais
   dados entram na analise.
2. Reutilize funcoes de `src/` em vez de copiar logica extensa entre notebooks.
3. Salve tabelas e figuras em uma subpasta de `outputs/` com nome do
   experimento.
4. Registre parametros, versao dos dados, data e conclusoes em Markdown.
5. Quando uma transformacao for reutilizavel, mova-a para `src/` e crie um
   teste correspondente em `tests/`.

Essa estrategia deixa cada resultado rastreavel: e possivel saber qual pergunta
gerou cada figura, quais parametros foram usados e como repetir a analise.

## Proximo fluxo de pesquisa

1. Definir uma lista canonica dos grafos do LEN-small. O pacote local possui
   104 arquivos, mas a documentacao do LEN-small menciona 100; existe pelo
   menos um par de arquivos identicos. Essa decisao deve ser registrada antes
   do primeiro split experimental.
2. Criar o notebook `02_validacao_temporal_len.ipynb` para confirmar a ordenacao
   das arestas por `timestamp` e descrever a duracao de cada rede. Os arquivos
   nao estao ordenados cronologicamente, portanto todo codigo futuro deve
   ordenar as arestas explicitamente.
3. Implementar em `src/` uma funcao que gere grafos parciais em 10%, 20%, ...,
   100% da evolucao observada. O notebook `03` deve testar e documentar essa
   funcao.
4. Extrair as primeiras features estruturais e temporais por janela e gerar a
   primeira tabela de atributos. Somente depois disso faz sentido iniciar o
   baseline.

## Regras metodologicas que ja valem

- Nunca altere os JSONs em `small_encoder_final/`.
- Separe treino, validacao e teste por campanha antes de criar as janelas
  temporais.
- Nao use `kcore` nos grafos parciais: esse atributo foi calculado a partir do
  grafo completo e introduz informacao futura.
- O LEN mantem apenas a interacao mais recente para cada par ordenado de
  usuarios. Assim, a reconstrucao temporal representa as arestas retidas pelo
  dataset, e nao todo o fluxo original de interacoes.

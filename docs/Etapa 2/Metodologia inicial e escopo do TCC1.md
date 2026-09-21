# Etapa 2 — Metodologia inicial e escopo do TCC1

**Data da decisão:** 21/09/2026

**Marco final do TCC1:** entrega do pôster até 09/11/2026

**Base experimental inicial:** LEN-small

## 1. Decisão metodológica principal

No TCC1 serão usados modelos clássicos alimentados por características
estruturais e temporais calculadas sobre grafos parciais. A Regressão Logística
será o baseline principal, por ser simples e interpretável, e o Random Forest
será a comparação não linear.

GNNs não fazem parte do resultado mínimo exigido para o pôster. Elas ficam como
extensão do TCC2, depois que o protocolo temporal e os baselines estiverem
validados. Essa escolha não afirma que GNNs são inadequadas ao problema. Ela
decorre de três limitações concretas desta etapa:

1. o LEN-small possui aproximadamente 100 grafos independentes; os snapshots do
   mesmo grafo não são novas amostras independentes;
2. os vetores de nós e arestas têm origem temporal ainda insuficientemente
   documentada para uso em detecção precoce;
3. antes de aumentar a complexidade do modelo, é necessário verificar se o
   resultado não é explicado apenas pela grande diferença de tamanho entre as
   classes.

Uma GNN estática, como GraphSAGE ou GIN, poderá ser adicionada posteriormente
como comparação sobre os mesmos snapshots. Modelos temporais como TGN não serão
priorizados enquanto o dataset não fornecer a sequência completa de interações.

## 2. Objetivo objetivo até o fim do TCC1

Ao final do TCC1, o trabalho deverá apresentar uma **prova experimental
reproduzível** de como a capacidade de distinguir campanhas de não campanhas
varia conforme a quantidade de rede observada.

O resultado mínimo deverá conter:

- uma lista canônica e documentada dos grafos usados;
- um gerador testado de grafos parciais por fração do tempo e por fração das
  arestas observadas;
- uma tabela reproduzível de características estruturais e temporais para 10%,
  20%, ..., 100% de cada grafo;
- uma EDA que descreva qualidade, tamanho, tempo, intensidade, conectividade,
  redundância entre features e diferenças entre as classes;
- uma divisão por grafo em treino, validação e teste, mantida igual para todos
  os snapshots;
- um baseline simples treinado sem vazamento temporal;
- curvas de desempenho por fração observada e uma análise preliminar das
  features mais úteis;
- relatório parcial e pôster com limitações explicitadas.

O TCC1 não precisa entregar uma GNN, um modelo pronto para produção, resultados
no LEN completo, análise do conteúdo textual ou uma afirmação definitiva sobre
qual arquitetura é a melhor.

## 3. Formulação do experimento

### 3.1 Unidade experimental e rótulo

A unidade independente é uma tendência/tópico, representada por um grafo. O
rótulo binário é `campaign` ou `noncampaign`. O rótulo caracteriza o tópico;
ele não significa que todos os usuários ou todas as arestas do grafo sejam
coordenados.

Cada estado parcial do mesmo grafo é uma medição repetida da mesma unidade, não
uma nova campanha. Por isso, snapshots do mesmo arquivo nunca poderão aparecer
em conjuntos diferentes.

### 3.2 Representação do grafo

O grafo é direcionado. Um nó representa um usuário. Uma aresta de `u` para `v`
representa a interação retida de `u` com `v`. O atributo `timestamp` fornece o
horário dessa aresta e `Interaction_Count` informa quantas interações do par
foram agregadas.

O LEN mantém somente a interação mais recente de cada par ordenado. Assim, a
reconstrução descreve a evolução das **arestas retidas pelo dataset**, não o
fluxo original completo. `Interaction_Count` será usado como intensidade, mas
não para inventar timestamps ausentes.

### 3.3 Grafo parcial por fração do tempo

Para uma fração `p` entre 0 e 1, define-se:

```text
limite(p) = timestamp_mínimo + p × (timestamp_máximo - timestamp_mínimo)
```

O snapshot contém as arestas cujo timestamp é menor ou igual ao limite. Entram
somente os nós que participam dessas arestas. O relógio avança mesmo quando não
há uma nova aresta naquele trecho.

### 3.4 Grafo parcial por fração de eventos observados

As arestas são ordenadas por timestamp. Para uma fração `p`, entram as primeiras
`ceil(p × número_total_de_arestas)` arestas. Empates de timestamp mantêm uma
ordem estável e reproduzível.

Esta modalidade é chamada de `events` no código. Ela significa fração das
arestas/eventos observados, não fração da soma de `Interaction_Count`.

### 3.5 Pontos de observação

As duas modalidades usarão inicialmente as frações de 0,1 a 1,0, em intervalos
de 0,1. A comparação entre elas responde a perguntas diferentes:

- tempo: quanto se sabe depois de determinada parcela da duração da campanha;
- eventos: quanto se sabe depois de determinada parcela das relações observadas.

## 4. Características candidatas

O código calcula um conjunto amplo de candidatas. A seleção final será feita
somente com o conjunto de treino.

| Grupo | Exemplos | O que representam |
| --- | --- | --- |
| Tamanho e intensidade | nós, arestas, soma e distribuição de `Interaction_Count` | volume observado |
| Conectividade | densidade, componentes fracos e fortes, fração do maior componente | fragmentação e coesão |
| Direção | reciprocidade, graus de entrada e saída | padrão das relações direcionadas |
| Concentração | máximos, percentis, Gini e centralização de graus | domínio de poucos usuários |
| Estrutura local | agrupamento médio e transitividade | fechamento de triângulos |
| Comunidades | quantidade de comunidades e modularidade Louvain | separação em grupos internos |
| Ritmo | nós, arestas e interações por hora | velocidade de crescimento |
| Intervalos | média, mediana, desvio, p90 e máximo entre eventos | espaçamento temporal |
| Concentração temporal | entropia em dez faixas, pico e simultaneidade | uniformidade ou rajadas |
| Rajadas | índice de burstiness | alternância entre atividade concentrada e pausas |

Não serão usados nesta etapa:

- `kcore` fornecido pelo arquivo, pois foi calculado no grafo completo;
- nós isolados copiados do grafo final;
- vetores `node_attr` e `edge_attr`;
- texto, descrição de perfil ou atributos cuja disponibilidade no instante do
  snapshot não tenha sido comprovada.

## 5. EDA e controle do viés de tamanho

A EDA deverá responder, de modo simples e visual:

1. quais arquivos realmente compõem a amostra;
2. quais campos estão ausentes, duplicados ou fora do intervalo esperado;
3. como tamanho, duração, intensidade, conectividade e ritmo variam;
4. como as duas modalidades de parcialidade diferem;
5. quais features são redundantes;
6. quais diferenças entre classes permanecem depois de retirar features de
   tamanho.

O controle de tamanho é obrigatório. Serão comparados quatro conjuntos:

- `size_only`: apenas nós, arestas, duração e volume de interações;
- `structural_without_size`: estrutura sem contagens brutas;
- `temporal`: somente dinâmica temporal;
- `structural_plus_temporal`: conjunto combinado após remover redundâncias.

Se `size_only` obtiver desempenho semelhante ao modelo completo, o resultado
deverá ser interpretado como possível viés de construção do dataset, e não como
evidência suficiente de detecção de coordenação.

## 6. Divisão e treinamento

A divisão será feita uma única vez, por arquivo e com estratificação por classe:
60% para treino, 20% para validação e 20% para teste. Todos os snapshots de um
arquivo herdam a mesma partição. A semente será registrada.

Para cada modalidade e fração será treinado um modelo independente. Assim, o
modelo de 20% nunca recebe features calculadas em 30% ou 100%.

No treino:

1. valores ausentes serão imputados usando estatísticas calculadas no treino;
2. a padronização da Regressão Logística será ajustada somente no treino;
3. seleção de features e hiperparâmetros usarão treino e validação;
4. o teste ficará congelado até a escolha final do pipeline.

## 7. Avaliação

Serão reportados precisão, revocação, F1, ROC-AUC e PR-AUC por fração. O F1 da
classe campanha será a medida principal do pôster; PR-AUC e ROC-AUC mostrarão o
comportamento independente de um único limiar.

O resultado central será uma curva:

```text
fração observada × desempenho
```

Também será registrado o primeiro estágio em que um desempenho previamente
definido é atingido e se mantém nos estágios seguintes. O valor do limiar não
será escolhido olhando o conjunto de teste.

## 8. Marcos até o pôster

| Data | Resultado verificável |
| --- | --- |
| 23/09 | metodologia registrada, código de snapshots testado, features candidatas definidas e divergência dos 104/100 arquivos documentada |
| 07/10 | amostra canônica congelada, EDA aprofundada concluída, split definido e primeiro baseline executado |
| 21/10 | configuração escolhida na validação, curvas de precocidade e análise de features congeladas |
| 04/11 a 09/11 | revisão técnica, redação final, diagramação e submissão do pôster |

## 9. Decisões pendentes

1. Identificar, por uma fonte oficial ou manifesto original, os três arquivos
   excedentes que permanecem após a remoção da duplicata conhecida. A página de
   download e o artigo descrevem versões diferentes do LEN; a decisão não deve
   ser feita por suposição.
2. Congelar a lista canônica antes de criar o split.
3. Definir o limiar operacional de “detecção suficientemente boa” usando apenas
   treino e validação.

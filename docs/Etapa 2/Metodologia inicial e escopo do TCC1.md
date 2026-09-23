# Etapa 2 — Metodologia inicial e escopo do TCC1

**Data da decisão:** 21/09/2026

**Revisado em:** 23/09/2026

**Prazo do pôster:** 09/11/2026

## Visão geral

Este TCC investiga se é possível reconhecer uma campanha coordenada antes que
todas as interações dela aconteçam.

A ideia central é simples:

1. ordenar as interações de cada tópico pelo horário;
2. mostrar ao modelo apenas uma parte dessas interações;
3. medir o que já existe nessa parte do grafo;
4. verificar em que momento campanhas e não campanhas começam a parecer
   diferentes.

No TCC1, vamos começar com modelos clássicos e explicáveis. GNNs ficam como uma
possível extensão do TCC2.

## 1. O que deve estar pronto no final do TCC1

Até a entrega do pôster, queremos ter:

- a lista exata dos grafos usados no experimento;
- código testado para criar grafos parciais;
- uma tabela com medidas calculadas em 10%, 20%, ..., 100% de cada grafo;
- uma análise clara das diferenças entre campanhas e não campanhas;
- uma divisão fixa dos grafos em 75% para treino, 10% para validação e 15% para
  teste;
- pelo menos um modelo simples treinado sem usar informações do futuro;
- gráficos mostrando como o desempenho muda conforme mais interações aparecem;
- uma análise inicial das medidas mais úteis para a classificação.

O TCC1 não precisa entregar uma GNN, um sistema pronto para uso real ou uma
análise dos textos publicados nas redes sociais.

## 2. Escolha dos primeiros modelos

Usaremos dois modelos:

- **Regressão Logística:** será o primeiro modelo porque é simples e permite
  observar como cada medida influencia a classificação.
- **Random Forest:** será usada como comparação porque consegue representar
  relações menos lineares entre as medidas.

As GNNs não foram descartadas. Elas foram adiadas porque o LEN-small possui
aproximadamente 100 grafos independentes. Os vários estados de 10%, 20% e 30%
do mesmo tópico continuam sendo partes do mesmo grafo e não podem ser tratados
como novas campanhas independentes.

Antes de usar uma arquitetura mais complexa, precisamos responder a uma questão
mais básica: o modelo está aprendendo coordenação ou apenas percebendo que as
campanhas do LEN-small costumam ser menores?

## 3. O que representa cada grafo

Cada grafo representa as interações relacionadas a um tópico do Twitter.

- **Nó:** um usuário.
- **Aresta:** uma interação, como retuíte, resposta ou citação.
- **Direção da aresta:** indica quem interagiu com quem.
- **Timestamp:** horário associado à interação armazenada.
- **Interaction_Count:** quantidade de interações agrupadas entre o mesmo par de
  usuários.

O rótulo `campaign` indica que o artigo detectou astroturfing efêmero na origem
da tendência. Ele não significa que todos os usuários ou todas as interações
daquele grafo sejam coordenados. Uma campanha pode ter apoio genuíno mesmo que
bots tenham ajudado a promovê-la.

O rótulo `noncampaign` foi atribuído manualmente a tendências consideradas mais
provavelmente orgânicas, como notícias, esportes e festivais. Ele não comprova
que o tópico esteja livre de qualquer forma de coordenação.

O dataset representa tendências turcas coletadas entre março e maio de 2023,
em um período próximo às eleições gerais. Resultados obtidos nesse conjunto não
podem ser generalizados automaticamente para outros países, períodos ou formas
de campanha.

### Limitação importante do LEN

Quando dois usuários interagiram várias vezes, o LEN mantém apenas a interação
mais recente entre eles. `Interaction_Count` informa quantas interações foram
agrupadas, mas não informa o horário individual de cada uma.

O artigo informa que essa escolha preserva aproximadamente 74% das arestas dos
grafos originais.

Por isso, este trabalho analisa a **evolução observada no LEN**. Não é possível
reconstruir perfeitamente tudo o que aconteceu no Twitter.

## 4. Como criamos os grafos parciais

Usamos duas formas diferentes. Elas respondem a perguntas diferentes e não
devem ser misturadas.

### 4.1 Fração do tempo

O intervalo entre a primeira e a última interação é dividido em dez partes.

Exemplo: um grafo durou 20 horas. O estado de 30% contém tudo o que apareceu
nas primeiras 6 horas.

Essa modalidade responde:

> Quanto da rede já apareceu depois de determinada parte da duração do tópico?

No código, ela é chamada de `time`.

### 4.2 Fração das arestas observadas

As arestas são ordenadas pelo horário. O estado de 30% contém as primeiras 30%
das arestas armazenadas no grafo.

Essa modalidade responde:

> O que sabemos depois de observar determinada quantidade das relações finais?

No código, ela é chamada de `events`.

Nesta modalidade, `events` significa arestas observadas. Não significa a soma de
`Interaction_Count`, porque não conhecemos os horários das interações agrupadas.

### 4.3 Quando um usuário entra no grafo parcial

Um usuário aparece somente quando participa de uma aresta que já aconteceu. Não
copiamos antecipadamente os usuários do grafo completo, pois isso revelaria
informações do futuro.

## 5. O que medimos em cada estado parcial

O código calcula várias medidas candidatas. Elas serão avaliadas antes da escolha
do conjunto final.

| Grupo | Exemplos | Pergunta que ajuda a responder |
| --- | --- | --- |
| Tamanho | usuários e arestas | Quanto da rede já apareceu? |
| Intensidade | total de interações | Poucas relações concentram muitas ações? |
| Conectividade | componentes e maior componente | A rede está unida ou fragmentada? |
| Direção | graus de entrada, saída e reciprocidade | As interações são concentradas ou correspondidas? |
| Concentração | máximos, percentis e desigualdade dos graus | Poucos usuários dominam a atividade? |
| Grupos internos | comunidades e modularidade | A rede se divide em grupos bem separados? |
| Ritmo | usuários, arestas e interações por hora | Com que velocidade a rede cresce? |
| Tempo | intervalos, pico, entropia e rajadas | As interações são regulares ou concentradas em certos momentos? |

Alguns campos não serão usados no primeiro modelo:

- `kcore` fornecido no JSON, pois foi calculado usando o grafo completo;
- `node_attr` e `edge_attr`, pois ainda não sabemos se todos os seus valores
  estariam disponíveis no momento de cada estado parcial;
- textos e descrições de perfil;
- usuários que só aparecem em etapas futuras.

## 6. Como evitar que o tamanho engane o modelo

No LEN-small, as campanhas são muito menores do que as não campanhas. Um modelo
pode obter um bom resultado apenas aprendendo “grafo pequeno = campanha”.

Essa diferença também aparece nos estados parciais. Nas contagens absolutas,
não campanhas possuem muito mais usuários e arestas. Quando dividimos cada
quantidade pelo total final do próprio grafo, as curvas das duas classes ficam
próximas. Isso indica que boa parte da separação absoluta vem do tamanho final,
e não de ritmos de crescimento muito diferentes.

Para verificar isso, compararemos quatro conjuntos de medidas:

1. **Somente tamanho:** usuários, arestas, duração e total de interações.
2. **Estrutura sem tamanho:** medidas de conectividade e concentração sem as
   contagens brutas.
3. **Somente tempo:** ritmo, intervalos e concentração temporal.
4. **Estrutura e tempo:** combinação das medidas úteis dos grupos anteriores.

Se o modelo completo não superar claramente o modelo que usa somente tamanho,
o resultado deverá ser apresentado como possível viés do dataset, e não como
uma descoberta de sinais de coordenação.

## 7. Separação dos dados

Primeiro dividiremos os grafos por tópico:

- 75% para treino;
- 10% para validação;
- 15% para teste.

Depois criaremos os estados parciais. Assim, todos os estados de um mesmo tópico
ficam sempre na mesma divisão.

Essa é a divisão inicial. Ela será estratificada por classe, na medida permitida
pelo número de grafos, e registrada com uma semente fixa para ser reproduzível.
Como o conjunto de validação terá poucos grafos, sua estabilidade deverá ser
observada antes de congelarmos a metodologia definitiva.

Isso evita uma situação injusta: o modelo estudar o estado de 20% de um tópico
no treino e encontrar o estado de 80% do mesmo tópico no teste.

Cada combinação de modalidade e fração terá seu próprio treinamento. O modelo
de 20% nunca receberá medidas calculadas em 30% ou 100%.

## 8. Como avaliaremos os resultados

Para cada fração, calcularemos:

- **Precisão:** quando o modelo indica campanha, quantas vezes ele está certo?
- **Revocação:** quantas das campanhas existentes o modelo consegue encontrar?
- **F1:** qual é o equilíbrio entre precisão e revocação?
- **ROC-AUC e PR-AUC:** o modelo coloca campanhas acima de não campanhas mesmo
  quando mudamos o limite usado para decidir entre as classes?

O principal gráfico será:

```text
parte observada do grafo × qualidade da classificação
```

Ele deverá mostrar se o desempenho melhora quando novas interações aparecem e
qual é a menor fração em que o resultado se torna estável.

O valor usado para definir “desempenho suficiente” será escolhido usando treino
e validação. O conjunto de teste não será usado para escolher esse valor.

## 9. Cronograma até o pôster

| Data | Entrega esperada |
| --- | --- |
| 23/09 | metodologia, grafos parciais, medidas candidatas e problemas da base documentados |
| 07/10 | lista de grafos definida, EDA concluída, divisão dos dados e primeiro modelo executado |
| 21/10 | resultados de validação, gráficos de precocidade e análise das medidas escolhidos |
| 04/11 a 09/11 | revisão, diagramação e entrega do pôster |

## 10. O que ainda precisa ser resolvido

1. O pacote local possui 103 grafos únicos, mas o artigo descreve 100. Precisamos
   identificar oficialmente os três arquivos excedentes.
2. Depois disso, precisamos congelar a lista de grafos e a divisão dos dados.
3. O critério de “detecção suficientemente boa” precisa ser definido antes da
   avaliação final no teste.
4. Os resultados precisam ser apresentados dentro do recorte do LEN: tendências
   turcas, rótulos construídos por procedimentos diferentes e coleta difícil de
   reproduzir atualmente.

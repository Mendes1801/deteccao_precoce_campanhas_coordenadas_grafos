# Etapa 2 — Análise aprofundada do LEN

**Data:** 21/09/2026

**Revisado em:** 23/09/2026

**Dados analisados:** 104 arquivos locais; 103 depois da retirada de uma
duplicata exata

## Resumo em linguagem simples

Os dados permitem criar grafos parciais e estudar o início das campanhas. Porém,
há quatro cuidados importantes:

1. ainda não sabemos quais são exatamente os 100 grafos usados no artigo;
2. as campanhas do pacote local são muito menores do que as não campanhas;
3. campanhas e não campanhas foram rotuladas por procedimentos diferentes;
4. o conjunto representa tendências turcas coletadas em um período curto e
   eleitoral.

Essa diferença de tamanho pode facilitar a classificação pelo motivo errado. Um
modelo pode aprender que “grafo pequeno” significa “campanha”, sem aprender um
padrão real de coordenação.

## 1. Quantos grafos existem no pacote local?

Foram encontrados:

- 53 arquivos de campanha;
- 51 arquivos de não campanha;
- 104 arquivos no total.

Dois arquivos são cópias exatas do mesmo grafo:

- `#SesimiziDuyanVarMi___2023-03-23_campaign_fulldata.json`;
- `#SesimiziDuyanVarMı___2023-03-23_campaign_fulldata.json`.

Depois de manter apenas uma cópia, restam 103 grafos: 52 campanhas e 51 não
campanhas. O artigo descreve 100 grafos: 51 campanhas e 49 não campanhas.

### O que isso significa?

Ainda não devemos criar a divisão definitiva de treino, validação e teste. Se
escolhermos por conta própria quais três arquivos remover, podemos produzir uma
amostra diferente da usada pelos autores.

A página do dataset e o artigo também parecem descrever versões diferentes da
base. Precisamos localizar uma lista oficial dos arquivos ou pedir essa
informação aos autores.

Quando essa lista estiver definida, a divisão inicial será de 75% dos grafos
para treino, 10% para validação e 15% para teste. A divisão continuará sendo
feita por tópico, antes da criação dos estados parciais.

## 2. Os arquivos possuem os dados necessários?

Sim. Nos critérios básicos avaliados:

- todos os grafos são direcionados;
- todos possuem timestamps nas arestas;
- não há IDs de usuários duplicados dentro do mesmo grafo;
- não há arestas apontando para usuários inexistentes;
- os arquivos originais não estão ordenados pelo horário.

O último ponto não é um problema, pois o código ordena as arestas antes de criar
os estados parciais.

## 3. Campanhas e não campanhas têm tamanhos diferentes

Os valores abaixo são medianas. A mediana representa um valor típico sem ser tão
influenciada pelos grafos muito grandes.

| Medida | Campanhas | Não campanhas | Leitura simples |
| --- | ---: | ---: | --- |
| Usuários | 506 | 3.227 | não campanhas têm muito mais usuários |
| Arestas | 1.078 | 3.769 | não campanhas têm mais relações observadas |
| Interações agrupadas | 1.647 | 4.835 | não campanhas têm maior volume total |
| Duração | 22,60 h | 23,94 h | a duração típica é parecida |
| Reciprocidade | 0,0311 | 0,0051 | campanhas têm mais relações nos dois sentidos |
| Usuários no maior componente | 69,3% | 72,5% | a parcela principal da rede é semelhante |

Em 93,6% das comparações entre uma campanha e uma não campanha escolhidas ao
acaso, a campanha possui menos usuários.

### O que isso significa?

O número de usuários sozinho já separa bastante as duas classes. Por isso,
qualquer modelo deverá ser comparado com um modelo simples que usa somente o
tamanho do grafo.

### O que acontece quando controlamos o tamanho final?

Os gráficos também foram calculados como proporções do total de cada grafo. Por
exemplo, usuários observados foram divididos pelo número final de usuários do
mesmo grafo antes de calcular a mediana da classe.

Nas contagens absolutas, não campanhas possuem muito mais usuários e arestas em
todas as frações. Depois da normalização, as curvas ficam próximas. Em 10% das
arestas, campanhas já apresentam 12,9% de seus usuários finais e não campanhas,
12,1%.

A maior diferença proporcional aparece no começo da duração. Em 30% do tempo,
campanhas apresentam 27,9% de seus usuários finais e não campanhas, 21,3%. Essa
diferença diminui nas frações seguintes.

Isso reforça que boa parte da separação nas contagens absolutas vem do tamanho
final dos grafos. Ainda pode existir informação estrutural ou temporal útil, mas
as contagens brutas não demonstram isso sozinhas.

## 4. Por que algumas medidas precisam de cuidado?

A densidade parece maior nas campanhas. Porém, a densidade cai naturalmente
quando o número de usuários aumenta. Nos dados, a relação entre tamanho e
densidade é muito forte: a correlação é `-0,98`.

Isso significa que uma diferença de densidade pode ser apenas consequência da
diferença de tamanho.

O mesmo cuidado vale para a quantidade de componentes. Grafos maiores tendem a
ter mais componentes simplesmente porque possuem mais usuários. Medidas em
forma de proporção, como a parcela de usuários no maior componente, permitem uma
comparação mais justa.

## 5. O que o tempo do LEN realmente representa?

O LEN guarda apenas a interação mais recente entre cada par de usuários. Quando
`Interaction_Count` vale 5, por exemplo, sabemos que houve cinco interações, mas
conhecemos somente um timestamp para esse grupo.

Segundo o artigo, essa simplificação preserva aproximadamente 74% das arestas
dos grafos originais.

Por isso:

- podemos ordenar e analisar as arestas armazenadas;
- não podemos inventar os horários das interações anteriores;
- as medidas temporais descrevem a evolução visível no LEN;
- os resultados não representam uma reconstrução completa do Twitter.

## 6. Tabela dos grafos parciais

Foram calculados:

- 103 grafos;
- 2 formas de parcialidade;
- 10 frações por forma;
- 2.060 estados parciais no total;
- 57 medidas para cada estado.

As duas formas de parcialidade são:

- **tempo:** quanto da duração total já passou;
- **arestas:** quanto do número final de arestas já foi observado.

Os estados crescem corretamente: nenhum estado posterior perde usuários ou
arestas. Em 100%, as duas formas chegam ao mesmo grafo final.

### Por que as duas formas não são equivalentes?

Em 10% das arestas, uma campanha típica já possui 73,5 usuários e 108,5
arestas. Em 10% do tempo, ela possui apenas 24 usuários e 22,5 arestas.

Isso ocorre porque as interações não aparecem em ritmo constante. Uma parte do
tempo pode conter poucas interações, enquanto outra parte concentra grande
atividade.

## 7. Valores ausentes na tabela

O CSV possui 2.060 registros preenchidos. As linhas 2 a 881 começam com `#`
porque representam tópicos que são hashtags. Alguns visualizadores tratam `#`
como marcador de comentário e escondem essas linhas. A exportação foi ajustada
para colocar os campos de texto entre aspas e evitar esse comportamento.

Existem somente 26 ausências reais. Elas aparecem nas medidas de intervalo entre
eventos quando o estado parcial contém apenas uma aresta. Com apenas um evento,
não existe um intervalo para calcular.

Esse não é um erro do dataset. Durante o treinamento, esses casos deverão ser
tratados com uma regra definida somente a partir do conjunto de treino.

## 8. Primeiros sinais que merecem investigação

A modularidade mede o quanto a rede está dividida em grupos com muitas conexões
internas e poucas conexões entre grupos.

Em 10% das arestas, a modularidade mediana foi:

- 0,405 para campanhas;
- 0,835 para não campanhas.

Essa diferença pode ser útil, mas ainda não é uma conclusão. Redes maiores ou
mais fragmentadas também podem apresentar modularidade maior. Precisamos testar
se a diferença continua útil depois de controlar o tamanho.

## 9. Limitações dos rótulos e da coleta

O rótulo de campanha foi obtido pela detecção de um tipo específico de ataque:
o astroturfing efêmero. Nesse ataque, bots publicam rapidamente textos gerados a
partir de um léxico para levar um tópico aos assuntos em alta e depois apagam as
publicações.

As não campanhas foram escolhidas manualmente entre notícias, esportes,
festivais e outros eventos populares. Os autores consideraram esses tópicos mais
provavelmente orgânicos por estarem associados a acontecimentos externos. Isso
é uma aproximação: `noncampaign` não comprova ausência de coordenação.

Também devemos considerar que:

- os dados representam tendências turcas entre março e maio de 2023, em um
  período próximo às eleições gerais;
- outros tipos de campanha coordenada podem não ter sido detectados;
- uma campanha pode conter usuários e apoio genuínos, mesmo que bots tenham
  ajudado a promovê-la;
- o Twitter encerrou o acesso ao fluxo gratuito de 1% usado na coleta, o que
  dificulta reproduzir ou ampliar o dataset.

Essas limitações impedem interpretar o problema como uma separação universal
entre comportamento autêntico e inautêntico. Neste trabalho, os rótulos serão
tratados como as categorias operacionais definidas pelo LEN.

## Conclusões e próximos passos

A análise confirma que o LEN pode ser usado para estudar detecção precoce. Os
timestamps permitem ordenar as arestas e criar estados que mostram somente a
parte já observada da rede.

Também ficou claro que a classificação exige cuidado. As campanhas são muito
menores do que as não campanhas. Portanto, um bom resultado de classificação
não será suficiente por si só. Precisaremos mostrar se as medidas estruturais e
temporais acrescentam informação além do tamanho.

As curvas normalizadas reforçam esse cuidado: quando cada quantidade é dividida
pelo total final do próprio grafo, campanhas e não campanhas crescem em ritmos
parecidos. O modelo de tamanho será uma referência obrigatória para interpretar
qualquer ganho posterior.

As duas formas de parcialidade devem permanecer separadas. A fração do tempo
simula quanto tempo passou. A fração das arestas controla quanto da estrutura
final já foi visto. Como o ritmo das interações varia, as duas formas geram
estados iniciais bastante diferentes.

Antes do primeiro treinamento, os próximos passos são:

1. identificar oficialmente os 100 grafos do LEN-small;
2. congelar a lista de arquivos usada no experimento;
3. separar os grafos em 75% para treino, 10% para validação e 15% para teste;
4. comparar um modelo que usa somente tamanho com modelos estruturais e
   temporais;
5. verificar em qual fração as medidas começam a separar as classes de forma
   estável;
6. registrar claramente as limitações do LEN no relatório e no pôster.

O objetivo não é apenas obter uma classificação alta. O objetivo é descobrir se
há sinais úteis de coordenação nas fases iniciais e demonstrar que esses sinais
não são apenas consequência do tamanho dos grafos.

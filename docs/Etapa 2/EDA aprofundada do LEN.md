# Etapa 2 — EDA aprofundada do LEN

**Data:** 21/09/2026

**Escopo:** 104 arquivos locais; 103 após remover uma duplicata exata

**Status:** análise descritiva e tabela de snapshots concluídas

## Resumo executivo

A EDA inicial confirmou que os arquivos podem ser lidos e possuem timestamps,
mas não era suficiente para orientar um modelo. A análise aprofundada encontrou
três questões que passam a controlar o desenho experimental:

1. o pacote local não corresponde exatamente ao LEN-small descrito no artigo;
2. campanhas e não campanhas têm tamanhos muito diferentes;
3. algumas métricas aparentemente discriminativas, como densidade, estão quase
   determinadas pelo tamanho do grafo.

O principal risco é construir um modelo que classifique tamanho, e não
coordenação.

## 1. Composição e integridade

Foram encontrados 104 JSONs: 53 campanhas e 51 não campanhas. Os arquivos
`#SesimiziDuyanVarMi...` e `#SesimiziDuyanVarMı...` são idênticos byte a byte,
com SHA-256
`57da6c1942138f0549c87a9cf696b8c306d32bc1f7aa7b51de9f49b10a313b88`.

Após excluir uma cópia, restam 103 grafos: 52 campanhas e 51 não campanhas. O
artigo descreve 100: 51 campanhas e 49 não campanhas. Portanto, ainda existem
um arquivo de campanha e dois de não campanha que precisam ser identificados
antes do split definitivo.

Há também indício de versões diferentes da base. A página oficial consultada em
21/09/2026 ainda descreve 305 grafos (170 campanhas e 135 não campanhas) e
oferece um pacote pequeno datado de 11/06/2024. O artigo de 2025 descreve 314
grafos (179 campanhas e 135 não campanhas). A lista canônica não deve ser
inferida apenas pela contagem; é necessário localizar um manifesto da versão
usada no artigo ou obter confirmação dos autores.

Todos os arquivos são grafos direcionados e não multigrafos. Não foram
encontrados IDs de nós duplicados, endpoints ausentes ou timestamps ausentes.
Nenhum arquivo está ordenado cronologicamente, por isso o código sempre ordena
as arestas explicitamente.

## 2. Diferença de tamanho entre as classes

Resultados após retirar a duplicata conhecida:

| Medida | Campanha (mediana) | Não campanha (mediana) | Observação |
| --- | ---: | ---: | --- |
| Nós | 506 | 3.227 | campanhas são muito menores |
| Arestas | 1.078 | 3.769 | diferença forte de volume |
| Interações agregadas | 1.647 | 4.835 | não campanhas têm maior atividade total |
| Duração | 22,60 h | 23,94 h | diferença menor, mas ainda presente |
| Densidade | 0,00418 | 0,00034 | campanhas parecem mais densas |
| Grau total médio | 3,57 | 2,39 | campanhas parecem mais concentradas |
| Reciprocidade | 0,0311 | 0,0051 | campanhas apresentam mais relações recíprocas |
| Componentes fracos | 15 | 142 | não campanhas têm mais fragmentos absolutos |
| Fração no maior componente | 0,693 | 0,725 | distribuições semelhantes |

Em 93,6% dos pares formados por uma campanha e uma não campanha escolhidas ao
acaso, a campanha possui menos nós. Isso mostra que `nodes` sozinho já contém
um sinal de classe muito forte.

## 3. Redundância e interpretação das métricas

A correlação de Spearman entre nós e arestas é 0,85. A correlação entre número
de nós e densidade é -0,98. Essa última relação não prova uma propriedade de
coordenação: a fórmula da densidade divide o número de arestas por uma quantidade
quadrática de pares possíveis, então grafos grandes tendem naturalmente a ter
densidade menor.

Da mesma forma, o número absoluto de componentes cresce com o tamanho do grafo
(correlação de 0,81 com nós). Por isso, a fração do maior componente é mais útil
para comparar grafos de tamanhos diferentes do que a contagem bruta de
componentes.

As próximas análises devem preferir medidas normalizadas e sempre comparar o
modelo completo com um baseline que usa somente tamanho.

## 4. Limitação temporal do LEN

O timestamp de uma aresta corresponde à interação mais recente retida para o
par ordenado. Quando `Interaction_Count` é maior que 1, o dataset informa o
volume agregado, mas não os horários das interações anteriores.

Consequências:

- é válido ordenar as arestas retidas e estudar quando elas aparecem;
- não é válido expandir `Interaction_Count` em eventos artificiais;
- taxas e intervalos descrevem as arestas observadas, não todo o fluxo original;
- o texto do TCC e do pôster deve usar a expressão “evolução observada no LEN”.

## 5. Campos excluídos do primeiro baseline

`kcore` é derivado do grafo completo e causaria vazamento. `node_attr` e
`edge_attr` contêm embeddings e outros atributos cuja disponibilidade temporal
ainda não foi comprovada. Eles não entram no primeiro baseline.

Os nós do grafo completo também não são copiados antecipadamente. Um usuário
passa a existir no snapshot somente quando participa de uma aresta já observada.

## 6. Resultado da nova tabela de snapshots

Foram geradas 2.060 linhas: 103 grafos × 2 modalidades × 10 frações. Cada linha
possui identificação, parâmetros do snapshot e 57 características calculadas.
Não há chaves duplicadas; nós e arestas crescem monotonicamente; e os dois modos
chegam ao mesmo grafo em 100%.

Nos snapshots por eventos, as medianas em 10% foram 73,5 nós e 108,5 arestas
para campanhas, contra 376 nós e 377 arestas para não campanhas. Pela fração do
tempo, os snapshots de 10% foram ainda menores: 24 nós e 22,5 arestas para
campanhas, contra 88 nós e 66 arestas para não campanhas. Logo, as duas
modalidades não são intercambiáveis.

A modularidade mediana por eventos em 10% foi 0,405 para campanhas e 0,835 para
não campanhas; em 100%, 0,529 e 0,851. Esse contraste é uma hipótese promissora,
mas ainda pode refletir tamanho e fragmentação. Ele deverá ser testado no
conjunto de treino, com controle explícito de tamanho.

Somente as estatísticas de intervalos entre eventos apresentaram ausência: cerca
de 1,26% dos snapshots possuíam apenas uma aresta e, portanto, não tinham um
intervalo a calcular. Isso é esperado e será tratado por imputação ajustada
somente no treino.

Para cada arquivo, modalidade e fração, a tabela registra volume, conectividade,
graus, concentração, comunidades, agrupamento, ritmo, intervalos, simultaneidade,
entropia temporal e rajadas.

As perguntas da próxima EDA são:

1. tempo e número de eventos produzem snapshots de tamanhos muito diferentes?
2. quais features estabilizam cedo e quais só aparecem perto do grafo completo?
3. quais diferenças de classe permanecem sem contagens brutas?
4. modularidade, reciprocidade e concentração temporal acrescentam informação
   além do tamanho?
5. há valores extremos que dominariam o treinamento?

## 7. Conclusão atual

O LEN é utilizável para um estudo exploratório de detecção precoce, mas não deve
ser tratado como uma sequência completa de interações. A principal hipótese a
testar no TCC1 não é apenas “é possível classificar?”, e sim “há sinal estrutural
ou temporal além do viés de tamanho, e em qual estágio ele aparece?”.

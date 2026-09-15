# Detecção precoce de campanhas coordenadas em redes sociais por meio da evolução de grafos temporais

## 1. Título

**Detecção precoce de campanhas coordenadas em redes sociais por meio da evolução de grafos temporais**

## 2. Integrantes
Camila Carniel 
Bruno Germanetti

## 3. Resumo

Este projeto investiga a possibilidade de identificar precocemente campanhas coordenadas em redes sociais a partir da evolução temporal das interações entre usuários. A base experimental inicial é o **Large Engagement Networks (LEN)**, um conjunto de grafos direcionados rotulados como `campaign` ou `noncampaign`. Na etapa atual, foi realizada uma análise exploratória reprodutível em Python, com leitura incremental dos arquivos JSON, cálculo de métricas estruturais e temporais e verificação de integridade. O pacote local contém 104 grafos, 53 classificados como campanhas e 51 como não campanhas, totalizando 212.231 nós e 289.975 arestas. Todos os grafos possuem timestamps nas arestas, o que permite reconstruir estados parciais da rede após ordenar os eventos. A metodologia proposta é separar as redes por campanha, gerar janelas temporais, extrair características de crescimento e topologia e comparar baselines com modelos temporais de grafos. Espera-se obter um detector que preserve desempenho com apenas uma fração inicial das interações e que produza evidências interpretáveis para apoiar a análise humana.

## 4. Introdução

### 4.1 Contextualização

Redes sociais permitem que usuários, publicações e comunidades se conectem em grande escala. Essa conectividade também pode ser explorada por grupos que coordenam comportamento, amplificam narrativas ou tentam simular engajamento orgânico. Uma campanha coordenada pode apresentar sinais na estrutura da rede, como concentração de interações, reciprocidade, crescimento acelerado e formação de componentes densos.

A representação de interações como grafos temporais permite observar não apenas quem se conecta, mas também a ordem em que as conexões aparecem. O trabalho de Gopalakrishnan et al. (2025) apresenta o LEN como uma base para classificar tendências orgânicas e campanhas coordenadas. Este projeto parte dessa base para estudar o cenário de detecção **precoce**, em que a decisão deve ser tomada antes que a rede completa esteja disponível.

### 4.2 Justificativa

A detecção tardia reduz a possibilidade de análise, resposta e contenção. Entretanto, antecipar uma classificação aumenta o risco de erro, pois os sinais iniciais podem ser incompletos ou compatíveis com comportamentos legítimos. Uma abordagem temporal, com avaliação em diferentes frações da evolução observada, permite medir esse compromisso entre antecedência e desempenho.

O projeto também é relevante do ponto de vista técnico: os arquivos do LEN contêm vetores de atributos de alta dimensão, e a leitura integral de todos os dados pode consumir muita memória. Por isso, a primeira etapa prioriza um pipeline auditável, incremental e baseado em campos cuja disponibilidade temporal é mais clara.

### 4.3 Objetivo

O objetivo geral é desenvolver e avaliar uma abordagem reprodutível para detectar precocemente campanhas coordenadas usando a evolução temporal de grafos de interação.

Objetivos específicos:

- caracterizar a estrutura, escala, temporalidade e qualidade do LEN;
- definir uma versão canônica da amostra e evitar duplicidades ou vazamento temporal;
- reconstruir grafos parciais em diferentes frações da evolução observada;
- extrair características estruturais e temporais das redes parciais;
- comparar um baseline simples com modelos temporais mais sofisticados;
- avaliar desempenho, antecedência da decisão, estabilidade e interpretabilidade.

### 4.4 Opção do projeto

A opção escolhida é um projeto aplicado de ciência de dados e inteligência artificial para análise de redes sociais. O problema será tratado inicialmente como classificação binária de grafos: `campaign` versus `noncampaign`. A dimensão temporal será incorporada pela criação de estados parciais ordenados por timestamp. O escopo inicial não inclui identificação nominal de pessoas, moderação automática de conteúdo ou intervenção sobre usuários.

## 5. Descrição do problema

Dado um grafo de interações parcialmente observado, deseja-se estimar se ele pertence a uma campanha coordenada. Formalmente, para uma rede com arestas ordenadas por tempo, sejam $G_{p}$ os estados formados pelas primeiras frações $p \in \{0{,}1, 0{,}2, \ldots, 1{,}0\}$ das arestas retidas pelo dataset. O modelo deve estimar $P(y=\text{campaign}\mid G_p)$ e permitir avaliar em que fração da evolução a decisão se torna confiável.

Há três dificuldades principais. Primeiro, a ordem dos eventos não pode ser inferida pela posição no JSON: a EDA verificou que os arquivos não estão ordenados cronologicamente. Segundo, o LEN retém a interação mais recente de cada par ordenado de usuários; portanto, a reconstrução representa as arestas retidas, e não o fluxo original completo (GOPALAKRISHNAN et al., 2025). Terceiro, atributos calculados a partir do grafo completo, como `kcore`, podem carregar informação do futuro e não devem entrar nos estados parciais.

## 6. Aspectos éticos e responsabilidade no uso da IA

O uso de IA para classificar campanhas coordenadas envolve riscos técnicos e sociais. Um falso positivo pode associar comportamento legítimo a manipulação, afetar reputação e gerar decisões injustas. Um falso negativo pode deixar uma campanha ativa sem análise. Por isso, o sistema deve ser tratado como apoio à investigação, e não como autoridade autônoma para punição, remoção ou atribuição de intenção.

A base deve ser usada conforme sua licença, documentação e finalidade científica. Os identificadores de usuários e os atributos potencialmente reidentificáveis devem ser minimizados, anonimizados quando necessário e nunca publicados além do que a licença permite. O grupo não deve tentar reidentificar indivíduos, inferir características sensíveis ou associar um rótulo experimental a uma pessoa real.

A responsabilidade inclui documentar origem, transformações, critérios de inclusão, limitações e incertezas. Também é necessário separar treino, validação e teste por campanha antes da criação das janelas, para evitar que estados de uma mesma rede apareçam em conjuntos diferentes. Métricas agregadas devem ser acompanhadas por análise de erros, calibração e, quando houver variáveis apropriadas, avaliação de desempenho entre subgrupos. Toda decisão operacional deve passar por revisão humana, registro de justificativa e mecanismo de contestação.

Por fim, a equipe deve reconhecer que o rótulo `campaign` é um rótulo do dataset, não uma prova universal de má-fé. O modelo aprende padrões presentes na coleta e na definição de classes; ele não estabelece sozinho causalidade, intenção ou ilegalidade. Essas limitações serão apresentadas junto aos resultados.

## 7. Dataset, análise exploratória e preparação em Python

### 7.1 Origem e conteúdo

O dataset utilizado é o **Large Engagement Networks (LEN)**, disponibilizado pelos autores do trabalho de Gopalakrishnan et al. (2025) na página do projeto: <https://erdemub.github.io/large-engagement-network/>. O subconjunto local usado nesta etapa é organizado na pasta `small_encoder_final/`, com um arquivo JSON por grafo. Os nomes dos arquivos permitem inferir o tópico e a classe (`campaign` ou `noncampaign`).

Cada arquivo contém grafos direcionados e não multigrafos, com nós e links. As arestas incluem, entre outros campos, `source`, `target`, `timestamp` e `Interaction_Count`. Também existem vetores `node_attr` de 772 posições e `edge_attr` de 776 posições. A composição e a disponibilidade temporal desses vetores ainda não foram validadas; por isso, eles foram ignorados no baseline inicial. A base local não é alterada pelo pipeline.

O pacote local possui 104 arquivos: 53 campanhas e 51 não campanhas. A documentação do LEN-small descreve 100 grafos, com 51 campanhas e 49 não campanhas. Também foi encontrada uma duplicidade byte a byte entre os arquivos `#SesimiziDuyanVarMi___2023-03-23_campaign_fulldata.json` e `#SesimiziDuyanVarMı___2023-03-23_campaign_fulldata.json`. Essa divergência precisa ser resolvida e registrada antes do experimento definitivo.

### 7.2 Análise exploratória

A análise inicial encontrou:

| Medida | Resultado |
| --- | ---: |
| Arquivos locais | 104 |
| Campanhas | 53 |
| Não campanhas | 51 |
| Nós totais | 212.231 |
| Arestas totais | 289.975 |
| Timestamps presentes | 100% das arestas |
| IDs de nós duplicados | Nenhum identificado |
| Endpoints de arestas ausentes | Nenhum identificado |
| Dimensão de `node_attr` | 772 |
| Dimensão de `edge_attr` | 776 |

A EDA compara tamanho dos grafos, quantidade de arestas, duração temporal, cobertura de timestamps e fração do maior componente fracamente conectado entre as classes. O notebook também lista grafos com problemas de integridade, como IDs duplicados, endpoints inexistentes e timestamps ausentes.

### 7.3 Preparação e implementação

O módulo `src/len_eda/summary.py` usa `ijson` para processar os JSONs de forma incremental, sem materializar na memória os grandes vetores de atributos. Durante a leitura, tokens `NaN` não padronizados são convertidos em `null` somente no fluxo do parser; os arquivos originais permanecem intactos.

Para cada grafo, o pipeline calcula classe, tópico, tamanho do arquivo, nós, arestas, IDs únicos, laços, endpoints ausentes, dimensões dos atributos, densidade, graus, reciprocidade, componentes, timestamp inicial e final, duração, cobertura temporal e estatísticas de `Interaction_Count`. A tabela derivada pode ser recriada com:

```bash
len-summary --data-dir small_encoder_final --output outputs/len_small_summary.csv
```

A análise exploratória em Python está em [notebooks/01_eda_inicial_len.ipynb](../notebooks/01_eda_inicial_len.ipynb). O código reutilizável e testado está em [src/len_eda/summary.py](../src/len_eda/summary.py), e o teste automatizado está em [tests/test_summary.py](../tests/test_summary.py).

## 8. Metodologia e resultados esperados

A metodologia será executada em etapas:

1. **Congelamento da amostra:** resolver a divergência entre 104 arquivos locais e os 100 grafos descritos na documentação, registrar a duplicidade e definir a lista canônica.
2. **Ordenação temporal:** ordenar as arestas por `timestamp`, independentemente da ordem no JSON, e documentar timestamps iguais e duração de cada rede.
3. **Construção dos estados:** gerar grafos parciais com 10%, 20%, ..., 100% das arestas observadas. A divisão entre treino, validação e teste será feita por campanha antes dessas janelas.
4. **Features iniciais:** calcular usuários ativos, arestas, `Interaction_Count`, graus, densidade, reciprocidade, componentes, concentração e velocidade de crescimento.
5. **Baseline:** comparar regras simples e classificadores tabulares, como regressão logística ou árvore, com normalização e tratamento de valores ausentes definidos no treino.
6. **Modelos temporais:** após validar o baseline, avaliar representações temporais de grafos e, se houver justificativa e ambiente reproduzível, modelos de aprendizado profundo para grafos.
7. **Avaliação:** medir acurácia balanceada, precisão, revocação, F1, ROC-AUC, PR-AUC, calibração e desempenho por fração temporal. Também serão analisados falsos positivos, falsos negativos e o ponto de antecedência em que a decisão atinge um nível de confiança definido.

Os resultados esperados são: uma base canônica e documentada; tabelas e gráficos reproduzíveis da EDA; um pipeline sem vazamento temporal; uma comparação transparente de baselines; e uma estimativa de quanto da evolução da rede é necessária para detectar uma campanha. Não se espera, nesta etapa, demonstrar uma solução pronta para moderação em produção. O resultado principal será evidência experimental sobre a viabilidade e as limitações da detecção precoce no LEN.

## 9. Referências citadas

GOPALAKRISHNAN, A. A.; HOSSAIN, J.; ELMAS, T.; SARIYÜCE, A. E. *Large Engagement Networks for Classifying Coordinated Campaigns and Organic Twitter Trends*. Proceedings of the International AAAI Conference on Web and Social Media, v. 19, n. 1, p. 688–702, 2025. DOI: [10.1609/icwsm.v19i1.35839](https://doi.org/10.1609/icwsm.v19i1.35839).

GOPALAKRISHNAN, A. A.; HOSSAIN, J.; ELMAS, T.; SARIYÜCE, A. E. *Large Engagement Network*. Página do projeto e dataset. Disponível em: <https://erdemub.github.io/large-engagement-network/>. Acesso em: 15 set. 2026.

## 10. Bibliografia

GUDIVADA, V. N.; RAGHAVAN, V. V.; KOHLER, W. W. Web 2.0 and its implications for data management. *Journal of Information Science*, v. 35, n. 4, 2009.

MITCHELL, M. *Artificial Intelligence: A Guide for Thinking Humans*. New York: Farrar, Straus and Giroux, 2019.

NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. Gaithersburg: NIST, 2023. DOI: [10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1).

NEWMAN, M. E. J. *Networks: An Introduction*. Oxford: Oxford University Press, 2010.

RECUERO, R. *Redes sociais na internet*. Porto Alegre: Sulina, 2009.

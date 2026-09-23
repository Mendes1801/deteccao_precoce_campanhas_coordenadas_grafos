# Large Engagement Networks (LEN): tradução orientada e resumo analítico

## Referência

GOPALAKRISHNAN, Atul Anand; HOSSAIN, Jakir; ELMAS, Tuğrulcan; SARIYÜCE, Ahmet Erdem. **Large Engagement Networks for Classifying Coordinated Campaigns and Organic Twitter Trends**. *Proceedings of the International AAAI Conference on Web and Social Media*, v. 19, n. 1, p. 688-702, 2025. DOI: 10.1609/icwsm.v19i1.35839.

## Nota sobre esta tradução

Esta é uma tradução acadêmica não oficial, preparada para estudo. Ela preserva o conteúdo substantivo do artigo: resumo, introdução, trabalhos relacionados, construção do conjunto de dados, experimentos, resultados, limitações, ética e elementos principais do apêndice. As referências bibliográficas e o checklist padronizado de ética da conferência não foram traduzidos integralmente, pois não acrescentam conteúdo metodológico novo. Termos técnicos importantes são acompanhados do original em inglês na primeira ocorrência.

# Resumo detalhado e análise para o TCC

## 1. Qual é o problema investigado?

O artigo parte de uma dificuldade básica: nas redes sociais, um assunto pode se tornar popular porque muitas pessoas passaram a discuti-lo espontaneamente ou porque um grupo coordenado inflou artificialmente sua visibilidade. Observando somente o resultado final - um tópico nos assuntos do momento -, essas duas origens podem parecer semelhantes.

O principal obstáculo para treinar classificadores é a falta de um **rótulo confiável**, ou *ground truth*. Em situações reais, quase nunca existe prova direta de que determinada tendência foi produzida por coordenação. Os autores contornam esse problema usando um tipo específico e muito reconhecível de manipulação: o **astroturfing efêmero**.

Nesse ataque, centenas ou milhares de contas publicam, em poucos segundos, mensagens geradas aleatoriamente que contêm uma palavra ou hashtag escolhida. Logo depois, as mensagens são apagadas. Mesmo assim, o algoritmo de tendências do Twitter pode contabilizá-las e promover o tópico. Esse padrão fornece aos autores um sinal forte de que houve uma campanha coordenada.

## 2. Qual é a principal contribuição?

A contribuição principal não é um novo classificador. É o conjunto de dados **LEN - Large Engagement Networks**, construído para classificação de grafos sociais grandes.

O LEN contém:

- 314 redes de engajamento;
- 179 redes classificadas como campanhas;
- 135 redes classificadas como não campanhas;
- média aproximada de 11.769 nós e 23.594 arestas por grafo;
- redes com 100 a 119.952 nós;
- redes com 203 a 1.105.918 arestas;
- rótulos mais específicos para tipos de campanha e de não campanha;
- atributos de nós, arestas e textos associados às interações.

Os autores também fornecem o **LEN-small**, uma versão balanceada com as 100 menores redes: 51 campanhas e 49 não campanhas. Essa versão foi criada para permitir experimentos mais rápidos.

## 3. Como cada rede é construída?

Cada tópico ou tendência origina um grafo direcionado de engajamento:

- cada nó representa um usuário;
- uma aresta de A para B indica que A retuitou, respondeu ou citou B;
- quando A interagiu várias vezes com B, somente a interação mais recente foi mantida;
- essa simplificação preservou aproximadamente 74% das arestas originais.

Os atributos dos nós incluem:

- descrição do perfil;
- número de seguidores;
- número de contas seguidas;
- número total de publicações;
- estado de verificação da conta.

Os atributos das arestas incluem:

- tipo de engajamento: retuíte, resposta ou citação;
- texto da publicação;
- número de impressões;
- quantidade de engajamentos;
- número de curtidas;
- horário da publicação;
- indicação de conteúdo sensível.

A descrição do perfil e o texto da publicação são transformados em vetores numéricos com o modelo multilíngue LaBSE.

## 4. Como os autores rotulam as campanhas?

Os autores coletaram, entre março e maio de 2023, uma amostra em tempo real correspondente a 1% das publicações do Twitter, concentrando-se em mensagens em turco. Um classificador baseado em regras identificou mensagens que pareciam ter sido geradas a partir de um vocabulário aleatório.

Uma mensagem era considerada desse tipo quando:

- tinha entre 2 e 9 tokens;
- não continha pontuação;
- começava com letra minúscula.

Quatro mensagens consecutivas com esse padrão, publicadas em segundos, mencionando a mesma hashtag ou palavra e posteriormente apagadas, eram interpretadas como indício de astroturfing efêmero. Na amostra de 1%, isso equivaleria, de forma aproximada, a 400 mensagens no fluxo completo do Twitter.

Estudos anteriores reportaram 100% de precisão e 99% de revocação para essa regra no contexto analisado. Os autores encontraram dois falsos positivos, as palavras “one” e “May”, e passaram a descartar palavras-alvo com menos de cinco caracteres.

Foram identificadas inicialmente 190 tendências falsas. Em julho de 2023, os autores coletaram as publicações relacionadas a essas tendências durante dois dias. Como as mensagens dos bots já haviam sido apagadas, o conteúdo coletado representava principalmente a atividade posterior de usuários e apoiadores do tópico. Foram removidas as tendências com menos de mil publicações. O texto informa 179 campanhas no conjunto final, embora a aritmética descrita nessa passagem - 190 menos 20 - não seja suficiente, sozinha, para chegar a 179. Essa pequena inconsistência textual merece ser registrada.

Dois pesquisadores falantes de turco classificaram manualmente os tipos de campanha; um terceiro resolveu os desacordos.

## 5. Como os autores rotulam as não campanhas?

Os autores reconhecem que a ausência do ataque efêmero não prova que uma tendência seja orgânica. Outros tipos de coordenação podem existir, inclusive organização em aplicativos de mensagem. Por isso, eles adotam uma estratégia conservadora: selecionam tendências associadas a acontecimentos externos de interesse nacional, para os quais seria plausível que muitas pessoas publicassem de forma independente.

As 135 não campanhas incluem:

- notícias sobre pessoas ou lugares;
- discussões surgidas no Twitter que depois chegaram à mídia tradicional;
- eventos esportivos;
- programas de televisão e vídeos populares;
- festivais, feriados e datas especiais;
- hashtags ou expressões comuns;
- algumas campanhas oficiais, políticas ou esportivas, que tiveram ampla discussão pública.

Esse processo prioriza precisão, não cobertura. Portanto, “não campanha” significa, na prática, “caso cuidadosamente selecionado como provavelmente orgânico”, e não ausência comprovada de qualquer coordenação.

## 6. Quais tipos de campanha existem?

As campanhas foram divididas em política, reforma, notícias, finanças, ruído, culto, entretenimento e expressões comuns. A maior parte está concentrada em política e reforma.

As não campanhas incluem notícias, esportes, festivais, eventos internos à plataforma, expressões comuns, entretenimento, campanhas oficiais anunciadas e campanhas esportivas.

Há uma diferença importante de tamanho: as não campanhas possuem, em média, redes maiores. Campanhas têm, em média, cerca de 5.157 nós e 16.006 arestas; não campanhas têm aproximadamente 20.632 nós e 33.765 arestas. Essa diferença pode funcionar como um atalho para os classificadores e precisa ser controlada ou discutida em qualquer experimento derivado.

## 7. Quais modelos foram avaliados?

Os autores testam oito abordagens:

1. **Texto + MLP:** ignora a estrutura do grafo e classifica a concatenação das médias dos vetores das descrições dos usuários e dos textos.
2. **GCN:** agrega informações dos vizinhos com normalização pelo grau dos nós.
3. **GAT:** usa atenção para atribuir pesos diferentes às mensagens recebidas de cada vizinho.
4. **GIN:** arquitetura mais expressiva que diferencia estruturas de vizinhança por meio de uma rede multicamadas.
5. **GraphSAGE:** aprende a agregar amostras das vizinhanças e pode generalizar para nós não vistos durante o treinamento.
6. **GINE:** variante de GIN que incorpora atributos das arestas.
7. **VNGE:** representação espectral baseada na entropia de Von Neumann.
8. **NetLSD/LSD:** descrição espectral da forma do grafo baseada no núcleo de calor.

As GNNs usam duas camadas, seguidas de média global dos nós e uma MLP de duas camadas para prever a classe do grafo.

## 8. Como foi feita a avaliação?

Os dados foram separados por amostragem estratificada em 75% para treinamento e 25% para teste. Os autores ajustaram taxa de aprendizado e dimensão das camadas ocultas. Cada combinação das GNNs foi executada cinco vezes com sementes aleatórias diferentes, e foram apresentadas médias e dispersões.

Para classificação binária, as métricas são acurácia, precisão, revocação e F1. Para classificação multiclasse, são usadas acurácia, precisão e revocação ponderadas, micro-F1 e macro-F1.

O artigo não descreve validação cruzada nem separação por origem temporal. Como o objetivo original é fornecer um *benchmark*, isso é compreensível, mas para detecção precoce será necessário um desenho experimental mais cuidadoso, especialmente para evitar que informações futuras ou relacionadas à mesma campanha apareçam nos dois lados da divisão.

## 9. Principais resultados da classificação binária

No LEN-small, GraphSAGE obteve a maior acurácia, 0,900, enquanto VNGE apresentou F1 de 0,857 e GraphSAGE F1 de 0,884. No conjunto completo, os resultados caíram:

- VNGE: acurácia 0,747 e F1 0,767;
- LSD: acurácia 0,734 e o melhor F1, 0,788;
- GAT: acurácia 0,735 e F1 0,765;
- GINE: acurácia 0,648 e F1 0,748;
- GraphSAGE: acurácia 0,729, precisão 0,930 e revocação 0,578;
- Texto + MLP: acurácia 0,570 e F1 0,701.

O resultado mais importante não é apenas qual modelo venceu. Os descritores espectrais VNGE e LSD, que não são redes neurais, foram tão bons quanto ou melhores do que várias GNNs. Isso sugere que propriedades globais da estrutura podem ser particularmente informativas e que modelos mais complexos não garantem melhor desempenho.

A queda do LEN-small para o LEN completo mostra que o tamanho e a diversidade das redes tornam a tarefa mais difícil. Ela também alerta para o risco de conclusões otimistas baseadas apenas na versão pequena.

## 10. Resultados da classificação do tipo de campanha

Os autores tentam classificar sete tipos: política, reforma, notícia, finanças, culto, entretenimento e expressão comum. Os resultados são substancialmente piores que os da classificação binária.

No LEN completo, a maior acurácia é 0,677, com GINE. Entretanto, os valores de macro-F1 são baixos; o melhor reportado é 0,383 para VNGE. As matrizes de confusão mostram que muitos exemplos são classificados como política ou reforma, as classes predominantes.

Isso demonstra que a acurácia isolada esconderia o baixo desempenho nas classes raras. Para o TCC, esse resultado reforça a necessidade de acompanhar PR-AUC, F1 por classe, macro-F1 e matrizes de confusão quando houver desbalanceamento.

## 11. Resultados apenas para redes de notícias

O artigo também compara 24 notícias amplificadas por campanhas com 24 redes de notícias provavelmente orgânicas. É um teste mais difícil porque os dois grupos compartilham o mesmo tema geral; o que muda é o processo de formação.

LSD alcança o melhor F1, 0,800. GraphSAGE, VNGE e LSD atingem acurácia próxima de 0,769. Os demais modelos ficam abaixo. O desempenho inferior ao teste geral mostra que parte da separação entre todas as campanhas e não campanhas pode ser explicada pelas diferenças de assunto e de tamanho, não somente por padrões genuínos de coordenação.

## 12. Limitações reconhecidas pelos autores

1. **Acesso à API:** o fluxo de 1% do Twitter deixou de estar disponível. Isso impede reproduzir a detecção em tempo real dos bots que apagam rapidamente as mensagens.
2. **Custo de coleta:** o acesso a grandes volumes passou a ser proibitivamente caro.
3. **Simplificação das arestas:** somente a interação mais recente entre dois usuários é preservada, descartando cerca de 26% das interações.
4. **Viés de tamanho e popularidade:** não campanhas tendem a ser eventos mais populares e geram redes maiores.
5. **Cobertura limitada dos ataques:** o conjunto assume que o astroturfing efêmero era a principal estratégia de criação de tendências falsas por bots no período e contexto estudados.
6. **Rótulos negativos heurísticos:** não campanhas foram anotadas manualmente; elas não possuem prova negativa absoluta.
7. **Contexto geográfico:** os dados se concentram na Turquia e em língua turca.
8. **Interpretação dos rótulos:** uma campanha apoiada por bots não é necessariamente totalmente falsa ou desprovida de apoio humano genuíno.

## 13. Cuidados éticos

O conjunto usa somente perfis públicos. Identificadores de usuários foram ocultados, incluindo ID, nome, nome de exibição e identificadores de usuários retuitados, mencionados ou respondidos. Dados completos podem ser concedidos a pesquisadores mediante solicitação razoável.

Os autores alertam explicitamente que o conjunto não deve ser usado para declarar que toda campanha classificada como coordenada é inteiramente inautêntica. Coordenação e autenticidade não são opostos absolutos: uma mobilização pode ter apoio humano legítimo e, ao mesmo tempo, receber amplificação artificial.

## 14. Relação direta com o TCC de detecção precoce

O artigo fornece três elementos essenciais:

- a unidade experimental: uma rede de engajamento por tópico;
- os rótulos: campanha ou não campanha;
- os dados temporais nas arestas: horário das publicações.

Mas ele trabalha com **grafos completos e estáticos**, agregando toda a atividade coletada. O artigo não responde:

- quanto da campanha precisa ser observado para classificá-la;
- em qual instante os sinais estruturais passam a ser discriminativos;
- quais atributos aparecem mais cedo;
- como o desempenho evolui de 10% para 20%, 30% e assim por diante;
- qual é o compromisso entre rapidez e confiabilidade;
- se os modelos continuam funcionando quando o corte de teste respeita o tempo.

Essa é a principal lacuna que o TCC pode explorar. A contribuição proposta não é repetir a classificação do LEN, mas transformar cada rede agregada em uma sequência ordenada de estados parciais e medir o desempenho em cada estágio.

## 15. Pontos metodológicos que o TCC deve observar

### 15.1 Evitar vazamento temporal

Em uma janela parcial, nenhum atributo pode utilizar informação posterior ao limite daquela janela. Graus, comunidades, contagens, textos agregados e estatísticas precisam ser recalculados somente com os eventos observados até o corte.

### 15.2 Controlar o atalho do tamanho

Como as não campanhas são maiores em média, um modelo pode aprender “rede grande = orgânica” em vez de aprender coordenação. Convém avaliar:

- modelos com e sem número de nós e arestas;
- atributos normalizados pelo tamanho;
- subconjuntos balanceados por escala;
- desempenho por faixas de tamanho.

### 15.3 Preservar interações repetidas

Para estudar evolução temporal, descartar todas as interações anteriores entre um mesmo par pode remover justamente a repetição e a intensidade da coordenação. É melhor manter um registro de eventos com timestamp e somente projetá-lo em um grafo simples quando uma métrica exigir isso.

### 15.4 Comparar modelos simples e complexos

Como VNGE e LSD foram competitivos no artigo, o TCC deve incluir modelos sobre atributos agregados, como regressão logística, Random Forest ou XGBoost, antes de concluir que GNNs temporais são necessárias.

### 15.5 Usar métricas adequadas

Acurácia e ROC-AUC não bastam quando as classes são desbalanceadas ou quando o custo de falso positivo é relevante. Recomenda-se relatar PR-AUC, precisão, revocação, F1, matriz de confusão e, se possível, intervalos de confiança.

## 16. Avaliação crítica

O trabalho é valioso porque fornece um conjunto raro de grafos sociais grandes com rótulos de coordenação relativamente fortes. Sua maior força é vincular as campanhas a um mecanismo observável de manipulação, evitando depender somente da opinião de anotadores ou da classificação do conteúdo.

Ao mesmo tempo, o rótulo da rede não é uma observação direta de toda a sua formação. O ataque efêmero serve para colocar o tópico nas tendências; depois, os autores coletam a rede de engajamento quando as mensagens dos bots já foram apagadas. Assim, o grafo disponibilizado representa principalmente a atividade que segue a promoção inicial. A relação causal entre a estrutura final e o ataque original precisa ser interpretada com cuidado.

Também existe risco de confusão entre classe, tema e tamanho. Campanhas e não campanhas possuem distribuições diferentes de assunto e escala. O experimento restrito a notícias reduz parcialmente essa confusão e, de fato, apresenta desempenho menor. Isso é uma evidência de que o problema real é mais difícil do que os resultados gerais sugerem.

Por fim, a divisão aleatória 75/25 é suficiente para um primeiro *benchmark*, mas não prova generalização temporal, geográfica ou entre tipos de campanha. O TCC pode avançar nesse ponto com divisões por campanha, período e categoria, desde que o número de exemplos permita.

# Tradução orientada do artigo

## Título

**Grandes Redes de Engajamento para Classificar Campanhas Coordenadas e Tendências Orgânicas do Twitter**

## Resumo

Usuários de redes sociais e contas inautênticas, como bots, podem agir de forma coordenada para promover determinados tópicos. Esses tópicos podem dar a impressão de serem organicamente populares entre o público, embora sejam campanhas de astroturfing administradas de maneira centralizada. É difícil prever se um tópico é orgânico ou uma campanha coordenada devido à falta de rótulos confiáveis.

Neste artigo, criamos esses rótulos detectando campanhas promovidas por ataques de astroturfing efêmero. Esses ataques levam qualquer tópico à lista de tendências do Twitter (X) mediante o uso de bots que publicam de maneira coordenada durante um curto período e apagam imediatamente suas mensagens. Também selecionamos manualmente um conjunto de tendências orgânicas do Twitter.

A partir desses dados, criamos redes de engajamento que podem servir como um conjunto de testes desafiador para a tarefa de classificação de grafos, distinguindo campanhas de tendências orgânicas. Nessas redes, os nós representam usuários e as arestas representam engajamentos - retuítes, respostas e citações - entre os usuários.

Disponibilizamos redes de engajamento para 179 campanhas e 135 não campanhas, além de rótulos mais detalhados que caracterizam seus tipos. Nosso conjunto de dados, LEN (*Large Engagement Networks*), está disponível publicamente. Em comparação com conjuntos tradicionais de classificação de grafos, que normalmente possuem dezenas de nós e poucas centenas de arestas, os grafos do LEN são maiores. Em média, cada grafo possui aproximadamente 11 mil nós e 23 mil arestas.

Mostramos que métodos de GNN considerados estado da arte obtêm somente resultados medianos na classificação campanha versus não campanha e na classificação do tipo de campanha. O LEN oferece um ambiente desafiador para a classificação de grafos e pode contribuir para avançar as técnicas de classificação de redes grandes, além de oferecer um caso de uso relevante: distinguir campanhas coordenadas de tendências orgânicas.

## Introdução

As redes sociais funcionam como um sensor do sentimento público, refletindo assuntos populares que despertam interesse amplo por meio de discussões orgânicas. O Twitter, recentemente renomeado como X, monitora tópicos populares e os publica em sua página principal como tendências, sugerindo que são amplamente discutidos pelos usuários.

Entretanto, esforços coordenados podem manipular a percepção sobre determinados assuntos. Usuários com objetivos comuns podem tentar aumentar artificialmente a popularidade de um tópico para promover suas campanhas. Para isso, podem utilizar contas falsas e bots de forma coordenada, ocultando a natureza inautêntica dessas contas. Essa estratégia é conhecida como astroturfing. Tais ações dificultam distinguir assuntos genuinamente populares de campanhas coordenadas. As tendências do Twitter são vulneráveis a esse tipo de manipulação, já observado em países como Paquistão, Índia e Turquia.

Este trabalho concentra-se no caso turco, em que os adversários empregam principalmente um ataque chamado astroturfing efêmero. Um conjunto de bots promove um tópico - uma hashtag ou sequência de palavras que representa uma campanha - publicando-o em massa dentro de textos gerados aleatoriamente a partir de um vocabulário. Em seguida, os bots apagam imediatamente as mensagens. Apesar disso, os tópicos ainda aparecem na lista de tendências.

Como esse ataque é eficaz e, ao mesmo tempo, fácil de reconhecer por seu padrão específico de atividade, ele permite estabelecer rótulos confiáveis para tópicos que representam campanhas.

O objetivo do trabalho é criar um conjunto de referência para classificação de grafos baseado em redes de engajamento do Twitter turco. Esse conjunto deve permitir identificar grafos de campanha e realizar tarefas derivadas, como reconhecer o tipo de campanha.

Para isso, os autores detectam ataques de astroturfing efêmero e classificam os tópicos-alvo como campanhas. A verificação manual mostra que eles estão principalmente ligados a política, promoções financeiras - como criptomoedas - e grupos que se organizam em defesa de reformas. Os dados são convertidos em redes nas quais usuários são nós e retuítes, respostas e citações formam arestas.

O LEN contém 314 redes grandes: 179 campanhas e 135 não campanhas. O artigo informa médias de 11.769 nós e 23.593 arestas. Também fornece rótulos mais específicos para os tipos de campanha e de não campanha. O conjunto é disponibilizado sob licença CC-BY.

O restante do artigo apresenta fundamentos e trabalhos relacionados, descreve a coleta e a conversão dos dados em grafos, avalia métodos de classificação e discute limitações e questões éticas.

## Trabalhos relacionados

### Métodos de classificação de grafos

A classificação de grafos é uma tarefa fundamental de aprendizado de máquina, com aplicações em bioinformática, química, análise de redes sociais e detecção de programas maliciosos. Em termos gerais, cria-se uma representação numérica para cada grafo e utiliza-se essa representação para classificá-lo.

Existem duas famílias principais: núcleos de grafos (*graph kernels*) e redes neurais de grafos. Os núcleos medem a semelhança entre pares de grafos mediante funções que comparam propriedades estruturais. Essas semelhanças formam uma matriz que pode ser fornecida a um classificador como uma SVM. Há métodos baseados em caminhadas aleatórias, caminhos mínimos, correspondência entre grafos, vizinhanças e pequenos subgrafos.

A principal limitação dos núcleos é a impossibilidade de aprender simultaneamente a extração de características e a tarefa de classificação. As GNNs procuram superar essa limitação por meio da passagem de mensagens. Cada nó mantém uma representação, envia-a aos vizinhos, agrega as mensagens recebidas e atualiza sua própria representação.

GCN normaliza as mensagens pelo grau dos nós. GAT utiliza atenção para atribuir pesos diferentes aos vizinhos. GIN emprega uma rede multicamadas na agregação e um parâmetro treinável que controla a importância do próprio nó. Para obter uma representação de todo o grafo, as representações dos nós são combinadas por uma função de agregação, como máximo ou média.

Agregações simples podem perder informação estrutural. Existem métodos mais elaborados, incluindo SORTPOOL e técnicas hierárquicas que reduzem progressivamente o grafo. Mesmo assim, GNNs podem ter dificuldade para capturar informação global e dependências de longa distância, sofrendo fenômenos conhecidos como suavização excessiva e compressão excessiva das mensagens. Neste artigo, os autores usam média global porque seu objetivo principal é verificar como modelos de aprendizado em grafos se comportam no LEN.

### Conjuntos de dados para classificação de grafos

Muitos conjuntos conhecidos vêm da biologia e da química. Neles, os nós representam átomos, moléculas ou proteínas, e os rótulos indicam propriedades químicas e biológicas. Outros conjuntos representam atores ligados por filmes, autores ligados por colaborações ou usuários ligados por respostas no Reddit.

Uma característica comum é o tamanho reduzido dos grafos. Muitas redes possuem somente dezenas de nós, o que limita a quantidade de informação relacional e não testa adequadamente a capacidade dos modelos em estruturas complexas. O MalNet é uma exceção, com grafos de chamadas de funções maiores, embora os autores observem problemas de duplicação nessa base.

O LEN procura preencher essa lacuna com redes sociais muito maiores. Sua versão completa tem 314 grafos, aproximadamente 11.769 nós e 23.594 arestas em média, além de 15 categorias quando os subtipos de campanhas e não campanhas são contados em conjunto.

### Manipulação de tendências

Embora o foco principal seja classificação de grafos, o trabalho também contribui para o estudo de desinformação e propaganda ao oferecer dados de campanhas coordenadas. Trabalhos anteriores investigaram comportamento de usuários, conteúdo, estratégias e redes de contas inautênticas, bots, grupos de seguimento recíproco, tópicos patrocinados e criptomoedas. GCNs também já foram aplicadas à detecção de notícias falsas e rumores.

O caso apresentado neste artigo é específico: usuários organizam-se para promover um tópico como parte de uma campanha. Essa formulação é difícil porque raramente existe prova de que as pessoas se organizaram para promover determinado tópico.

Os autores obtêm esse rótulo por meio das tendências falsas. Estudos anteriores observaram manipulação coordenada das tendências na Índia e no Paquistão. A diferença deste trabalho é fornecer um conjunto anotado, em larga escala, de tendências falsas para as quais existe evidência forte de que bots foram usados. O artigo amplia o trabalho de Elmas e colaboradores ao reformular a detecção dessas tendências como classificação de grafos.

## Redes de engajamento: campanha ou não?

Os autores coletam dois tipos de dados. As campanhas são obtidas pela detecção, em tempo real, de ataques de astroturfing efêmero. As não campanhas são selecionadas por anotação manual entre tendências populares que não foram alvo desse ataque.

### Metodologia de coleta das campanhas

Os adversários escolhem uma palavra ou expressão que desejam colocar nas tendências, muitas vezes como parte de uma transação comercial. Em seguida, centenas ou milhares de bots publicam o alvo de maneira coordenada. Para contornar filtros de spam, os textos são construídos escolhendo aleatoriamente palavras de um vocabulário. As mensagens são apagadas logo após a publicação.

O algoritmo de tendências não considera adequadamente essas exclusões e ainda pode marcar o assunto como popular. Depois que o alvo entra nas tendências, outros usuários, geralmente ligados aos patrocinadores e já cientes da operação, passam a mencioná-lo para ampliar ainda mais sua visibilidade.

Para detectar esses ataques, os autores coletaram a amostra de 1% de todas as publicações disponibilizada em tempo real pela API do Twitter. O foco foi a Turquia e mensagens em turco. Um classificador por regras marcou como “texto de vocabulário” as mensagens com 2 a 9 tokens, sem pontuação e iniciadas por letra minúscula.

Quatro mensagens consecutivas desse tipo, mencionando a mesma hashtag ou palavra e posteriormente apagadas, indicavam um ataque. Na totalidade do Twitter, isso corresponderia aproximadamente a 400 mensagens com a mesma hashtag e padrão textual, publicadas em poucos segundos. A metodologia já havia atingido 100% de precisão e 99% de revocação em trabalho anterior.

Entre março e maio de 2023, antes das eleições gerais turcas de 14 de maio, os autores identificaram 190 tendências falsas. Em julho, coletaram todas as mensagens referentes a essas tendências durante dois dias. Nesse momento, as mensagens dos bots já haviam sido removidas, reduzindo o ruído gerado pelo ataque inicial.

Tendências com menos de mil publicações foram excluídas porque poderiam não possuir apoio suficiente de uma campanha coordenada ou poderiam ter perdido mensagens devido a intervenções da plataforma. As tendências restantes formaram as 179 campanhas do LEN.

Dois pesquisadores falantes de turco classificaram manualmente os tipos das campanhas, e um terceiro resolveu os desacordos. Entre as 179 tendências, 24 eram notícias que também poderiam ter provocado discussão genuína, mas haviam sido amplificadas por bots e trolls. Em nove casos, os pesquisadores não conseguiram determinar qual grupo promovia o assunto; esses casos foram mantidos com o rótulo “ruído”.

### Metodologia de coleta das não campanhas

A ausência do ataque detectado não permite concluir que uma tendência seja completamente livre de coordenação. Pessoas podem se organizar por outros meios, como aplicativos de mensagem. Por isso, os autores realizam anotação manual.

A hipótese adotada é que tendências ligadas a eventos externos de interesse nacional têm maior probabilidade de serem orgânicas, pois muitas pessoas podem publicar independentemente sobre elas. Além disso, adversários teriam menos incentivo para promover assuntos que já estão nas tendências, porque suas mensagens seriam diluídas na discussão geral.

Foram anotadas tendências referentes a pessoas ou lugares mencionados em notícias, acontecimentos que surgiram na plataforma e chegaram à mídia tradicional, eventos esportivos, programas de televisão ou YouTube, datas especiais e expressões comuns. Algumas hashtags correspondiam a campanhas oficiais políticas ou esportivas, mas foram amplamente discutidas. Casos que não se enquadravam nessas categorias foram descartados. No total, foram selecionadas 135 não campanhas, buscando maximizar a precisão dos rótulos.

### Construção das redes

Com os dados coletados, os autores constroem redes direcionadas. Os nós representam usuários. Uma aresta de A para B indica que A retuitou, respondeu ou citou B. Quando um usuário interagiu repetidamente com outro, somente a interação mais recente foi mantida. Esse procedimento preservou cerca de 74% das arestas.

Os atributos dos nós vêm dos perfis. Os atributos das arestas vêm das publicações que geraram a interação. Textos e descrições são codificados pelo LaBSE, um modelo multilíngue de representação de sentenças.

O LEN completo possui 314 grafos, 179 de campanha e 135 de não campanha. Há sete subtipos usados na classificação multiclasse de campanhas e oito subtipos de não campanhas. O número de nós varia de 100 a 119.952, e o número de arestas varia de 203 a 1.105.918.

Para facilitar experimentos rápidos, os autores criam o LEN-small, formado pelas 100 menores redes: 51 campanhas e 49 não campanhas. Nessa versão, o número de nós varia de 100 a 8.355, com média de 2.079; as arestas variam de 203 a 10.608, com média de 2.696.

## Classificação das redes de engajamento

Os experimentos abrangem três tarefas:

1. distinguir campanhas de não campanhas;
2. classificar campanhas em sete subtipos;
3. distinguir campanhas de não campanhas somente entre redes relacionadas a notícias.

Os dados são divididos por amostragem estratificada: 75% para treinamento e 25% para teste. Para classificação binária são usadas acurácia, precisão, revocação e F1. Na tarefa multiclasse, são utilizadas acurácia, precisão e revocação ponderadas, micro-F1 e macro-F1.

### Classificador sem grafo

Para evidenciar o valor da estrutura, os autores utilizam um modelo que ignora as conexões. Ele calcula a média das representações das descrições dos usuários e a média das representações dos textos, concatena os dois vetores e os fornece a uma MLP.

### Classificadores de grafos

Foram avaliados GCN, GAT, GIN, GraphSAGE e GINE. Também foram usados dois descritores não neurais, VNGE e NetLSD. Cada GNN tem duas camadas, seguida de média global das representações dos nós e de uma MLP de duas camadas.

As taxas de aprendizado testadas foram 0,001, 0,0001 e 0,00001. As dimensões ocultas foram 128, 256, 512 e 1.024. Cada combinação foi executada cinco vezes com sementes diferentes, e os autores reportam as médias. VNGE e LSD também tiveram seus parâmetros ajustados por busca em grade.

### Classificação binária

No LEN-small, GraphSAGE obtém a melhor acurácia. No LEN completo, VNGE apresenta a melhor acurácia e LSD o melhor F1. Os resultados são inferiores no conjunto completo, indicando que redes grandes são mais difíceis de classificar.

Na análise de tempo de execução, GCN, GIN e GAT sofrem pouca alteração com o tamanho dos grafos nas condições testadas, enquanto o custo do GINE cresce de maneira aproximadamente linear.

### Classificação do tipo de campanha

As campanhas são separadas em política, reforma, notícia, finanças, culto, entretenimento e expressão comum. A identificação do tipo apenas pela estrutura é mais difícil que a classificação binária.

VNGE obtém a maior acurácia no LEN-small; GINE obtém a maior acurácia no LEN completo. Apesar de valores razoáveis de micro-F1, os valores de macro-F1 são baixos. As matrizes de confusão revelam que muitos grafos são classificados como política ou reforma, refletindo o desbalanceamento entre as classes.

### Classificação apenas de notícias

O artigo compara 24 notícias amplificadas por bots e trolls com 24 redes de notícias formadas organicamente em torno de acontecimentos populares. Como as redes compartilham um tema semelhante e diferem principalmente no processo de formação, esse subconjunto é especialmente desafiador.

LSD apresenta os melhores resultados gerais, com F1 de 0,800. Os resultados dos demais modelos são consistentemente menores que os obtidos na classificação de todas as redes.

## Limitações

A coleta foi realizada antes da restrição da API do Twitter. A plataforma retirou o acesso ao fluxo de 1% das publicações, tornando inviável detectar em tempo real bots que apagam imediatamente suas mensagens. A coleta em larga escala também se tornou cara, o que dificulta reproduzir ou ampliar o LEN.

Ao construir os grafos, somente a interação mais recente entre dois usuários foi mantida. Embora cerca de 74% das arestas tenham sido preservadas, parte da atividade foi descartada.

O conjunto também apresenta possível viés em favor de eventos populares. As não campanhas são maiores porque eventos pouco populares normalmente não entram nas tendências ou não satisfazem os critérios de anotação.

A atividade adversarial é variada e evolui. O astroturfing efêmero pode não ser a única estratégia de criação de tendências falsas. Os autores adotam essa estratégia como principal com base em estudos anteriores. Para reduzir o risco de rotular como orgânicas campanhas produzidas por outros métodos, selecionam as não campanhas manualmente e de forma conservadora.

## Ética

O conjunto contém apenas usuários com perfis públicos. Para proteger a privacidade, os autores ocultam informações identificadoras, incluindo IDs, nomes, identificadores de conta e os IDs de usuários envolvidos em retuítes, menções e respostas. O acesso completo pode ser concedido a pesquisadores mediante solicitação razoável.

Embora as campanhas tenham recebido apoio de bots e fossem, portanto, parcialmente inautênticas, não seria correto classificá-las como totalmente inautênticas ou sem qualquer apoio legítimo. O trabalho não deve ser usado para invalidar essas campanhas nem para classificar outros movimentos como falsos apenas com base em um modelo treinado no LEN.

## Elementos principais do apêndice

A maior componente conexa representa, em média, aproximadamente 76,7% dos nós das campanhas e 81,6% dos nós das não campanhas. Isso mostra que a maior parte dos usuários está ligada a um núcleo principal, embora existam componentes menores e isolados.

As curvas ROC fornecidas no apêndice mostram o comportamento dos classificadores no LEN-small e no LEN completo. Como as classes e subtipos possuem distribuições diferentes, essas curvas devem ser interpretadas junto de precisão, revocação e F1.

## Síntese em uma frase

O artigo cria um conjunto de 314 grandes redes de engajamento, rotuladas como campanhas coordenadas ou tendências provavelmente orgânicas, mostra que modelos atuais ainda têm desempenho limitado nessa classificação e deixa em aberto a questão central do TCC: **quão cedo, durante a formação da rede, essa distinção se torna possível?**

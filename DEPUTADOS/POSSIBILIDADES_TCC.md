# Possibilidades do TCC e entrega interativa

Atualização de 21/10/2026, após a orientação. Este documento passa a orientar a escolha do tema; o EDA de agosto/2023 permanece como piloto técnico.

## O que foi estabelecido

- O estudo final deve abranger pelo menos vinte anos. Janela de trabalho proposta: **2006–2025**, vinte anos civis completos. A cobertura efetiva da análise escolhida ainda precisa ser confirmada.
- A entrega final será um **site público de exploração das análises**, com grafos e informações interativas. A pergunta de pesquisa e as análises serão discutidas com o orientador.
- A tarefa atual é um levantamento leve de possibilidades, sem baixar ou analisar em profundidade toda essa série histórica.
- A extração definitiva deve ocorrer somente após escolher quais dados respondem à pergunta de pesquisa.

## Evidência leve: cinco momentos, não vinte anos analisados

Foi executado `sondagem_historica.py`, usando 35 consultas de aplicação à API, sem calcular redes históricas nem totais anuais.
Foram inspecionadas as primeiras páginas de março e agosto de 2006, 2011, 2016, 2021 e 2025: até cinquenta metadados por mês. Entre elas, uma decisão por ano foi priorizada pelo placar descrito; foram consultados seus votos e orientações. Também foi escolhido um PL por ano, com seus autores e temas.

| Ano de referência | Metadados de decisões inspecionados | Votos individuais na decisão escolhida | Autores no PL escolhido | Temas no PL escolhido |
| --- | --- | --- | --- | --- |
| 2006 | 50 | 0, lista vazia | 1 | 1 |
| 2011 | 97 | 0, lista vazia | 1 | 1 |
| 2016 | 100 | 447 | 2 | 1 |
| 2021 | 100 | 467 | 15 | 1 |
| 2025 | 95 | 462 | 1 | 1 |

Esses valores descrevem exclusivamente as respostas escolhidas. Não são contagens anuais nem medidas de produção parlamentar. As listagens foram deliberadamente limitadas; não há representatividade estatística.

Lista vazia em uma decisão antiga não demonstra inexistência de votos naquele ano ou em outras fontes oficiais. Porém, a sondagem ainda **não confirmou** a cobertura de votos individuais de 2006–2025. Antes de escolher esse caminho, verificar outras decisões nominais antigas e, se necessário, a fonte oficial histórica correspondente.

As despesas são uma opção complementar: a documentação oficial apresenta a série desde 2008, o que cobre dezoito anos civis completos até 2025, e não vinte. Não supor que a API possua 2006–2007 só porque aceita o parâmetro de ano.

## Possibilidades e o que o usuário veria no site

| Possibilidade | Dados necessários | Pergunta de pesquisa possível | Interação no site | Situação de viabilidade |
| --- | --- | --- | --- | --- |
| **Coautoria de proposições** | Proposições, autores, identificação do deputado e data de apresentação | Como a colaboração formal entre deputados e partidos mudou ao longo do período? | Escolher ano/legislatura; explorar a rede; clicar numa ligação para ver as proposições assinadas em conjunto | Coautoria observada nas pequenas amostras de 2016 e 2021. Proposições e autores também retornaram nos anos antigos. Caminho promissor a verificar nos demais anos |
| **Relação entre atuação e temas** | Ementa, temas oficiais, autores e datas | Como os temas associados à produção legislativa variam entre períodos e grupos de autores? | Selecionar tema ou deputado; ver séries temporais, rede deputado–tema e propostas que sustentam cada conexão | Temas e autores encontrados nos cinco momentos. Comparabilidade das categorias e cobertura ainda precisam ser medidas |
| **Afinidade de votos e comunidades** | Votos por deputado e decisão, datas, partido observado no voto | Como as afinidades e as comunidades de votação mudam entre períodos? | Filtros por período, deputado e partido; selecionar um par e abrir os votos comuns e a taxa de concordância | Maior reaproveitamento do código atual. Cobertura nominal antiga ainda não confirmada; manter como opção condicionada |
| **Adesão às orientações** | Votos, orientações e composição histórica de blocos/federações | Como varia a adesão às orientações ao longo dos anos? | Escolher bancada e período; ver concordância e quais decisões entram no cálculo | Exige resolver os vínculos históricos; o piloto de 2023 só associou diretamente 15,8% dos votos Sim/Não |
| **Percursos das proposições** | Datas, tipos e sequências de tramitação | Como se distribuem os percursos e tempos de tramitação por tema ou tipo de proposta? | Abrir uma linha do tempo; comparar trajetórias de propostas | Endpoint já examinado no piloto. Exige estudo de estados, mudanças de procedimento e proposições ainda em andamento |
| **Compartilhamento de fornecedores** | Despesas, fornecedor, deputado, data e tipo | Como se estruturam relações de contratação registradas na cota parlamentar? | Rede deputado–fornecedor e filtros de período/categoria | Complementar: série documentada desde 2008 e consultas do piloto vieram vazias. Ainda não é opção confirmada para vinte anos |

**Leitura de viabilidade:** coautoria e relação deputado–tema merecem prioridade na conversa por combinarem grafos, fontes retornadas nos cinco momentos e uma interação explicável ao público. Afinidades de voto continuam possíveis, mas dependem da confirmação dos dados mais antigos. Essa é uma priorização técnica, não a escolha definitiva do tema nem uma afirmação de novidade acadêmica.

## O site como resultado do estudo

Referência de experiência: [ElectoMaps — deputados](https://electomaps.com.br/apuracao-deputados?cargo=0006&uf=sp), em especial a navegação por recortes e a ligação entre visualização e informações detalhadas. A página consultada apresentou estado/partido e áreas de detalhamento; não foi feita uma reprodução visual nem presumida a implementação interna do serviço.

Escopo inicial proposto para o site:

1. **Escolher um período** entre os anos disponíveis e, quando fizer sentido, comparar dois períodos.
2. **Explorar um grafo** com zoom, movimento e seleção de nó ou ligação; complementar com tabela acessível.
3. **Buscar um deputado** e aplicar filtros de partido, UF e tema, quando esses campos forem adequados à análise escolhida.
4. **Entender a evidência:** ao selecionar uma conexão, abrir as proposições ou votos que a sustentam, a medida utilizada e seu denominador.
5. **Entender a cobertura:** informar período, quantidade de registros, critérios, limitações e data da extração. Uma lacuna deve aparecer como indisponibilidade, não como zero de atividade.
6. **Consultar metodologia e fonte oficial**, com endereço compartilhável para o recorte. Exportação pode ser acrescentada depois de estabilizar a primeira análise.

Os filtros são possibilidades: não assumir que toda análise precisa de todos eles. O primeiro site deve explicar **uma análise principal bem definida**, com contexto, evidência e navegação; outras análises podem ser adicionadas conforme a discussão acadêmica.

O produto é o site. A contribuição do TCC será a pergunta respondida, o método e sua avaliação: por exemplo, comparar a estabilidade de redes de colaboração ou explicar a evolução das relações entre autores e temas. Definir o site, sozinho, ainda não define a pergunta científica.

## Como preparar os dados sem sobrecarregar a API ou o navegador

**Exploração atual:** respostas pequenas da API e cache para repetir as verificações. A sondagem não calcula rankings, tendências ou comunidades dos vinte anos.

**Após escolher o tema:** coletar apenas os recursos necessários, em janelas de tempo pequenas, com paginação completa, retomada e registro de falhas. O endpoint de votações retornou HTTP 400 para uma consulta anual de teste, informando que a diferença entre datas não pode superar três meses. Usar janelas mensais é uma opção conservadora; testar os limites de cada recurso, não assumir que todas as rotas têm a mesma regra.

**Processamento:** produzir tabelas e grafos por período, com regras versionadas. A filiação deve refletir o período, e a identidade do deputado deve ser o ID. Para coautoria, distinguir assinatura/apoiamento, proponente e atores não parlamentares. Uma proposta com muitas assinaturas pode criar muitas ligações na projeção; avaliar pesos ou começar pela rede bipartida deputado–proposição.

**Site:** consultar resultados previamente preparados por período; carregar somente o recorte necessário. A API oficial fornece a origem dos dados e os vínculos de conferência. Os cálculos caros dos vinte anos ficam na preparação, para a interação do visitante não disparar milhares de chamadas.

Para grafos grandes, limitar o que é desenhado e explicar a regra visual. Arestas ocultadas por legibilidade não podem alterar silenciosamente as métricas calculadas. Números de comunidade não devem ser tratados como identidades permanentes entre períodos: uma comparação longitudinal exige alinhar e avaliar os grupos.

## Etapas revisadas, orientadas por metas

| Etapa | Resultado esperado |
| --- | --- |
| Levantar possibilidades | Documento e sondagem pequena, com requisitos históricos e de interação |
| Definir pergunta e escopo com o orientador | Uma pergunta principal, recursos, período de pelo menos vinte anos e critérios de avaliação |
| Confirmar cobertura e integrar dados | Lacunas documentadas e base necessária ao recorte escolhido |
| Executar análise histórica | Resultados por período e avaliação da comparabilidade e robustez |
| Desenvolver o site | Primeira análise navegável, evidência acessível e metodologia explicada |
| Validar e redigir | Conferência dos cálculos, avaliação da navegação e relatório final com o histórico da mudança |

Não reaplicar automaticamente as datas e os objetivos do cronograma LEN. Confirmar com o orientador quais entregas e prazos permanecem após a redefinição.

## Decisões úteis para a próxima conversa

- A contribuição principal será sobre colaboração formal, temas legislativos ou afinidades de voto?
- Os vinte anos precisam ser os mesmos para todas as análises, ou uma análise principal deve cobrir o período e outras podem ter séries menores?
- O recorte 2006–2025 é adequado? Qual janela fará sentido para a comparação: ano, semestre ou legislatura?
- A expectativa acadêmica inclui predição/IA, ou análise de redes e avaliação de visualização atendem ao objetivo?
- Quais interações são essenciais para explicar a análise a alguém que não conhece grafos?

## Reprodução e fontes

```bash
python DEPUTADOS/sondagem_historica.py
python DEPUTADOS/sondagem_historica.py --offline
```

O padrão inspeciona cinco anos de referência e faz no máximo 35 consultas na configuração atual; o cliente permite até cinquenta consultas novas para interromper expansões acidentais. Retentativas de transporte podem gerar tentativas HTTP adicionais. As primeiras páginas são parciais e isso fica registrado em `resultados_viabilidade/sondagem.json`.

- [API e arquivos oficiais — cobertura de proposições, autores e despesas](https://dadosabertos.camara.leg.br/swagger/api.html).
- [Conceitos e limitações dos dados de votações](https://dadosabertos.camara.leg.br/howtouse/2020-02-07-dados-votacoes.html).
- [Especificação OpenAPI](https://dadosabertos.camara.leg.br/api/v2/api-docs).
- Evidência empírica: `resultados_viabilidade/sondagem.json`, com resumos, campos observados, filtros e manifesto; respostas completas no cache local.

Presença de um campo em uma resposta não garante sua cobertura ou comparabilidade em todos os anos. Nenhuma alternativa demonstra influência causal, ideologia, corrupção ou qualidade do mandato por simples posição no grafo.

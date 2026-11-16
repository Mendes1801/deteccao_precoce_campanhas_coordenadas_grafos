# Roteiro da apresentação — N2

**Duração-alvo:** 4 min 45 s (máximo permitido: 5 min)

**Projeto:** Detecção precoce de campanhas coordenadas em redes sociais por meio da evolução de grafos temporais

O roteiro enumera os pontos que devem ser apresentados. Dividam as falas entre os integrantes e ensaiem com cronômetro para manter o vídeo dentro do limite.

## 1. Apresentação da equipe — 0:00 a 0:30

- Dizer o título do projeto.
- Apresentar os integrantes, incluindo nome completo e RA.
- Identificar o Prof. Dr. Leandro Zerbinatti, a disciplina Inteligência Artificial, o curso Sistemas de Informação, a turma 7ºK SI — Noite e a Universidade Presbiteriana Mackenzie — Faculdade de Computação e Informática.

## 2. Tema e problema — 0:30 a 1:05

- Explicar que o projeto investiga como identificar campanhas coordenadas em redes sociais antes de observar todas as interações.
- Descrever a dificuldade: os sinais iniciais são incompletos e podem se confundir com comportamento legítimo.
- Apresentar a pergunta do projeto: quanto da evolução de uma rede é necessário observar para avaliar se ela pertence à classe `campaign` ou `noncampaign`?

## 3. Uso de IA e fundamentos — 1:05 a 1:50

- Explicar que o problema foi formulado como classificação binária supervisionada de grafos.
- Apresentar os grafos direcionados e temporais: usuários são nós; interações são arestas com timestamps.
- Explicar que a proposta é extrair características estruturais e temporais de estados parciais e, em etapas futuras, comparar essas características com baselines de classificação.
- Deixar claro que ainda não foi treinado um classificador nem foram calculadas métricas de desempenho; o trabalho atual é a preparação experimental e a extração de características.

## 4. Solução e artefato — 1:50 a 3:15

- Apresentar o dataset **Large Engagement Networks (LEN)** e indicar sua fonte oficial.
- Explicar brevemente o fluxo implementado:
  1. leitura incremental dos arquivos JSON;
  2. ordenação das arestas por timestamp;
  3. construção de estados parciais de 10% a 100%, por tempo decorrido e por número de eventos observados;
  4. extração de características estruturais e temporais.
- Mostrar o notebook [02_eda_aprofundada_len.ipynb](../notebooks/02_eda_aprofundada_len.ipynb) e os módulos em [`src/len_eda/`](../src/len_eda/).
- Destacar um cuidado metodológico: atributos calculados sobre o grafo completo, como `kcore`, não devem ser usados nos estados parciais, pois podem revelar informação futura.
- Se os dados estiverem disponíveis no computador da gravação, demonstrar a tabela de estados parciais. Caso contrário, mostrar o código e o notebook sem afirmar que a execução ocorreu durante o vídeo.

## 5. Resultados obtidos e limitações — 3:15 a 4:00

- Informar os resultados da análise exploratória: 104 arquivos locais, 53 grafos de campanha e 51 de não campanha, com 212.231 nós e 289.975 arestas; todas as arestas inspecionadas tinham timestamp.
- Explicar que foi identificada uma duplicata exata: após excluí-la, restam 103 grafos únicos (52 campanhas e 51 não campanhas).
- Mencionar que a documentação do LEN-small descreve 100 grafos; a diferença de três ainda precisa ser esclarecida.
- Ressaltar que não há resultados de classificação ou métricas de teste. Portanto, ainda não se pode afirmar que a detecção precoce foi validada.

## 6. Ética, conclusão e GitHub — 4:00 a 4:45

- Reforçar que o rótulo do dataset não prova intenção ou má-fé e que um falso positivo pode prejudicar comportamentos legítimos.
- Dizer que a solução deve apoiar a análise humana, não determinar punições ou remoções automaticamente.
- Concluir que a etapa atual preparou e documentou o pipeline; os próximos passos são resolver a composição da amostra e avaliar baselines com divisão por grafo, análise de erros e métricas por fração temporal.
- Mostrar a página pública do [repositório GitHub](https://github.com/Mendes1801/deteccao_precoce_campanhas_coordenadas_grafos), apontando o relatório, os notebooks e o código.
- Encerrar dentro do limite de cinco minutos.

## Conferência antes de publicar

- [ ] Conferir nomes completos, RAs e e-mails dos integrantes.
- [ ] Confirmar que o vídeo tem no máximo cinco minutos e está público no YouTube de um integrante.
- [ ] Inserir no [relatório](Relatório%20do%20Projeto.md) o endereço público do vídeo.
- [ ] Confirmar que o repositório e os artefatos apresentados estão públicos e atualizados.
- [ ] Não apresentar métricas de modelos como resultados: elas ainda não foram obtidas.

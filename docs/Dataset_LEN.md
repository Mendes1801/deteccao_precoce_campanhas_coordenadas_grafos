# Dataset LEN-small

## Identificação e conteúdo

Este projeto utiliza o conjunto **Large Engagement Networks (LEN-small)**,
disponibilizado pelos autores de Gopalakrishnan et al. (2025). Os dados são
grafos direcionados de engajamento em redes sociais. Em cada arquivo:

- os nós representam usuários identificados por IDs técnicos;
- as arestas representam retuítes, respostas ou citações;
- cada aresta inclui `source`, `target`, `timestamp` e `Interaction_Count`;
- o nome do arquivo indica a classe `campaign` ou `noncampaign`;
- os vetores `node_attr` e `edge_attr` têm, respectivamente, 772 e 776 posições.

Na documentação oficial, o LEN-small possui 100 grafos, divididos em 51 campanhas
e 49 não campanhas. No pacote baixado neste workspace foram encontrados 104
arquivos JSON, com 53 campanhas e 51 não campanhas. Uma duplicata byte a byte
foi registrada na configuração `config/len_small_exclusions.csv`.

## Uso de dados e privacidade

Os arquivos brutos não são armazenados neste repositório. O motivo principal é o
tamanho do pacote LEN-small — aproximadamente 5,4 GB. Além disso, o repositório
adota somente os dados necessários à reprodução e não publica novos dados pessoais:
os identificadores originais são tratados como identificadores técnicos do dataset
e não são utilizados para tentativa de reidentificação.

Os resultados derivados versionados no projeto são tabelas agregadas e não
copiam os vetores completos de atributos dos grafos. Antes de redistribuir os
dados brutos, os usuários devem verificar a licença e os termos da fonte oficial.

## Origem oficial

- Página do projeto: https://erdemub.github.io/large-engagement-network/
- Página de downloads: https://erdemub.github.io/large-engagement-network/download_page.html
- Pacote pequeno: https://cse.buffalo.edu/~erdem/small_encoder_final.tar

Referência:

Gopalakrishnan, A. A.; Hossain, J.; Elmas, T.; Sariyuce, A. E. "Large
Engagement Networks for Classifying Coordinated Campaigns and Organic Twitter
Trends." Proceedings of the International AAAI Conference on Web and Social
Media, v. 19, n. 1, p. 688–702, 2025.

## Como obter e executar localmente

Na raiz do repositório:

```bash
curl -L --fail https://cse.buffalo.edu/~erdem/small_encoder_final.tar \
  -o small_encoder_final.tar

tar -xf small_encoder_final.tar

python -m pip install -e ".[dev,notebook]"

mkdir -p outputs
len-summary \
  --data-dir small_encoder_final \
  --output outputs/len_small_summary.csv

len-features \
  --data-dir small_encoder_final \
  --exclusions config/len_small_exclusions.csv \
  --output outputs/partial_graph_features.csv

len-evaluate \
  --features outputs/partial_graph_features.csv \
  --mode events \
  --output outputs/partial_graph_metrics_events.csv
```

O diretório `small_encoder_final/` permanece local e não deve ser enviado ao
GitHub. Os CSVs derivados em `outputs/` são pequenos o suficiente para serem
versionados e permitem verificar a reprodução dos resultados.

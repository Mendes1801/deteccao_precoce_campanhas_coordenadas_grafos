# Detecção precoce de campanhas coordenadas

TCC sobre detecção precoce de campanhas coordenadas em redes sociais por
meio da evolução de grafos temporais. A base experimental inicial é o
[Large Engagement Networks (LEN)](https://erdemub.github.io/large-engagement-network/).

O estado atual do ambiente, o que já foi executado e o fluxo recomendado para
os próximos notebooks estão em [docs/guia_ambiente_e_fluxo.md](docs/guia_ambiente_e_fluxo.md).

## Primeira configuração do ambiente

O ambiente desta etapa foi mantido propositalmente pequeno: leitura incremental
dos JSONs, análise tabular, visualização e NetworkX. Bibliotecas de GNN não entram
ainda, pois exigem uma escolha separada de versões de PyTorch e PyTorch Geometric.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,notebook]"
```

Para confirmar que o ambiente e o leitor funcionam:

```bash
pytest
len-summary --data-dir small_encoder_final --limit 5
```

Para gerar a tabela completa de atributos iniciais:

```bash
len-summary \
  --data-dir small_encoder_final \
  --output outputs/len_small_summary.csv
```

Depois, abra o notebook:

```bash
jupyter lab notebooks/01_eda_inicial_len.ipynb
```

## O que o resumo mede

O comando `len-summary` percorre os arquivos sem carregar os vetores de 772 e
776 dimensões inteiros na memória. Para cada grafo, ele registra:

- classe inferida do nome do arquivo;
- quantidade de nós e arestas;
- densidade, graus e reciprocidade;
- componentes fracamente conectados e fração do maior componente;
- cobertura, intervalo e duração dos timestamps;
- contagem de interações e problemas básicos de integridade.

Alguns arquivos usam a constante não padronizada `NaN`. Durante a leitura, o
comando a converte para `null` no fluxo de dados, sem alterar o dataset original.

Use `--limit N` durante testes rápidos. Sem esse argumento, todos os arquivos
JSON da pasta são processados.

## Cuidados metodológicos já identificados

1. O LEN mantém somente a interação mais recente de cada par ordenado de
   usuários. O artigo informa que isso preserva aproximadamente 74% das arestas.
   Portanto, a evolução reconstruída é a evolução das arestas retidas, não o
   fluxo original completo de eventos.
2. O atributo `kcore` foi calculado sobre o grafo completo e não deve entrar em
   estados parciais. Ele carregaria informação do futuro.
3. Os grandes vetores `node_attr` e `edge_attr` são ignorados nesta primeira
   inspeção. A origem temporal de cada componente deve ser documentada antes de
   usá-los em detecção precoce.
4. A divisão entre treino, validação e teste deve ocorrer por campanha antes da
   geração das janelas temporais.
5. O pacote local possui 104 arquivos, enquanto o artigo descreve 100 grafos no
   LEN-small. Há pelo menos um par de arquivos byte a byte idêntico; essa
   divergência precisa ser resolvida antes de congelar a amostra experimental.

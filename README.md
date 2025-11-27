# Projeto de Grafos — Grupo 6  

## Equipe
- Felipe França  
- Felipe Matias  
- Lucas Ferreira Torres  
- Luis Gustavo Melo  

## Estrutura de Arquivos

```
projeto-grafos/
├─ README.md
├─ requirements.txt
├─ data/
│  ├─ bairros_recife.csv
│  ├─ adjacencias_bairros.csv
│  ├─ enderecos.csv
│  └─ dataset_parte2/
│     ├─ airlineFlightRoutes.csv
│     └─ csvFiltrado.csv
├─ out/
│  └─ .gitkeep
├─ src/
│  ├─ cli.py               # Interface de Linha de Comando
│  ├─ solve.py             # Geração dos arquivos .csv ou .json
│  ├─ graphs/
│  │  ├─ io.py             # Processamento do dataset original (Parte 1)
│  │  ├─ graph.py          # Criação da lista de adjacência
│  │  └─ algorithms.py     # Dijkstra, Bellman-Ford, DFS, BFS
│  └─ viz.py               # Geração dos arquivos .png e .html de visualização
├─ tests/
│  ├─ test_bfs.py
│  ├─ test_dfs.py
│  ├─ test_dijkstra.py
│  └─ test_bellman_ford.py
```

## Como Executar

### 1. Criar o ambiente virtual
`py -m venv venv`

### 2. Ativar o ambiente virtual
Windows:
`.\venv\Scripts\activate`

### 3. Instalar os requisitos
`pip install -r requirements.txt`

### 4. Gerar todos os arquivos dentro de /out
Execute na raiz do projeto:
`python -m src.cli out`

Ou, se preferir, execute esses arquivos manualmente para obter o mesmo resultado:

`python src/solve.py`  
`python src/viz.py`

import json
import os
from graphs.graph import carregar_lista_adjacencia
from graphs.io import carregar_lista_adjacencia_parte2
from graphs.algorithms import dijkstra_path, bfs, dfs, bellman_ford
import pandas as pd
import time
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

caminho_out_folder = os.path.join(BASE_DIR, "../out/")
caminho_graus = os.path.join(BASE_DIR, "../out/graus.csv")

caminho_bairro_maior_grau = os.path.join(BASE_DIR, "../out/bairro_maior_grau.json")

caminho_bairros_unique = os.path.join(BASE_DIR, "../data/bairros_unique.csv")
caminho_recife_global = os.path.join(BASE_DIR, "../out/recife_global.json")
caminho_microrregioes = os.path.join(BASE_DIR, "../out/microrregioes.json")
ego_bairro_csv = os.path.join(BASE_DIR, "../out/ego_bairro.csv")

caminho_enderecos_csv = os.path.join(BASE_DIR, "../data/enderecos.csv")
distancias_enderecos_csv = os.path.join(BASE_DIR, "../out/distancias_enderecos.csv")
percurso_nova_descoberta_setubal = os.path.join(BASE_DIR, "../out/percurso_nova_descoberta_setubal.json")

# parte 2 - caminhos aereos
caminho_out = os.path.join(BASE_DIR, "../out/parte2_metrics.json")
caminho_csvFiltrado = os.path.join(BASE_DIR, "../data/dataset_parte2/csvFiltrado.csv")

caminho_out_bfsdfs = os.path.join(BASE_DIR, "../out/bfs_dfs_resultados.json")
caminho_out_dijkstra = os.path.join(BASE_DIR, "../out/dijkstra_resultados.json")
caminho_out_bellman = os.path.join(BASE_DIR, "../out/bellman_ford_resultados.json")

#####################################
## PARTE 1
#####################################

def gerar_csv_graus(lista_adjacencia = carregar_lista_adjacencia()):
    graus = {}
    graus_values = []

    resultado = []

    for bairro, vizinhos in lista_adjacencia.items():
        grau = len(vizinhos)
        graus[bairro] = grau
        graus_values.append(grau)

        resultado.append({
            "bairro": bairro,   
            "grau": grau
        })

    if not os.path.exists(caminho_out_folder):
        os.makedirs(caminho_out_folder)

    with open(caminho_graus, "w", encoding="utf-8") as f:
        pd.DataFrame(resultado).to_csv(f, index=False)

# Retorna e escreve um json com o bairro com maior grau
def obter_bairro_com_maior_grau():
    df = pd.read_csv(caminho_graus)

    df = df.sort_values('grau', ascending=False)

    alvo = df.iloc[0]

    alvo_json = {
        "bairro": alvo['bairro'],
        "grau": int(alvo['grau']) 
    }

    with open(caminho_bairro_maior_grau, "w", encoding="utf-8") as f:
        json.dump(alvo_json, f, indent=4, ensure_ascii=False)

def metricas_globais(lista_adjacencia = carregar_lista_adjacencia(), write=True):
    # Ordem (nº de vértices)
    V = len(lista_adjacencia)

    # Tamanho (nº de arestas)
    # somatório dos graus / 2 pois o grafo é não-direcionado
    E = sum(len(vizinhos) for vizinhos in lista_adjacencia.values()) // 2

    # Densidade
    if V < 2:
        densidade = 0
    else:
        densidade = (2 * E) / (V * (V - 1))

    metricas_globais_json = {
        "ordem": V,
        "tamanho": E,
        "densidade": f"{densidade:.2f}"
    }

    if(write):
        if not os.path.exists(caminho_out_folder):
            os.makedirs(caminho_out_folder)

        with open(caminho_recife_global, "w", encoding="utf-8") as f:
            json.dump(metricas_globais_json, f, indent=4, ensure_ascii=False)

            f.close()

    return metricas_globais_json

# Retorna um subgrafo filtrado apenas com bairros daquela microrregião e suas arestas internas.
def obter_subgrafo_por_microrregiao(lista_adjacencia, df, microrregiao):
    # Filtra os bairros que pertencem à microrregião desejada
    bairros = set(df.loc[df["microrregiao"] == microrregiao, "bairro"])


    subgrafo = {}

    # Percorre os bairros da microrregião e adiciona suas arestas internas ao subgrafo
    for bairro in bairros:
        if bairro not in lista_adjacencia:
            continue
        
        vizinhos_filtrados = [(vertice, peso) for vertice, peso in lista_adjacencia[bairro] if vertice in bairros]

        if vizinhos_filtrados:
            subgrafo[bairro] = vizinhos_filtrados

    return subgrafo

# Calcula as métricas globais para cada microrregião e salva em um JSON
def metricas_globais_microrregioes(lista_adjacencia = carregar_lista_adjacencia()):
    df = pd.read_csv(caminho_bairros_unique)

    resultados = {}

    # lista única de microrregioes
    microrregioes = df["microrregiao"].unique()
    # Para cada microregião, obtém o subgrafo e calcula as métricas globais do subgrafo
    for micro in microrregioes:
        subgrafo = obter_subgrafo_por_microrregiao(lista_adjacencia, df, micro)
        metricas = metricas_globais(subgrafo, False)
        
        resultados[micro] = metricas

    # salva o JSON
    with open(caminho_microrregioes, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    return resultados

# Calcula as métricas de ego network para cada bairro
def ego_network_metricas(lista_adjacencia = carregar_lista_adjacencia()):
    results = []

    for bairro in lista_adjacencia.keys():

        vizinhos = []
        
        # coleta vizinhos do bairro
        for item in lista_adjacencia[bairro]:
            if isinstance(item, tuple):
                vizinhos.append(item[0])
            else:
                vizinhos.append(item)

        # calcula grau do bairro
        grau = len(vizinhos)

        ego_vertices = set([bairro] + vizinhos)

        ego_arestas = set()

        # percorre os vértices da ego network
        for u in ego_vertices:

            # vizinhos de u
            for item in lista_adjacencia[u]:
                v = item[0] if isinstance(item, tuple) else item

                # armazena aresta se v também está na ego
                if v in ego_vertices:

                    ego_arestas.add((u, v))

        tamanho_ego = len(ego_arestas)

        ordem_ego = len(ego_vertices)

        # calcula densidade da ego network
        if ordem_ego > 1:
            densidade_ego = tamanho_ego / (ordem_ego * (ordem_ego - 1) / 2)
        else:
            densidade_ego = 0

        results.append({
            "bairro": bairro,
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": f"{densidade_ego:.2f}"
        })

    df = pd.DataFrame(results)
    df.to_csv(ego_bairro_csv, index=False)
    return df

# Converte um deque em string no formato "A -> B -> C"
def deque_to_string(deque_obj):
    list_obj = list(deque_obj)

    result = ""
    
    for i in list_obj:
        result += str(i)
        if i != list_obj[-1]:
            result += " -> "

    return result

# Calcula o peso do caminho entre os endereços listados no CSV
def calcular_peso_caminho_enderecos(lista_adjacencia = carregar_lista_adjacencia()):
    df_enderecos = pd.read_csv(caminho_enderecos_csv)

    resultado = []

    # Para cada par de endereços, calcula o peso do caminho entre os bairros correspondentes
    for _, row in df_enderecos.iterrows():
        endereco_X = row["X"]
        endereco_Y = row["Y"]
        bairro_X = row["bairro_X"].strip().lower()
        bairro_Y = row["bairro_Y"].strip().lower()

        # Calcula o peso do caminho entre os bairros usando Dijkstra
        peso, caminho = dijkstra_path(lista_adjacencia, bairro_X, bairro_Y)

        # Se o par de bairros for "nova descoberta" e "setubal", salva o percurso em um JSON separado
        if bairro_X == "nova descoberta" and bairro_Y == "setubal":
            with open(percurso_nova_descoberta_setubal, "w", encoding="utf-8") as f:
                json.dump({
                    "caminho": deque_to_string(caminho)
                }, f, indent=4, ensure_ascii=False)

        resultado.append({
            "X": endereco_X,
            "Y": endereco_Y,
            "bairro_X": bairro_X,
            "bairro_Y": bairro_Y,
            "custo": peso,
            "caminho": deque_to_string(caminho)
        })

    with open(distancias_enderecos_csv, "w", encoding="utf-8") as f:
        pd.DataFrame(resultado).to_csv(f, index=False)


#####################################
## PARTE 2
#####################################

# Função para calcular as métricas do grafo direcionado e ponderado da parte 2
def calcular_metricas_parte2(lista_adj = carregar_lista_adjacencia_parte2(caminho_csvFiltrado)):
    
    #---------------
    # Ordem (nº de vértices)
    #---------------

    # set para evitar duplicatas
    # já coloca todos os vértices que aparecem como origem
    vertices = set(lista_adj.keys())
    for origem, vizinhos in lista_adj.items():
        # percorre os vizinhos do vértice origem
        for destino, _ in vizinhos:
            vertices.add(destino)
    
    # adquire o número de vértices únicos
    V = len(vertices)

    #---------------
    # Tamanho (nº de arestas)
    #---------------

    # Arestas são contadas somando todos os vértices adjacentes da lista de adjacencia 
    E = sum(len(vizinhos) for vizinhos in lista_adj.values()) 

    #---------------
    # Graus (in e out)
    #---------------

    # inicializa dicionários de grau
    out_degree = {v: 0 for v in vertices}
    in_degree = {v: 0 for v in vertices}

    # percorre a lista de adjacência para calcular os graus
    for origem, vizinhos in lista_adj.items():
        # grau de saída é o número de vizinhos
        out_degree[origem] += len(vizinhos)
        # percorre os vizinhos para incrementar o grau de entrada
        for destino, _ in vizinhos:
            # grau de entrada é incrementado para cada ligação que chega ao destino
            in_degree[destino] += 1

    #---------------
    # Estatísticas da distribuição 
    #---------------

    maior_out = max(out_degree.items(), key=lambda x: x[1])
    maior_in  = max(in_degree.items(),  key=lambda x: x[1])

    resultado = {
        "num_vertices": V,
        "num_arestas": E,
        "tipo": {
            "dirigido": True,
            "ponderado": True
        },
        "graus": {
            "out_degree": out_degree,
            "in_degree": in_degree,
            "maior_out_degree": {
                "vertice": maior_out[0],
                "valor": maior_out[1]
            },
            "maior_in_degree": {
                "vertice": maior_in[0],
                "valor": maior_in[1]
            }
        }
    }

    # Salva arquivo
    with open(caminho_out, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

    return resultado

# função pra salvar o json
def salvar_bfs_dfs_json(resultado):
    with open(caminho_out_bfsdfs, "w", encoding="utf-8") as f:  
        json.dump(resultado, f, indent=4, ensure_ascii=False)

# função pra pegar os resultados do bfs e dfs
def getResultadosBfsDfs(lista_adj):
    fontes = ["abq", "acy", "cos"]

    resultados = {
        "bfs": {},
        "dfs": {}
    }

    for f in fontes: 
        resultados["bfs"][f] = bfs(lista_adj, f)
        resultados["dfs"][f] = dfs(lista_adj, f)

    return resultados

# função para salvar o json
def salvar_dijkstra_json(resultado):
    with open(caminho_out_dijkstra, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

# função para pegar os resultados de dijkstra 
def getResultadosDijkstra(lista_adj):
    pares = [
        ("dfw", "mia"),
        ("lax", "ord"),
        ("bos", "sea"),
        ("phx", "den"),
        ("atl", "iah")
    ]

    resultados = {}

    for origem, destino in pares:
        custo, caminho = dijkstra_path(lista_adj, origem, destino)

        if caminho == -1:
            caminho_str = "inexistente"
            custo = "-"
        else:
            caminho_str = " -> ".join(list(caminho))
            
        resultados[f"{origem}_para_{destino}"] = {
            "origem": origem,
            "destino": destino,
            "custo": custo,
            "caminho": caminho_str
        }

    salvar_dijkstra_json(resultados)
    return resultados

# Função para salvar o json
def salvar_bellman_json(resultado):
    with open(caminho_out_bellman, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

# Função para pegar os resultados do Bellman-Ford
def getResultadosBellmanFord():
    
    resultados = {}

    # Caso 1: Sem ciclo negativo
    vertices1 = ["dfw","mia","ord"] 

    arestas1 = [
        ("dfw", "mia", 120),
        ("mia", "ord", -20),
        ("dfw", "ord", 50)
    ]

    bf1 = bellman_ford(vertices1, arestas1, "dfw")

    resultados["caso1_sem_ciclo_negativo"] = {
        "vertices": vertices1,
        "arestas": arestas1,
        "origem": "dfw",
        "resultados": bf1
    }

    # Caso 2: Com ciclo negativo
    vertices2 = ["lax", "phx", "sea"]
    arestas2 = [
        ("lax", "phx", 3),
        ("phx", "sea", -10),
        ("sea", "lax", 2)
    ]
    bf2 = bellman_ford(vertices2, arestas2, "lax")

    if bf2 == -1:
        print("Ciclo negativo detectado!")
    else:
        print("Distâncias:", bf2)

    resultados["caso2_com_ciclo_negativo"] = {
        "vertices": vertices2,
        "arestas": arestas2,
        "origem": "lax",
        "resultados": bf2
    }

    salvar_bellman_json(resultados)
    
    return resultados

def executar_metrica_desempenho(lista_adj):
    #---------------
    # Função que executa os algortimos medindo o tempo e gerando o parte2_report.json
    #---------------

    report = {
        "dataset": "Dataset Parte 2",
        "resultados": []
    }
    
    vertices = list(lista_adj.keys())
    
    # Escolhemos uma amostragem de 3 fontes para o BFS/DFS/Bellman Ford
    fontes_algoritmos = vertices[:3] if len(vertices) >= 3 else vertices

    # Escolhemos uma amostragem de 5 fontes para o Dijkstra
    pares_dijkstra = [
        ("dfw", "mia"),
        ("lax", "ord"),
        ("bos", "sea"),
        ("phx", "den"),
        ("atl", "iah")
    ]

    print("\nIniciando Comparação de Desempenho dos Algoritmos\n ")

    # 1. Medindo BFS 
    print(f"Rodando BFS com {len(fontes_algoritmos)} fontes.")
    for fonte in fontes_algoritmos:
        inicio = time.perf_counter()
        aux = bfs(lista_adj, fonte)
        fim = time.perf_counter()
        
        report["resultados"].append({
            "algoritmo": "BFS",
            "origem": fonte,
            "tempo_execucao": f"{fim - inicio:.6f}",
            "tamanho": len(aux)
        })

    # 2. Medindo DFS 
    print(f"Rodando DFS com {len(fontes_algoritmos)} fontes.")
    for fonte in fontes_algoritmos:
        inicio = time.perf_counter()
        aux = dfs(lista_adj, fonte)
        fim = time.perf_counter()
        
        report["resultados"].append({
            "algoritmo": "DFS",
            "origem": fonte,
            "tempo_execucao": f"{fim - inicio:.6f}",
            "tamanho": len(aux)
        })

    # 3. Medindo Dijkstra
    for origem, destino in pares_dijkstra:
        if origem in lista_adj and destino in vertices: 
            inicio = time.perf_counter()
            aux = dijkstra_path(lista_adj, origem, destino) 
            fim = time.perf_counter()
            
            # Dijkstra vai retornar (custo, caminho) ou infinito se nao houver caminhos
            custo = aux[0] if isinstance(aux, tuple) else aux
            
            report["resultados"].append({
                "algoritmo": "Dijkstra",
                "origem": origem,
                "destino": destino,
                "tempo_execucao": f"{fim - inicio:.6f}s",
                "custo_total": custo
            })


    # 4. Medindo Bellman-Ford 
    
    # Convertendo as listas para um formato que o algoritmo aceite
    lista_vertices_bf = list(lista_adj.keys())
    lista_arestas_bf = []
    for i, vizinhos in lista_adj.items():
        for j, peso in vizinhos:
            lista_arestas_bf.append((i, j, peso))
            
    # 4.1 Bellman-Ford com o dataset
    print(f"Rodando Bellman-Ford com {len(fontes_algoritmos)} fontes.")
    for fonte in fontes_algoritmos:
        inicio = time.perf_counter()
        # Passamos as listas convertidas
        aux_bf = bellman_ford(lista_vertices_bf, lista_arestas_bf, fonte)
        fim = time.perf_counter()
        
        # So para validar se voltou certo com o dicionario
        status = "OK" if isinstance(aux_bf, dict) else "Erro/Ciclo"
        
        report["resultados"].append({
            "algoritmo": "Bellman-Ford",
            "caso": "Dataset Real",
            "origem": fonte,
            "tempo_execucao": f"{fim - inicio:.6f}s",
            "status_validacao": status
        })
    print("Rodando Bellman-Ford com os casos de controle.")
    
    # Caso 1: Peso Negativo sem ciclo negativo 
    v_bf1 = ["dfw", "mia", "ord"]
    e_bf1 = [
        ("dfw", "mia", 120),
        ("mia", "ord", -20),
        ("dfw", "ord", 50)
    ]
    # DFW -> MIA (120) -> ORD (-20) = 100
    # DFW -> ORD (50)
    # Menor caminho é 50.
    
    inicio = time.perf_counter()
    aux_bf1 = bellman_ford(v_bf1, e_bf1, "dfw")
    fim = time.perf_counter()
    
    # Verificando se calculou (retornou dict) e se o valor pra 'ord' esta correto (50)
    correto = "FALHA"
    if isinstance(aux_bf1, dict) and aux_bf1.get("ord") == 50:
        correto = "OK"

    report["resultados"].append({
        "algoritmo": "Bellman-Ford",
        "caso": "Peso Negativo (Sem Ciclo)",
        "tempo_execucao": f"{fim - inicio:.6f}",
        "status_validacao": correto
    })

    #  Caso 2: Ciclo Negativo detectado 
    v_bf2 = ["lax", "phx", "sea"]
    e_bf2 = [
        ("lax", "phx", 3),
        ("phx", "sea", -10),
        ("sea", "lax", 2)
    ] 
    # Ciclo: 3 - 10 + 2 = -5
    
    inicio = time.perf_counter()
    aux_bf2 = bellman_ford(v_bf2, e_bf2, "lax")
    fim = time.perf_counter()
    
    # Deve retornar -1 indicando ciclo negativo
    report["resultados"].append({
        "algoritmo": "Bellman-Ford",
        "caso": "Ciclo Negativo",
        "tempo_execucao": f"{fim - inicio:.6f}",
        "status_validacao": "OK" if aux_bf2 == -1 else "FALHA"
    })

    # Salvar JSON final
    caminho_report = os.path.join(BASE_DIR, "../out/parte2_report.json")
    with open(caminho_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"Relatório de desempenho salvo em: {caminho_report}")

def main_solve():
    metricas_globais()
    metricas_globais_microrregioes()
    ego_network_metricas()
    calcular_peso_caminho_enderecos()
    gerar_csv_graus()
    obter_bairro_com_maior_grau()

    lista_adj = carregar_lista_adjacencia_parte2(caminho_csvFiltrado)

    resultados_bfsdfs = getResultadosBfsDfs(lista_adj)
    salvar_bfs_dfs_json(resultados_bfsdfs)

    resultados_dijkstra = getResultadosDijkstra(lista_adj)
    salvar_dijkstra_json(resultados_dijkstra)

    resultados_bellman = getResultadosBellmanFord()
    salvar_bellman_json(resultados_bellman)


    executar_metrica_desempenho(lista_adj)

    calcular_metricas_parte2(lista_adj)

if __name__ == "__main__":
    main_solve()
    

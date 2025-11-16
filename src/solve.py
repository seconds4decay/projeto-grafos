import json
import os
from graphs.graph import carregar_lista_adjacencia
from graphs.io import carregar_lista_adjacencia_parte2
from graphs.algorithms import dijkstra_path
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

caminho_graus = os.path.join(BASE_DIR, "../out/graus.csv")

caminho_bairros_unique = os.path.join(BASE_DIR, "../data/bairros_unique.csv")
caminho_recife_global = os.path.join(BASE_DIR, "../out/recife_global.json")
caminho_microrregioes = os.path.join(BASE_DIR, "../out/microrregioes.json")
ego_bairro_csv = os.path.join(BASE_DIR, "../out/ego_bairro.csv")

caminho_enderecos_csv = os.path.join(BASE_DIR, "../data/enderecos.csv")
distancias_enderecos_csv = os.path.join(BASE_DIR, "../out/distancias_enderecos.csv")
percurso_nova_descoberta_setubal = os.path.join(BASE_DIR, "../out/percurso_nova_descoberta_setubal.json")

# parte 2 - caminhos aereos
caminho_out = os.path.join(BASE_DIR, "../out/parte2_metrics.json")
caminho_csvFiltrado = ("../data/dataset_parte2/csvFiltrado.csv")

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

    with open(caminho_graus, "w", encoding="utf-8") as f:
        pd.DataFrame(resultado).to_csv(f, index=False)
   

def metricas_globais(lista_adjacencia = carregar_lista_adjacencia()):
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
        metricas = metricas_globais(subgrafo)
        
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

def calcular_metricas_parte2(lista_adj = carregar_lista_adjacencia_parte2(caminho_csvFiltrado)):
    
    #---------------
    # Ordem (nº de vértices)
    #---------------

    # set para evitar duplicatas
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



if __name__ == "__main__":
    #metricas_globais()
    #metricas_globais_microrregioes()
    #ego_network_metricas()
    #calcular_peso_caminho_enderecos()
    #gerar_csv_graus()

    resultado_parte2 = calcular_metricas_parte2()
    print(json.dumps(resultado_parte2, indent=4, ensure_ascii=False))
    
    



    

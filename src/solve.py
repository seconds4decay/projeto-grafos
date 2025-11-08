import json
import os
from graphs.graph import carregar_lista_adjacencia
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_csv = os.path.join(BASE_DIR, "../data/adjacencias_bairros.csv")
caminho_bairros_unique = os.path.join(BASE_DIR, "../data/bairros_unique.csv")
caminho_recife_global = os.path.join(BASE_DIR, "../out/recife_global.json")
caminho_microrregioes = os.path.join(BASE_DIR, "../out/microrregioes.json")
ego_bairro_csv = os.path.join(BASE_DIR, "../out/ego_bairro.csv")

def metricas_globais(lista_adjacencia):
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

def metricas_globais_microrregioes(lista_adjacencia):
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

def ego_network_metrics(lista_adjacencia):    
    results = []

    for bairro in lista_adjacencia.keys():

        vizinhos = []

        for item in lista_adjacencia[bairro]:
            if isinstance(item, tuple):
                vizinhos.append(item[0])
            else:
                vizinhos.append(item)

        grau = len(vizinhos)

        ego_vertices = set([bairro] + vizinhos)

        ego_arestas = set()

        for u in ego_vertices:
            if u not in lista_adjacencia:
                continue

            # vizinhos de u
            for item in lista_adjacencia[u]:
                v = item[0] if isinstance(item, tuple) else item

                # armazena aresta se v também está na ego
                if v in ego_vertices:

                    # como o grafo é não orientado, ordenamos a tupla
                    aresta = tuple(sorted([u, v]))
                    ego_arestas.add(aresta)

        tamanho_ego = len(ego_arestas)

        ordem_ego = len(ego_vertices)


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



if __name__ == "__main__":
    lista_adjacencia = carregar_lista_adjacencia(caminho_csv)

    resultado_global = metricas_globais(lista_adjacencia)

    #print("Métricas globais do grafo:")
    #print(resultado_global)

    resultado_metricas_microrregioes = metricas_globais_microrregioes(lista_adjacencia)

    print("Métricas por microrregião:")
    print(resultado_metricas_microrregioes)

    ego_network_metrics(lista_adjacencia)
    
    



    

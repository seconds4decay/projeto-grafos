from pyvis.network import Network
import json, os, pandas as pd
from graphs.graph import carregar_lista_adjacencia

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_json = os.path.join(BASE_DIR, "../out/percurso_nova_descoberta_setubal.json")
arvore_percurso_html = os.path.join(BASE_DIR, "../out/arvore_percurso.html")
mapa_cores_graus_html = os.path.join(BASE_DIR, "../out/mapa_cores_graus.html")

caminho_graus_csv = os.path.join(BASE_DIR, "../out/graus.csv")


def string_to_list(string):
    return string.strip().split(" -> ")

def plot_percurso_nova_descoberta_setubal():
    with open(caminho_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    caminho = string_to_list(data["caminho"])

    net = Network(height="750px", width="100%", notebook=False)

    # Adiciona os nós e arestas ao grafo
    for i in range(len(caminho) - 1):
        net.add_node(caminho[i], label=caminho[i])
        net.add_node(caminho[i + 1], label=caminho[i + 1])
        net.add_edge(caminho[i], caminho[i + 1])

    # Gera o arquivo HTML
    net.write_html(arvore_percurso_html)

def mapa_de_cores_por_grau(lista_adjacencia, graus):
    net = Network(height="750px", width="100%", notebook=False)

    min_grau = graus["grau"].min()
    max_grau = graus["grau"].max()

    print(min_grau, max_grau)

    bairros = lista_adjacencia.keys()

    for bairro in bairros:
        grau = graus.loc[graus["bairro"] == bairro, "grau"].values[0]

        # Quanto maior o grau, mais verde; quanto menor, mais vermelho
        intensidade_cor = int(255 * (grau - min_grau) / (max_grau - min_grau)) if max_grau > min_grau else 0
        cor = f"rgb({255 - intensidade_cor}, {intensidade_cor}, 0)"

        net.add_node(bairro, label=bairro, color=cor)

    for origem, vizinhos in lista_adjacencia.items():
        for destino, peso in vizinhos:
            if net.get_node(destino):
                net.add_edge(origem, destino, value=peso)

    net.write_html(mapa_cores_graus_html)

if __name__ == "__main__":
    mapa_de_cores_por_grau(carregar_lista_adjacencia(), pd.read_csv(caminho_graus_csv))  
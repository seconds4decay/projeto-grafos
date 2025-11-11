import json
import os
import pandas as pd
import matplotlib.pyplot as plt

from graphs.graph import carregar_lista_adjacencia
from graphs.algorithms import dijkstra_path

from pyvis.network import Network
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_json = os.path.join(BASE_DIR, "../out/percurso_nova_descoberta_setubal.json")
arvore_percurso_html = os.path.join(BASE_DIR, "../out/arvore_percurso.html")
mapa_cores_graus_html = os.path.join(BASE_DIR, "../out/mapa_cores_graus.html")
ego_bairros_csv = os.path.join(BASE_DIR, "../out/ego_bairro.csv")
bairros_microrregiao_csv = os.path.join(BASE_DIR, "../data/bairros_unique.csv")

caminho_graus_csv = os.path.join(BASE_DIR, "../out/graus.csv")


def string_to_list(string):
    return string.strip().split(" -> ")

# Função para plotar o percurso da nova descoberta em Setúbal
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

# Função para criar um mapa de cores baseado no grau dos bairros
def mapa_de_cores_por_grau(lista_adjacencia = carregar_lista_adjacencia(), graus = pd.read_csv(caminho_graus_csv)):
    net = Network(height="750px", width="100%", notebook=False)

    min_grau = graus["grau"].min()
    max_grau = graus["grau"].max()

    bairros = lista_adjacencia.keys()

    for bairro in bairros:
        grau = graus.loc[graus["bairro"] == bairro, "grau"].values[0]

        # Quanto maior o grau, mais verde; quanto menor, mais vermelho
        intensidade_cor = int(255 * (grau - min_grau) / (max_grau - min_grau)) if max_grau > min_grau else 0
        cor = f"rgb({255 - intensidade_cor}, 255, 255)"

        net.add_node(bairro, label=bairro, color=cor)

    for origem, vizinhos in lista_adjacencia.items():
        for destino, peso in vizinhos:
            if net.get_node(destino):
                net.add_edge(origem, destino, value=peso)

    net.write_html(mapa_cores_graus_html)

# Função para gerar um gráfico de ranking de microrregiões por densidade ego
def ranking_densidade_ego_por_microrregiao(df_ego_bairro = pd.read_csv(ego_bairros_csv), bairros_microrregiao_csv = bairros_microrregiao_csv):
    bairros_microrregiao = pd.read_csv(bairros_microrregiao_csv)

    # Remover espaços em branco dos nomes dos bairros e microrregiões
    bairros_microrregiao["microrregiao"] = (
        bairros_microrregiao["microrregiao"]
        .astype(str)
        .str.strip()
    )

    # Merge nos dataframes para associar bairros às microrregiões
    df_merged = pd.merge(df_ego_bairro, bairros_microrregiao, on="bairro")
    df_grouped = df_merged.groupby("microrregiao")["densidade_ego"].mean().reset_index()
    df_sorted = df_grouped.sort_values(by="densidade_ego", ascending=False)

    # Plota o gráfico de barras horizontais das microrregiões com maior densidade ego
    plt.figure(figsize=(10, 6))
    plt.barh(df_sorted["microrregiao"], df_sorted["densidade_ego"], 
             color='skyblue', edgecolor='black', height=0.5)

    # adicionar valores ao lado das barras
    for i, v in enumerate(df_sorted["densidade_ego"]):
        plt.text(v + 0.005, i, f"{v:.3f}", va='center')

    plt.xlabel("Densidade Ego Média")
    plt.title("Top 10 Microrregiões por Densidade Ego")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, "../out/ranking_densidade_ego_por_microrregiao.png"))
    plt.close()

def histograma_graus(lista_graus = pd.read_csv(caminho_graus_csv)):
    # Histograma
    plt.hist(lista_graus["grau"])
    plt.xlabel("Grau")
    plt.ylabel("Frequência")
    plt.title("Distribuição dos Graus")
    plt.savefig(os.path.join(BASE_DIR, "../out/histograma_graus.png"))
    plt.close()

# Função principal para visualizar o grafo interativo
def visualizar_grafo(
    lista_adjacencia = carregar_lista_adjacencia(),
    graus = pd.read_csv(caminho_graus_csv),
    ego_df = pd.read_csv(ego_bairros_csv),
    micro_df = pd.read_csv(bairros_microrregiao_csv),

    output_html="out/grafo_interativo.html",
):
    net = Network(height="850px", width="100%", notebook=False, directed=False)
    net.force_atlas_2based()

    # Normalização de cores
    min_grau = graus["grau"].min()
    max_grau = graus["grau"].max()

    # Dicionários auxiliares
    densidades = dict(zip(ego_df["bairro"], ego_df["densidade_ego"]))
    microrregioes = dict(zip(micro_df["bairro"], micro_df["microrregiao"]))

    # adiciona nós
    for bairro in lista_adjacencia.keys():
        grau = graus.loc[graus["bairro"] == bairro, "grau"].values[0]
        dens = densidades.get(bairro, "N/A")
        micro = microrregioes.get(bairro, "N/A")

        intensidade_cor = int(255 * (grau - min_grau) / (max_grau - min_grau)) if max_grau > min_grau else 0
        cor = f"rgb({255 - intensidade_cor}, {intensidade_cor}, 100)"
        tamanho = 20

        tooltip = f"Grau: {grau} | Densidade Ego: {dens} | Microrregião: {micro}"
        net.add_node(
            bairro,
            label=bairro,
            title=tooltip,
            color=cor,
            size=tamanho,
            originalColor=cor
        )

    # adiciona arestas
    for origem_b, vizinhos in lista_adjacencia.items():
        for destino_b, peso in vizinhos:
            if destino_b in lista_adjacencia:
                net.add_edge(origem_b, destino_b, value=peso, color="rgba(100,100,100,0.5)", width=1)

    # escreve html
    net.write_html(output_html)

    # script para escolher dois bairros e destacar caminho
    script = f"""
        <script>

        const adj = {json.dumps(lista_adjacencia)};

        function dijkstra(graph, start, end) {{
            let distances = {{}};
            let prev = {{}};
            let pq = [];

            Object.keys(graph).forEach(v => distances[v] = Infinity);
            distances[start] = 0;
            pq.push([0, start]);

            while (pq.length > 0) {{
                pq.sort((a,b)=>a[0]-b[0]);
                let [dist, node] = pq.shift();
                if (node === end) break;

                for (let [neighbor, weight] of graph[node]) {{
                    let alt = dist + weight;
                    if (alt < distances[neighbor]) {{
                        distances[neighbor] = alt;
                        prev[neighbor] = node;
                        pq.push([alt, neighbor]);
                    }}
                }}
            }}

            // reconstruir caminho
            let path = [];
            let u = end;
            if (!(u in prev) && start !== end) return {{ path: [], cost: Infinity }};
            while (u) {{
                path.unshift(u);
                if (u === start) break;
                u = prev[u];
            }}
            return {{ path, cost: distances[end] }};
        }}


        function resetGraph() {{
            Object.values(network.body.nodes).forEach(n => {{
                n.setOptions({{
                    color: n.options.originalColor,
                    size: 20
                }});
            }});

            Object.values(network.body.edges).forEach(e => {{
                e.setOptions({{
                    color: "rgba(100,100,100,0.5)",
                    width: 1
                }});
            }});
        }}


        function highlightPath(orig, dest) {{
            let s = orig ?? document.getElementById("selOrigem").value;
            let t = dest ?? document.getElementById("selDestino").value;

            let result = dijkstra(adj, s, t);
            let p = result.path;
            let cost = result.cost;

            if (p.length === 0) {{
                alert("Sem caminho encontrado.");
                document.getElementById("custoCaminho").textContent = "—";
                return;
            }}

            resetGraph();

            // destaca nós
            p.forEach(n => {{
                let node = network.body.nodes[n];
                node.setOptions({{ color:"yellow", size:35 }});
            }});

            // destaca arestas
            for (let i=0;i<p.length-1;i++) {{
                let a = p[i], b = p[i+1];
                Object.values(network.body.edges).forEach(e => {{
                    if ((e.fromId===a && e.toId===b) || (e.fromId===b && e.toId===a)) {{
                        e.setOptions({{ color:"yellow", width:5 }});
                    }}
                }});
            }}

            document.getElementById("custoCaminho").textContent = cost;
        }}

        </script>

        <div style="padding:10px; display:flex; gap:10px; align-items:center;">
            <label>Origem:</label>
            <select id="selOrigem">
            {"".join([f'<option value="{b}">{b}</option>' for b in lista_adjacencia.keys()])}
            </select>

            <label>Destino:</label>
            <select id="selDestino">
            {"".join([f'<option value="{b}">{b}</option>' for b in lista_adjacencia.keys()])}
            </select>

            <button onclick="highlightPath()"> Encontrar Caminho</button>

            <label>Custo do Caminho: <span id="custoCaminho"></span></label>
        </div>

        <div style="padding:10px;">
            <label style="font-weight:bold;">Realçar Caminho:</label>
            <button onclick="highlightPath('nova descoberta', 'setubal')">
                Nova Descoberta → Setúbal
            </button>
        </div>

        <div style="padding:10px; width:260px;">
            <label style="font-weight:bold;">Legenda (grau):</label>
            <div style="
                height: 18px;
                background: linear-gradient(to right, red, green);
                border: 1px solid #999;
                margin-top: 4px;
                position: relative;
            ">
                <span style="
                    position: absolute;
                    left: 0;
                    top: 20px;
                    font-size: 12px;
                ">1</span>

                <span style="
                    position: absolute;
                    left: 50%;
                    transform: translateX(-50%);
                    top: 20px;
                    font-size: 12px;
                ">6</span>

                <span style="
                    position: absolute;
                    right: 0;
                    top: 20px;
                    font-size: 12px;
                ">11</span>
            </div>
        </div>
    """
    # injeta script no HTML
    with open(output_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("</body>", script + "\n</body>")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Grafo salvo em {output_html}")

if __name__ == "__main__":
    plot_percurso_nova_descoberta_setubal()
    mapa_de_cores_por_grau()
    ranking_densidade_ego_por_microrregiao()
    visualizar_grafo()
    histograma_graus()
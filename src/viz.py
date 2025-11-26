import json
import os
import pandas as pd
import matplotlib.pyplot as plt

from graphs.graph import carregar_lista_adjacencia
from graphs.io import carregar_lista_adjacencia_parte2
from solve import gerar_csv_graus, ego_network_metricas, calcular_peso_caminho_enderecos

from pyvis.network import Network
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_json = os.path.join(BASE_DIR, "../out/percurso_nova_descoberta_setubal.json")
arvore_percurso_html = os.path.join(BASE_DIR, "../out/arvore_percurso.html")
mapa_cores_graus_html = os.path.join(BASE_DIR, "../out/mapa_cores_graus.html")
ego_bairros_csv = os.path.join(BASE_DIR, "../out/ego_bairro.csv")
bairros_microrregiao_csv = os.path.join(BASE_DIR, "../data/bairros_unique.csv")

caminho_graus_csv = os.path.join(BASE_DIR, "../out/graus.csv")

caminho_csvFiltrado = os.path.join(BASE_DIR, "../data/dataset_parte2/csvFiltrado.csv")

gerar_csv_graus()
ego_network_metricas()
calcular_peso_caminho_enderecos()

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
    plt.title("Ranking de Microrregiões por Densidade Ego")
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
                net.add_edge(origem_b, destino_b,title=f"Peso: {peso}", value=peso, color="rgba(100,100,100,0.5)", width=1)

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
                    color: "rgba(100,100,100,0.5)"
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
                node.setOptions({{ color:"purple", size:35 }});
            }});

            // destaca arestas
            for (let i=0;i<p.length-1;i++) {{
                let a = p[i], b = p[i+1];
                Object.values(network.body.edges).forEach(e => {{
                    if ((e.fromId===a && e.toId===b) || (e.fromId===b && e.toId===a)) {{
                        e.setOptions({{ color:"purple"}});
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
        <div style="padding:10px;">
            <label style="font-weight:bold;">Trocar Grafo:</label>
            <button onclick="window.location.href = './digrafo_interativo.html'">
                Rotas Aereas EUA
            </button>
        </div>
        <div style="display:flex; gap:20px; flex-direction:row;">
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

        <div style="padding:10px; width:260px;">
            <label style="font-weight:bold;">Legenda (peso da aresta):</label>

            <div style="display:flex; flex-direction:column; gap:6px; margin-top:6px;">

                <div style="display:flex; align-items:center; gap:10px;">
                    <svg width="60" height="8">
                        <line x1="0" y1="4" x2="60" y2="4" stroke="black" stroke-width="1"/>
                    </svg>
                    <span style="font-size:12px;">peso baixo</span>
                </div>

                <div style="display:flex; align-items:center; gap:10px;">
                    <svg width="60" height="8">
                        <line x1="0" y1="4" x2="60" y2="4" stroke="black" stroke-width="3"/>
                    </svg>
                    <span style="font-size:12px;">peso médio</span>
                </div>

                <div style="display:flex; align-items:center; gap:10px;">
                    <svg width="60" height="8">
                        <line x1="0" y1="4" x2="60" y2="4" stroke="black" stroke-width="6"/>
                    </svg>
                    <span style="font-size:12px;">peso alto</span>
                </div>
            </div>
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

def visualizar_digrafo(
    lista_adjacencia=carregar_lista_adjacencia_parte2(),
    output_html="out/digrafo_interativo.html",
):
    # converte
    vertices = list(lista_adjacencia.keys())
    arestas = []
    for o, viz in lista_adjacencia.items():
        for d, p in viz:
            arestas.append([o, d, p])

    net = Network(height="850px", width="100%", directed=True)
    net.force_atlas_2based()

    # nós
    for v in vertices:
        cor = "rgb(80, 163, 199)"
        net.add_node(v, label=v, color=cor, originalColor=cor, size=18)

    # arestas dirigidas
    for o, d, p in arestas:
        net.add_edge(
            o,
            d,
            value=p,
            title=f"Peso {p}",
            arrows="to",
            color="rgba(80, 163, 199, 0.5)",
            originalColor="rgba(80, 163, 199, 0.5)"
        )

    net.write_html(output_html)

    script = f"""
    <script>
        
        const bfVertices = {json.dumps(vertices)};
        const bfArestas = {json.dumps(arestas)};

        function bellmanFord(vertice, aresta, start, end) {{
            let dist = {{}};
            let parent = {{}};

            vertice.forEach(v => {{
                dist[v] = Infinity;
                parent[v] = null;
            }});

            dist[start] = 0;

            aresta = aresta.map(e => [e[0], e[1], Number(e[2])]);

            for (let i = 0; i < vertice.length - 1; i++) {{
                aresta.forEach(([u, v, w]) => {{
                    if (dist[u] !== Infinity && dist[u] + w < dist[v]) {{
                        dist[v] = dist[u] + w;
                        parent[v] = u;
                    }}
                }});
            }}

            if (dist[end] === Infinity)
                return {{ path: [], cost: Infinity }};

            let path = [];
            let cur = end;

            while (cur !== null) {{
                path.push(cur);
                cur = parent[cur];
            }}

            path.reverse();
            return {{ path, cost: dist[end] }};
        }}

        function highlightBF() {{
            let s = document.getElementById("orig").value;
            let t = document.getElementById("dest").value;

            let result = bellmanFord(bfVertices, bfArestas, s, t);
            let path = result.path;
            let cost = result.cost;

            if (path.length === 0) {{
                alert("Sem caminho.");
                document.getElementById("custo").textContent = "";
                return;
            }}

            resetGraph();

            path.forEach(n => {{
                let node = network.body.nodes[n];
                if (node) node.setOptions({{ color: "purple", size: 30 }});
            }});

            
            let a = path[0];
            let b = path[1];

            Object.values(network.body.edges).forEach(e => {{
                if (e.fromId === a && e.toId === b) {{
                    e.setOptions({{ color: "purple" }});
                }}
            }});
            

            document.getElementById("custo").textContent = cost;
        }}

        function resetGraph() {{
            Object.values(network.body.nodes).forEach(n => {{
                n.setOptions({{
                    color: n.options.color ? n.options.color : "rgb(80, 163, 199)",
                    size: 18
                }});
            }});

            Object.values(network.body.edges).forEach(e => {{
                e.setOptions({{
                    color: "rgba(80, 163, 199, 0.5)"
                }});
            }});
        }}

    </script>  
    <div style="padding:10px; ">
        <div style="padding:10px;">
        Origem:
        <select id="orig">
            {"".join([f'<option value="{v}">{v}</option>' for v in vertices])}
        </select>

        Destino:
        <select id="dest">
            {"".join([f'<option value="{v}">{v}</option>' for v in vertices])}
        </select>

        <button onclick="highlightBF()">Menor Caminho (Bellman-Ford)</button>

        <span style="margin-left:12px;font-weight:bold;">
            Custo: <span id="custo"></span>
        </span>
        </div>
        <div style="padding:10px;">
            <label style="font-weight:bold;">Trocar Grafo:</label>
            <button onclick="window.location.href = './grafo_interativo.html'">
                Bairros de Recife
            </button>
        </div>
    </div>  
    """
    
    with open(output_html) as f:
        html = f.read()

    html = html.replace("</body>", script + "</body>")

    with open(output_html, "w") as f:
        f.write(html)

    print("Digrafo salvo em:", output_html)

def gerar_grafico_distribuicao_graus(lista_adj):
    #---------------
    # Função pra gerar o grafico de graus de saída
    #---------------

    print("Gerando grafico de distribuição de graus.")

    # Para cada vizinho na lista de adjacencia, aumenta o grau de saida

    graus_saida = []
    for vizinhos in lista_adj.values():
        graus_saida.append(len(vizinhos))
    
    plt.figure(figsize=(10, 6))
    
    plt.hist(graus_saida, bins=30, color='skyblue', edgecolor='black')
    
    plt.title("Distribuição de Graus de Saída (Out-Degree) - Dataset Voos")
    plt.xlabel("Grau de Saída (Nº de Destinos)")
    plt.ylabel("Frequência (Nº de Aeroportos)")
    plt.grid(True, alpha=0.3)
    
    caminho_img = os.path.join(BASE_DIR, "../out/distribuicao_graus.png")
    os.makedirs(os.path.dirname(caminho_img), exist_ok=True)
    
    plt.savefig(caminho_img)
    print(f"Visualização salva em: {caminho_img}")
    plt.close()

def main_viz():
    lista_adj = carregar_lista_adjacencia_parte2(caminho_csvFiltrado)

    plot_percurso_nova_descoberta_setubal()
    mapa_de_cores_por_grau()
    ranking_densidade_ego_por_microrregiao()
    visualizar_grafo()
    visualizar_digrafo()
    histograma_graus()

    gerar_grafico_distribuicao_graus(lista_adj)

if __name__ == "__main__":
    main_viz()
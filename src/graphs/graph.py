import pandas as pd
from pathlib import Path

# === Caminhos ===
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ARQ_BAIRROS = DATA_DIR / "bairros_unique.csv"
ARQ_ADJ = DATA_DIR / "adjacencias_bairros.csv"


def calcular_peso(categoria_via: str, ponte=False, semaforos=0, horario_pico=False, alpha=1.0, beta=1.0):
    """
    Calcula o peso de uma aresta segundo a fórmula:
        peso = α·categoria + β·penalidades
    onde:
        categoria: avenida (1.0), coletora (1.5), local (2.0)
        penalidades: +0.5 ponte/túnel, +0.2 por semáforo, +α se horário de pico
    """
    categoria_via = (categoria_via or "").strip().lower()

    categorias = {
        "avenida": 1.0,
        "coletora": 1.5,
        "local": 2.0
    }

    base = categorias.get(categoria_via, 2.0)
    penalidades = 0.0

    if ponte:
        penalidades += 0.5
    if semaforos > 0:
        penalidades += semaforos * 0.2
    if horario_pico:
        penalidades += alpha  

    peso = alpha * base + beta * penalidades
    return round(peso, 2)


def gerar_adjacencias_automaticas(alpha=1.0, beta=1.0):

    if not ARQ_BAIRROS.exists():
        raise FileNotFoundError(f"Arquivo {ARQ_BAIRROS} não encontrado.")

    df_bairros = pd.read_csv(ARQ_BAIRROS)

    arestas = []
    for microrregiao, grupo in df_bairros.groupby("microrregiao"):
        bairros = sorted(grupo["bairro"].unique())

        for i in range(len(bairros)):
            for j in range(i + 1, len(bairros)):
                categoria = "avenida" if i % 3 == 0 else ("coletora" if i % 3 == 1 else "local")
                ponte = (j % 5 == 0)
                semaforos = (i + j) % 3
                horario_pico = (i + j) % 7 == 0

                peso = calcular_peso(
                    categoria_via=categoria,
                    ponte=ponte,
                    semaforos=semaforos,
                    horario_pico=horario_pico,
                    alpha=alpha,
                    beta=beta
                )

                arestas.append({
                    "bairro_origem": bairros[i],
                    "bairro_destino": bairros[j],
                    "logradouro": f"Via {i}-{j}",
                    "observacao": f"Mesma microrregião {microrregiao}, tipo={categoria}",
                    "peso": peso
                })

    df_adj = pd.DataFrame(arestas)
    df_adj.to_csv(ARQ_ADJ, index=False)
    print(f"[+] Arquivo gerado: {ARQ_ADJ} ({len(df_adj)} arestas criadas).")


def carregar_adjacencias():
    if not ARQ_ADJ.exists():
        print("Nenhum arquivo de adjacências encontrado.")
        return None
    return pd.read_csv(ARQ_ADJ)


if __name__ == "__main__":
    # Exemplo: α = 1.0, β = 1.0
    gerar_adjacencias_automaticas(alpha=1.0, beta=1.0)

    df = carregar_adjacencias()
    if df is not None:
        print(df.head(10))

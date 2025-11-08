import csv
from collections import defaultdict
import os

# Função que lê um arquivo CSV contendo as arestas
# e constrói uma lista de adjacência representando o grafo.
def carregar_lista_adjacencia(caminho_csv: str) -> dict[str, list[tuple[str, float]]]:
    # Cria um dicionário que, para cada bairro (vértice),
    # armazenará uma lista de tuplas (vizinho, peso da ligação)
    grafo = defaultdict(list)

    # Abre o arquivo CSV no modo leitura
    with open(caminho_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)  # Lê o CSV como um dicionário, usando o cabeçalho como chave

        # Percorre cada linha (aresta) do CSV
        for linha in reader:
            # Normaliza os nomes dos bairros (remove espaços extras e coloca em minúsculo)
            origem = linha["bairro_origem"].strip().lower()
            destino = linha["bairro_destino"].strip().lower()
            # Converte o peso (distância) para tipo float
            peso = float(linha["peso"])

            # Adiciona a conexão nas duas direções (pois o grafo é não-direcionado)
            # Exemplo: se há uma ligação entre "recife" e "boa vista",
            # ambos passam a ser vizinhos um do outro.
            grafo[origem].append((destino, peso))
            grafo[destino].append((origem, peso))

    # Converte o defaultdict em dict normal antes de retornar
    return dict(grafo)

def csv_para_lista(caminho_arquivo: str):
    # Lista para armazenar o resultado
    resultado = []

    # Abre o arquivo CSV no modo leitura
    with open(caminho_arquivo, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)

        # Percorre cada linha do CSV
        for linha in leitor:
            origem = linha["bairro_origem"].strip()
            destino = linha["bairro_destino"].strip()
            logradouro = linha["logradouro"].strip()
            peso = float(linha["peso"])

            # Armazena um objeto do tipo dicionario com as informações de cada aresta
            resultado.append({
                "vertice_origem": origem,
                "vertice_destino": destino,
                "aresta": logradouro,
                "peso": peso
            })

    return resultado

# Bloco principal — só é executado se o arquivo for rodado diretamente (não importado)
if __name__ == "__main__":
    # Caminho relativo até o CSV de arestas (ajuste conforme estrutura do projeto)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(BASE_DIR, "../../data/adjacencias_bairros.csv")

    try:
        # Carrega a lista de adjacência a partir do arquivo CSV
        grafo = carregar_lista_adjacencia(caminho_csv)

        print("Lista de adjacência carregada com sucesso!\n")
        print(f"Total de bairros (vértices): {len(grafo)}\n")

        print("Conexões:\n")
        # Exibe cada bairro e seus vizinhos com as distâncias
        for bairro, vizinhos in list(grafo.items()):
            print(f"{bairro} → {vizinhos}")
            print("\n")

    # Captura o erro caso o arquivo não seja encontrado no caminho especificado
    except FileNotFoundError:
        print(f"Arquivo não encontrado em: {caminho_csv}")

    # Captura qualquer outro erro inesperado (ex: erro de leitura ou formatação)
    except Exception as e:
        print(f"Erro ao carregar o grafo: {e}")
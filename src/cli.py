import argparse
import os
import sys
import json

sys.path.append("src/")

from graphs.algorithms import dijkstra_path, bfs
from graphs.graph import carregar_lista_adjacencia
from solve import deque_to_string
from viz import visualizar_grafo

DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(DIR, "../")

def dijkstra_output(source, target, dataset_path, output_dir):
    custo, caminho = dijkstra_path(carregar_lista_adjacencia(), source, target)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"{source}_{target}_dijkstra_resultado.json")
    with open(output_path, "w") as f:
        json.dump({
            "caminho": deque_to_string(caminho),
            "custo": custo
        }, f)

    print(f"Resultado salvo em: {output_path}")

def bfs_output(source, dataset_path, output_dir):
    caminho = bfs(carregar_lista_adjacencia(), source)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"{source}_bfs_resultado.json")
    with open(output_path, "w") as f:
        json.dump({
            "caminho": deque_to_string(caminho)
        }, f)

    print(f"Resultado salvo em: {output_path}")

def interactive_output(dataset_path, output_dir):
    output_path = os.path.join(output_dir, "grafo_interativo.html")
    visualizar_grafo(output_html=output_path)


def main():
    parser = argparse.ArgumentParser(
        description="CLI para algoritmos de grafos sobre bairros do Recife"
    )

    parser.add_argument(
        "--dataset",
        required=False,
        help="Caminho para o CSV de bairros"
    )

    parser.add_argument(
        "--alg",
        choices=["BFS", "DIJKSTRA"],
        help="Algoritmo a ser executado"
    )

    parser.add_argument(
        "--source",
        help='Bairro de origem (ex: "boa viagem")'
    )

    parser.add_argument(
        "--target",
        help='Bairro de destino (ex: "recife")'
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interativo"
    )

    parser.add_argument(
        "--out",
        help="Diretório de saída"
    )

    args = parser.parse_args()

    # -------- LÓGICA -------- #

    if not args.dataset:
        print("Erro: --dataset deve ser informado")
        return
    
    if not args.out:
        print("Erro: --out deve ser informado")
        return
    
    DATASET_DIR = os.path.join(BASE_DIR, args.dataset)
    OUTPUT_DIR = os.path.join(BASE_DIR, args.out)

    if args.interactive:
        interactive_output(
            DATASET_DIR,
            OUTPUT_DIR
        )
        return
    
    if not args.alg and not args.interactive:
        print("Erro: --alg deve ser informado se --interactive não for usado")
        return

    if args.alg == "DIJKSTRA":
        if not args.source:
            print("Erro: --source deve ser informado")
            return

        if not args.target:
            print("Erro: --target deve ser informado para o algoritmo DIJKSTRA")
            return
        
        dijkstra_output(
            str(args.source).lower(),
            str(args.target).lower(),
            DATASET_DIR,
            OUTPUT_DIR
        )

        return

    if args.alg == "BFS":
        if not args.source:
            print("Erro: --source deve ser informado")
            return
        
        bfs_output(
            str(args.source).lower(),
            DATASET_DIR,
            OUTPUT_DIR
        )

        return

    if args.alg not in ["BFS", "DIJKSTRA"]:
        print(f"Erro: algoritmo {args.alg} não reconhecido")
        return


if __name__ == "__main__":
    main()

import sys
import os
# Arrumando o caminho pra conseguir importar os algoritmos da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from graphs.algorithms import bfs

def test_bfs_basico():
    # Montando um grafo simples pra testar se o BFS respeita os níveis
    # A é pai de B e C
    grafo_teste = {
        "A": [("B", 1), ("C", 1)],
        "B": [],
        "C": []
    }
    
    # Rodando o algoritmo a partir do nó A
    ordem_visitada = bfs(grafo_teste, "A")
    
    # O primeiro tem que ser o nó de origem
    assert ordem_visitada[0] == "A"
    
    # Como B e C são vizinhos diretos, eles devem aparecer logo depois do A
    # (A ordem entre B e C não importa no BFS, mas ambos têm que estar lá)
    vizinhos = ordem_visitada[1:] # Pega do segundo elemento até o fim
    
    assert "B" in vizinhos
    assert "C" in vizinhos
    
    # Verifica se o tamanho tá certo (não pode ter visitado nenhum a mais)
    assert len(ordem_visitada) == 3
import sys
import os
# Arrumando o caminho pra conseguir importar os algoritmos da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from graphs.algorithms import dfs

def test_dfs_classificacao_arestas():
    # Testa o caminho básico de arestas de arvore
    # Grafo simples: A -> B -> C, sem voltas
    grafo = {
        "A": [("B", 1)],
        "B": [("C", 1)],
        "C": []
    }
    
    resultado = dfs(grafo, "A")
    
    # Tem que visitar na ordem de profundidade: A, depois B, depois C
    assert resultado == ["A", "B", "C"]

def test_dfs_deteccao_ciclo():
    # Testa detecção de ciclo e aresta de retorno
    # Cenário: A -> B, e B tem uma aresta que volta para A (Ciclo)
    grafo_ciclo = {
        "A": [("B", 1)],
        "B": [("A", 1)] 
    }
    
    visitados = dfs(grafo_ciclo, "A")
    
    # Para validar os testes
    # 1. Não pode travar em loop infinito
    # 2. Tem que visitar os dois nós (A e B) e parar quando achar o ciclo
    assert len(visitados) == 2
    assert "A" in visitados
    assert "B" in visitados
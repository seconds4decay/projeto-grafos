import sys
import os
# Arrumando o path para importar corretamente da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from graphs.algorithms import dijkstra_path

def test_dijkstra_caminho_correto():
    # Teste de lógica: Caminho mais curto vs Caminho direto
    # A -> B custa 10 (Direto, mas caro)
    # A -> C -> B custa 1 + 1 = 2 (Mais longo em nós, mas mais barato)
    grafo = {
        "A": [("B", 10), ("C", 1)],
        "B": [],
        "C": [("B", 1)]
    }
    
    # Roda o algoritmo pedindo o caminho de A até B
    custo_total, rota = dijkstra_path(grafo, "A", "B")
    
    # O Dijkstra tem que escolher o melhor caminho de custo 2
    assert custo_total == 2
    
    # Verifica se a rota foi A -> C -> B
    assert list(rota) == ["A", "C", "B"]

def test_dijkstra_rejeita_pesos_negativos():
    # O Dijkstra  não funciona bem com pesos negativos entao vamos testar
    # foi programado para retornar -1 como flag de erro.
    grafo_invalido = {
        "A": [("B", -5)]
    }
    
    resultado = dijkstra_path(grafo_invalido, "A", "B")
    
    # Tem que retornar o código de erro -1
    assert resultado == -1
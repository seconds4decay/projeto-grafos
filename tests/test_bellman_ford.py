import sys
import os
# Ajuste de path para importar da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from graphs.algorithms import bellman_ford

def test_bf_com_pesos_negativos():
    # Pesos negativos (sem ciclo)
    #  A -> B custa 10, mas B -> C tem peso -5 .
    # Custo total A -> C deve ser 10 - 5 = 5.
    
    lista_vertices = ["A", "B", "C"]
    lista_arestas = [
        ("A", "B", 10),
        ("B", "C", -5)
    ]
    
    # Executa partindo de A
    mapa_distancias = bellman_ford(lista_vertices, lista_arestas, "A")
    
    # Verificando se o resultado foi correto =5 
    assert mapa_distancias["C"] == 5

def test_bf_ciclo_negativo():
    # Detectar o ciclo negativo
    # A vai pra B (custo 1) e B volta pra A (custo -5).
    # Total do ciclo: 1 - 5 = -4. Isso causaria loop infinito se não tratado.
    
    nos = ["A", "B"]
    conexoes = [
        ("A", "B", 1),
        ("B", "A", -5)
    ]
    
    resultado = bellman_ford(nos, conexoes, "A")
    
    # O algoritmo deve perceber o ciclo e retornar a flag de erro (-1)
    assert resultado == -1
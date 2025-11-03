import heapq
import sys

def dijkstra(vertices, arestas, v_inicio):

    # Definição dos parâmetros:
    #   vertices -> lista de vértices
    #   arestas -> lista de arestas onde cada elemento é uma lista organizada da seguinte forma: [vertice de origem, vertice de destino, peso]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo

    # cria-se uma lista de adjacencia (dicionário)
    lista_adjacencia = {}

    # deifine as chaves do dicionario como os vértices
    for vertice in vertices:
        lista_adjacencia[vertice] = []
    
    # para cada vértice (chave do dicionário), um valor no formato (vertice destino, peso)
    for v_origem, v_destino, peso in arestas:
        lista_adjacencia[v_origem].append([v_destino, peso])

    # o resultado sai no seguinte formato: vértice -> distância mínima
    resultado = {}
    
    # define como "infinito" (no caso, é só um valor muito grande) para os vértices, no momento, inalcançáveis
    for vertice in vertices:
        resultado[vertice] = sys.maxsize

    # o vértice de início sempre tem peso 0
    resultado[v_inicio] = 0

    # o min heap (fila de prioridade) serve para guardar os vértices e a distância atual para alcança-los
    # a fila de prioridade vai priorizar as menores distâncias durante a análise, evitando desperdício de tempo
    min_heap = []

    # carrega a fila com o vértice inicial
    heapq.heappush(min_heap, [0, v_inicio])

    # enquanto min_heap não for vazio
    while min_heap:

        #retira e obtém o valor com menor distância presente na fila de prioridade
        distancia, vertice = heapq.heappop(min_heap)

        # ocorre a verificação de cada vértice adjacente ao vértice analisado
        for v_adjacente, peso in lista_adjacencia[vertice]:

            # caso o a distância atual + peso para chegar no vértice adjacente é menor que a distância atual, o valor é atualizado
            if (distancia + peso) < resultado[v_adjacente]:
                resultado[v_adjacente] = distancia + peso

                # além disso, o a nova distância atual e o vértice adjacente é carregado na fila de prioridade
                heapq.heappush([distancia + peso, v_adjacente])

    # retorna o resultado
    return resultado
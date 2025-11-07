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


def bellman_ford(vertices, arestas, v_inicio):

    # Definição dos parâmetros:
    #   vertices -> lista de vértices
    #   arestas -> lista de arestas onde cada elemento é uma lista organizada da seguinte forma: [vertice de origem, vertice de destino, peso]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo


    # o resultado sai no seguinte formato: vértice -> distância mínima
    resultado = {}
    
    # define como "infinito" (no caso, é só um valor muito grande) para os vértices, no momento, inalcançáveis
    for vertice in vertices:
        resultado[vertice] = sys.maxsize

    # o vértice de início sempre tem peso 0
    resultado[v_inicio] = 0

    # define-se o número máximo de iterações n - 1
    iteracoes = len(vertices) - 1

    # começo das iterações do algoritmo
    for i in range (iteracoes):

        #percorre todas as arestas
        for aresta in arestas:
            v_origem = aresta[0]
            v_destino = aresta[1]
            peso = aresta[2]

            # caso a distância para o vértice de origem for alcançável (não for infinita)
            # e
            # a distância para o vértice de origem + o peso da aresta for menor que a distância para o vértice de destino
            if resultado[v_origem] != sys.maxsize and (resultado[v_origem] + peso) < resultado[v_destino]:

                # a distância do vértice de destino é atualizada
                resultado[v_destino] = resultado[v_origem] + peso
    
    # aqui é feita mais uma iteração para checar se há ciclos negativos
    for aresta in arestas:
        v_origem = aresta[0]
        v_destino = aresta[1]
        peso = aresta[2]
        
        # caso seja possível diminuir a distância de algum vértice após n - 1 ciclos
        if resultado[v_origem] != sys.maxsize and (resultado[v_origem] + peso) < resultado[v_destino]:

            # o algoritmo retorna um número negativo para indicar a existência de um ciclo negativo no grafo
            resultado = -1

    #retorna o resultado
    return resultado

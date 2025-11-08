import heapq
import sys
from collections import deque

def dijkstra(lista_adjacencia, v_inicio):

    # Definição dos parâmetros:
    #   vertices -> lista de vértices
    #   arestas -> lista de arestas onde cada elemento é uma lista organizada da seguinte forma: [vertice de origem, vertice de destino, peso]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo

    # cria-se uma lista de adjacencia (dicionário)
    # o resultado sai no seguinte formato: vértice -> distância mínima
    resultado = {}
    
    # define como "infinito" (no caso, é só um valor muito grande) para os vértices, no momento, inalcançáveis
    for vertice in lista_adjacencia.keys():
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
                heapq.heappush(min_heap, [distancia + peso, v_adjacente])

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


def bfs(lista_adjacencia, v_inicio):

    # Definição dos parâmetros:
    #   lista_adjacencia -> lista de adjacencia do grafo
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo


    # o resultado do algoritmo será uma lista com a sequência de vertices visitados pelo bfs
    resultado = []

    # cria-se e popula-se um dicionário (vertice -> estado de visitação) para determinar se um vertice já foi ou não visitado pelo algoritmo
    visitado = {}

    vertices = list(lista_adjacencia.keys())
    for vertice in vertices:
        visitado[vertice] = False


    # uma fila é criada para guardar os vértices que serão analisados em cada iteração
    queue = deque()

    # o vértice de início é adicionado na fila e tem seu estado de visitação mudado para True, indicando que já está sendo visitado
    queue.append(v_inicio)
    visitado[v_inicio] = True

    # enquanto a fila não estiver vazia
    while queue:
        
        # o vértice na frente da fila é retirado
        vertice = queue.popleft()

        # o vértice é adicionado à sequência de resultado
        resultado.append(vertice)

        # percorre-se os vértices adjacentes ao vértice analisado
        for v_adjacente, peso in lista_adjacencia[vertice]:
            
            # se o vértice adjacente ainda não foi visitado
            if visitado[v_adjacente] == False:

                # vértice adjacente é marcado como visitado e adicionado à fila
                visitado[v_adjacente] = True
                queue.append(v_adjacente)

    # retorna o resultado
    return resultado

def dfs(lista_adjacencia, v_inicio):

    # Definição dos parâmetros:
    #   lista_adjacencia -> lista de adjacencia do grafo
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo

    # o resultado do algoritmo será uma lista com a sequência de vertices visitados pelo bfs
    resultado = []

    # cria-se e popula-se um dicionário (vertice -> estado de visitação) para determinar se um vertice já foi ou não visitado pelo algoritmo
    visitado = {}

    vertices = list(lista_adjacencia.keys())
    for vertice in vertices:
        visitado[vertice] = False

    
    # o vértice de início tem seu estado de visitação mudado para True, indicando que já está sendo visitado
    visitado[v_inicio] = True

    # início da chamada recursiva da função auxiliar de "mergulho" na profundidade do grafo
    dfs_aux(v_inicio, visitado, lista_adjacencia, resultado)

    # retorna o resultado
    return resultado


def dfs_aux(vertice, visitado, lista_adjacencia, resultado):

    # Definição dos parâmetros:
    #   vertice -> vértice que está sendo visitado pelo algoritmo
    #   visitado -> dicionário com os estados de visitação dos vértices
    #   lista_adjacencia -> lista de adjacencia do grafo
    #   resultado -> lista com a sequência de vértices visitados pelo dfs

    # o vértice é marcado como visitado pelo algoritmo e adicionado ao resultado
    visitado[vertice] = True
    resultado.append(vertice)

    # para cada vértice adjacente ao vértice visitado
    for v_adjacente, peso in lista_adjacencia[vertice]:
            
            # se o vértice adjacente ainda não foi visitado
            if visitado[v_adjacente] == False:

                # ocorre a chamada recursiva da função auxiliar, iniciando o processo de visitação com o vértice adjacente
                dfs_aux(v_adjacente, visitado, lista_adjacencia, resultado)


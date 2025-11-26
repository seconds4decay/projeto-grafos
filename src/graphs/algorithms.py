import heapq
import sys
from collections import deque

def dijkstra(lista_adjacencia, v_inicio):

    # Definição dos parâmetros:
    #   lista_adjacencia -> lista de adjacencia do grafo: vértice -> [[vértice adjacente, peso]]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo

    # checagem para pesos negativos no grafo
    for vertice in lista_adjacencia.keys():
        for v_adjacente, peso in lista_adjacencia[vertice]:
            if peso < 0:
                return -1

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

def dijkstra_path(lista_adjacencia, v_inicio, v_destino):

    # Definição dos parâmetros:
    #   lista_adjacencia -> lista de adjacencia do grafo: vértice -> [[vértice adjacente, peso]]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo
    #   v_destino -> vértice de destino do caminho que será gerado

    # checagem para pesos negativos no grafo
    for vertice in lista_adjacencia.keys():
        for v_adjacente, peso in lista_adjacencia[vertice]:
            if peso < 0:
                return -1

    # o resultado sai no seguinte formato: vértice -> distância mínima
    resultado = {}

    # cria-se um dicionário que irá guardar os antecessores adjacentes do caminho: vértice -> vértice antecessor
    antecessor = {}
    
    # define como "infinito" (no caso, é só um valor muito grande) para os vértices, no momento, inalcançáveis
    for vertice in lista_adjacencia.keys():
        resultado[vertice] = sys.maxsize
        antecessor[vertice] = None

    # o vértice de início sempre tem peso 0
    resultado[v_inicio] = 0

    # o antecessor do vértice de início é ele mesmo
    antecessor[v_inicio] = v_inicio

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

                # o antecessor do vértice adjacente atualizado é modificado
                antecessor[v_adjacente] = vertice
                # além disso, o a nova distância atual e o vértice adjacente é carregado na fila de prioridade
                heapq.heappush(min_heap, [distancia + peso, v_adjacente])

    # caso não exista um caminho para chegar o vértice de destino partindo do vértice de início, o algoritmo retorna "infinito" e -1
    if (resultado[v_destino] == sys.maxsize or antecessor[v_destino] == None):
        return resultado[v_destino], -1
    
    # cria-se uma fila para gerar o caminho do vértice de início até o vértice de destino
    caminho = deque()

    # adicona o vértice de destino ao final da fila
    caminho.appendleft(v_destino)

    # cria-se uma variável para definir uma condição de parada
    atual = v_destino

    # enquanto atual for diferente do início
    while atual != v_inicio:
        # o antecessor do atual é adicionado à fila
        caminho.appendleft(antecessor[atual])

        # o atual é atualizado para ser seu antecessor
        atual = antecessor[atual]


    # retorna o custo e o caminho mais curto para chegar ao vértice de destino partindo do vértice de início
    return resultado[v_destino], caminho

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
            break

    #retorna o resultado
    return resultado

def bfs(lista_adjacencia, v_inicio):

    # Definição dos parâmetros:
    #   lista_adjacencia -> lista de adjacencia do grafo: vértice -> [[vértice adjacente, peso]]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo


    # o resultado do algoritmo será uma lista com a sequência de vertices visitados pelo bfs
    resultado = []

    # cria-se e popula-se um dicionário (vertice -> estado de visitação) para determinar se um vertice já foi ou não visitado pelo algoritmo
    visitado = {}

    vertices = lista_adjacencia.keys()
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
    #   lista_adjacencia -> lista de adjacencia do grafo: vértice -> [[vértice adjacente, peso]]
    #   v_inicio -> vértice de início que será utilizado como referência para o começo do algoritmo

    # o resultado do algoritmo será uma lista com a sequência de vertices visitados pelo bfs
    resultado = []

    # cria-se e popula-se um dicionário (vertice -> estado de visitação) para determinar se um vertice já foi ou não visitado pelo algoritmo
    visitado = {}

    # um conjunto auxiliar para rastrear quem está na pilha de execução agora, usa isso para pegar ciclos e saber o tipo da aresta e classifica-la.
    pilha_recursao = set()

    vertices = lista_adjacencia.keys()
    for vertice in vertices:
        visitado[vertice] = False

    
    # o vértice de início tem seu estado de visitação mudado para True, indicando que já está sendo visitado
    visitado[v_inicio] = True

    # início da chamada recursiva da função auxiliar de "mergulho" na profundidade do grafo
    # adicionado o parametro de pilha_recursao
    dfs_aux(v_inicio, visitado, lista_adjacencia, resultado,pilha_recursao)

    # retorna o resultado
    return resultado

def dfs_aux(vertice, visitado, lista_adjacencia, resultado,pilha_recursao):

    # Definição dos parâmetros:
    #   vertice -> vértice que está sendo visitado pelo algoritmo
    #   visitado -> dicionário com os estados de visitação dos vértices
    #   lista_adjacencia -> lista de adjacencia do grafo: vértice -> [[vértice adjacente, peso]]
    #   resultado -> lista com a sequência de vértices visitados pelo dfs

    # o vértice é marcado como visitado pelo algoritmo e adicionado ao resultado
    visitado[vertice] = True
    #adiciona o vertice atual a pilha e a pilha de recursao
    pilha_recursao.add(vertice)
    resultado.append(vertice)

    # para cada vértice adjacente ao vértice visitado
    for v_adjacente, peso in lista_adjacencia[vertice]:
            
            # se o vértice adjacente ainda não foi visitado
            if visitado[v_adjacente] == False:

                # Se não foi visitado, é uma aresta de árvore,logo um caminho novo
                print(f"Aresta de Árvore {vertice} -> {v_adjacente}")

                # ocorre a chamada recursiva da função auxiliar, iniciando o processo de visitação com o vértice adjacente
                dfs_aux(v_adjacente, visitado, lista_adjacencia, resultado,pilha_recursao)
            else:
                # Se o vizinho estiver na pilha de recursão,isso significa que é uma aresta de retorno,indicando um ciclo
                if v_adjacente in pilha_recursao:
                    print(f"Aresta de Retorno {vertice} -> {v_adjacente} ")
                
                # Se já foi visitado mas não está na pilha, é aresta de avanço
                else:
                    print(f"[Aresta de Avanço] {vertice} -> {v_adjacente}")
    # Remove o vértice da pilha antes de voltar
    pilha_recursao.remove(vertice)

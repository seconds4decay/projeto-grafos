import csv
import os
import unicodedata
import re
from collections import defaultdict

def normalizar_nome(nome: str) -> str:
    # Remove acentos, espaços extras e transforma em minúsculas
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ASCII", "ignore").decode("utf-8").lower().strip()
    nome = re.sub(r"\s+", " ", nome)  # colapsa espaços internos
    return nome

##############################
# PARTE 1
##############################

# Derrete o csv bairros_recife.csv e transforma em uma dicionario 
def derreter_bairros_recife(input_path: str) -> dict[str, str]:
    with open(input_path, newline='', encoding="utf-8") as csvfile: #Abre o arquivo csv
        reader = csv.DictReader(csvfile) # lê como um dicionario
        colunas_microrregiao = [c for c in reader.fieldnames if re.match(r"^[1-6]\.[1-3]$", c)] # Pega só as colunas que batem com o padrão (1.1,2.3,etc)
        
        bairros_dict: dict[str, str] = {} # Bairro -> Microrregião 
        
        for row in reader:  # Percorre o dicionario 
            for microrregiao in colunas_microrregiao:
                celula = row[microrregiao]
                if not celula:
                    continue
                
                bairros = [b.strip() for b in celula.split(",") if b.strip()] #Divide os bairros separados por vírgula 
                
                for bairro in bairros:  #Percorre bairros para normalizar 
                    bairro_norm = normalizar_nome(bairro)
                    
                    if not bairro_norm: #Garante que o nome do bairro não está vazio 
                        raise ValueError(f"Bairro vazio encontrado em microrregião {microrregiao}")
                                
                    if bairro_norm in bairros_dict:     #Se o bairro já foi salvo antes em outra microrregião ele não adiciona no dicionário 
                        if bairros_dict[bairro_norm] != microrregiao:
                            continue
                    else:  #Caso contrário adiciona ao dicioniario 
                        bairros_dict[bairro_norm] = microrregiao

        return bairros_dict

def salvar_bairros_unique(bairros_dict: dict[str, str], output_path: str) -> None: #Gera o arquivo bairros_unique.csv a partir do dicionário {bairro: microrregiao}.
    # Abre (ou cria) o arquivo CSV para escrita
    with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Cabeçalho fixo
        writer.writerow(["bairro", "microrregiao"])
        
        # Escreve cada linha do dicionário
        for bairro, microrregiao in bairros_dict.items():
            writer.writerow([bairro, microrregiao])

    print(f"Arquivo salvo com sucesso em: {output_path}")

##############################
# PARTE 2
##############################

# Função pra ler o dataset bruto 
def ler_dataset_bruto(caminho: str):
    linhas = []

    with open(caminho, newline='', encoding="utf-8") as f:
        leitor = csv.DictReader(f) 
        for linha in leitor:
            linhas.append(linha)
    return linhas   

# Função pra filtrar o dataset e gerar um csv limpo
def filtrar_dataset_2024_e_gerar_csv(caminho_entrada: str, caminho_saida: str):
    with open(caminho_entrada, newline='', encoding="utf-8") as f_in:
        leitor = csv.DictReader(f_in) # lê como um dicionario

        # Já prepara o arquivo de saída 
        with open(caminho_saida, "w", encoding="utf-8", newline="") as f_out:
            escritor = csv.writer(f_out)

            # Cabeçalho 
            escritor.writerow(["vertice_origem", "vertice_destino", "peso"])

            # Pra evitar duplicatas
            vistos = set()

            for linha in leitor:
                # Filtra apenas voos de 2024
                if linha["Year"] != "2024":
                    continue

                vertice_origem = linha["airport_1"].strip().lower()
                vertice_destino = linha["airport_2"].strip().lower()
                peso_str = linha["nsmiles"].strip()

                # validações básicas
                if not vertice_destino or not vertice_origem or not peso_str:
                    continue
                
                # Converte peso para float
                peso = float(peso_str)
                
                # Verifica duplicatas
                chave = (vertice_origem, vertice_destino)
                if chave in vistos:
                    continue
                vistos.add(chave)
                
                # Escreve no arquivo de saída
                escritor.writerow([vertice_origem, vertice_destino, peso])

def carregar_lista_adjacencia_parte2(caminho_csv: str) -> dict:
    grafo = defaultdict(list)

    with open(caminho_csv, newline='', encoding="utf-8") as f:
        leitor = csv.DictReader(f) # lê como um dicionario

        for linha in leitor:
            origem = linha["vertice_origem"].strip().lower()
            destino = linha["vertice_destino"].strip().lower()
            peso = float(linha["peso"].strip())
            
            # Garante que os vértices isolados também sejam adicionados
            if destino not in grafo:
                grafo[destino] = []

            # Adiciona a aresta ao grafo ( Origem -> Destino )
            grafo[origem].append((destino, peso))

    return dict(grafo)

# Main para testar as funções 
if __name__ == "__main__":
    #caminho_csv = "../../data/bairros_recife.csv"
    #saida_csv = "../../data/bairros_unique.csv"
    
    caminho_csvBruto = "../../data/dataset_parte2/airlineFlightRoutes.csv"
    saida_csvFiltrado = "../../data/dataset_parte2/csvFiltrado.csv"
    
    dicionario = carregar_lista_adjacencia_parte2(saida_csvFiltrado)
    
    for o, d in list(dicionario.items()):
        print(o, ":", d)

    """
    try:
        filtrar_dataset_2024_e_gerar_csv(caminho_csvBruto, saida_csvFiltrado)
        print("CSV filtrado gerado com sucesso!")

    except Exception as e:
        print("Erro:", e)

    """

import csv
import os
import unicodedata
import re

def normalizar_nome(nome: str) -> str:
    # Remove acentos, espaços extras e transforma em minúsculas
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ASCII", "ignore").decode("utf-8").lower().strip()
    nome = re.sub(r"\s+", " ", nome)  # colapsa espaços internos
    return nome

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

# Main para testar as funções 
if __name__ == "__main__":
    caminho_csv = "../../data/bairros_recife.csv"
    saida_csv = "../../data/bairros_unique.csv"

    try:
        bairros = derreter_bairros_recife(caminho_csv)  # Dicionario
        print(f"Total de bairros únicos: {len(bairros)}\n")

        for i, (bairro, microrregiao) in enumerate(bairros.items()):
            print(f"{bairro} -> {microrregiao}")

    except Exception as e:
        print("Erro:", e)

    salvar_bairros_unique(bairros, saida_csv)
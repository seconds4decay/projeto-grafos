import pandas as pd
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

input_csv = BASE_DIR / "data" / "bairros_recife.csv"

output_bairros_microrregiao = "bairros_unique.csv"

def normalizar_nome(nome: str) -> str:
    if pd.isna(nome):
        return None
    nome = nome.strip().title()
    nome = ''.join(c for c in unicodedata.normalize('NFKD', nome) if not unicodedata.combining(c))
    return nome

df = pd.read_csv(input_csv)

bairros_melted = df.melt(var_name="microrregiao", value_name="bairro").dropna()

bairros_melted["bairro"] = bairros_melted["bairro"].apply(normalizar_nome)

bairros_unique = bairros_melted.drop_duplicates().reset_index(drop=True)

output_path = BASE_DIR / "data" / output_bairros_microrregiao

bairros_unique.to_csv(output_path, index=False)

print(f"Arquivos gerados com sucesso:")
print(f" - {output_bairros_microrregiao} (bairros + microrregião)")
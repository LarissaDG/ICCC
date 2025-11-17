import pandas as pd
import os
import shutil
from IPython.display import Image

csv_path = "/home_cerberus/disk3/larissa.gomide/APDDv2/APDDv2-10023.csv"

# Carregar o dataset corretamente como UTF-8
df = pd.read_csv(csv_path, encoding='ISO-8859-1')

# Tratar a coluna 'Artistic Categories' substituindo '*' por ', '
df["Artistic Categories"] = df["Artistic Categories"].str.replace("*", ", ")

# Garantir que a coluna de filename está correta
df["filename"] = df["filename"].astype(str)

print(df.head())

# Criar uma amostragem estratificada por 'Artistic Categories' e 'Total aesthetic score'
amostra = df.groupby("Artistic Categories").apply(lambda x: x.sample(frac=0.2, random_state=42)).reset_index(drop=True)

# Criar pasta para imagens amostradas
output_dir = "/home_cerberus/disk3/larissa.gomide/"
dataset_path = "/home_cerberus/disk3/larissa.gomide/"
images_output_dir = os.path.join(output_dir, "sampled_images")
os.makedirs(images_output_dir, exist_ok=True)

# Copiar imagens amostradas para a nova pasta
for filename in amostra["filename"]:
    src = os.path.join(dataset_path, filename)
    dst = os.path.join(images_output_dir, filename)
    if os.path.exists(src):
        shutil.copy(src, dst)

# Salvar novo CSV apenas com as amostras
sample_csv_path = os.path.join(output_dir, "sampled_dataset.csv")
amostra.to_csv(sample_csv_path, index=False, encoding='utf-8')

print(f"Amostragem concluída! Imagens copiadas para {images_output_dir} e CSV salvo em {sample_csv_path}.")


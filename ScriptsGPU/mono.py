
#@title Bibliotecas
import os
from PIL import Image
import requests
import pollinations as ai
import uuid
import json
import pandas as pd
import uuid
import multiprocessing 
from multiprocessing import Pool
import time
from diffusers import StableDiffusionPipeline
import torch


#Global variables
max_retries = 10
wait_time = 60

# Configurações
positive_prompts_file = "beauty_prompts"
negative_prompts_file = "ugly_prompts"
models = ["Pollinations", "ShuttleIA", "StableDiffusion", "Midjouney", "DALL-E"]
output_directory = "images"  # A "pastona"
num_workers = 1  # Ajuste conforme o número de núcleos disponíveis

multiprocessing.set_start_method('spawn', force=True)

# modelo StableDiffusion
pipeline = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipeline = pipeline.to("cuda")  # Usar GPU

#Colocar elementos no dicionário
def adicionar_entrada(dicionario, chave, valor):
    dicionario[chave] = valor

# Nome do arquivo
nome_arquivo = "retry.txt"

# Função para escrever o dicionário no arquivo
def salvar_dicionario_em_arquivo(dicionario, arquivo):
    # Garantir que cada entrada seja formatada corretamente como string
    entrada = ", ".join([f"{chave}: {valor}" for chave, valor in dicionario.items()])

    # Abrir o arquivo em modo de adição ("a"), cria o arquivo se não existir
    with open(arquivo, "a") as f:
        f.write(entrada + "\n")  # Adicionar uma nova linha no final

def truncate_prompt(prompt, max_tokens=77):
    return ' '.join(prompt.split()[:max_tokens])

def generate_image(prompt, model_name, output_dir):
    #print(f"Prompt: {prompt}")
    #print(f"Model: {model_name}")
    retry = {}
    #Flag sucesso ou fracasso
    isSucesso = False

    # Criar o diretório do modelo dentro da "pastona"
    model_dir = os.path.join(output_dir, model_name)
    os.makedirs(model_dir, exist_ok=True)

    # Criar ID único para a imagem
    image_id = str(uuid.uuid4())
    file_name = f"{image_id}.jpg"
    image_path = os.path.join(model_dir, file_name)

    for attempt in range(max_retries):
      if isSucesso == False:
        try:
          # Seleção de modelos

          # modelo Pollinations
          if model_name == "Pollinations":
            model_obj = ai.ImageModel()
            image = model_obj.generate(
              prompt=f'{prompt}{ai.flux_realism}',
              model=ai.flux,
              width=1200,
              height=630,
              seed=42
            )
            #Salva a imagem gerada
            try:
              image.save(image_path)
              print(f"Imagem salva em: {image_path}")
              isSucesso = True
              break
            except:
              print("Something went wrong")
              adicionar_entrada(retry,model_name, prompt)
              print(retry)

          elif model_name == "ShuttleIA":
              # Simulação de geração de imagem para o modelo ShuttleIA
              pass

          elif model_name == "StableDiffusion":
              if len(prompt) > 77:
                # Limita o prompt a 77 tokens
                prompt = truncate_prompt(prompt)
                #todo - colocar um aviso sobre isso na tabela

              # Gerar a imagem
              image = pipeline(prompt).images[0]

              #Salva a imagem gerada
              try:
                image.save(image_path)
                print(f"Imagem salva em: {image_path}")
                isSucesso = True
                break
              except:
                print("Something went wrong")
                adicionar_entrada(retry,model_name, prompt)
                print(retry)

          elif model_name == "Midjouney":
              # Simulação de geração de imagem para o modelo Midjourney
              pass

          elif model_name == "DALL-E":
              # Simulação de geração de imagem para o modelo DALL-E
              pass
        except requests.exceptions.ReadTimeout:
          print(f"Timeout occurred. Retrying... (Attempt {attempt + 1}/{max_retries})")
          time.sleep(wait_time)  # Wait before retrying
        except requests.exceptions.RequestException as e:
          print(f"Erro de requisição com o modelo {model_name}: {e}")

    if attempt >= max_retries:
      adicionar_entrada(retry,model_name, prompt)
      print(retry)

    #Salvar o arquivo com os prompts que deram errado
    salvar_dicionario_em_arquivo(retry, nome_arquivo)

    # Confirmar operação
    #print(f"Dados salvos em {nome_arquivo}")

    # Retornar o caminho da imagem e o ID
    return image_path, image_id

# Função auxiliar para processar um único prompt

def process_single_prompt(args):
    prompt, intention, model, output_dir = args
    image_path, image_id = generate_image(prompt, model, output_dir)
    return {
        "image_id": image_id,
        "prompt": prompt,
        "intention": intention,
        "model": model,
        "image_path": image_path,
        "size": "512x512",  # Pode variar
        "style": None  # Pode ser adicionado conforme necessário
    }

# Função principal para processar prompts

def process_prompts(positive_file, negative_file, models, output_dir, num_workers):
    metadata = []  # Para armazenar os metadados das imagens
    total_prompts = 0  # Para contar o número total de prompts (não vazios)

    # Ler arquivos de prompts, ignorando as linhas vazias
    with open(positive_file, "r") as pos_file, open(negative_file, "r") as neg_file:
        # Filtrar as linhas vazias e contar os prompts
        positive_prompts = [line.strip() for line in pos_file if line.strip()]
        negative_prompts = [line.strip() for line in neg_file if line.strip()]

        # Atualizar o número total de prompts
        total_prompts = len(positive_prompts) + len(negative_prompts)

        # Criar a lista de prompts
        prompts = [(line, "positive") for line in positive_prompts] + \
                  [(line, "negative") for line in negative_prompts]

    # Criar uma lista de tarefas (prompt, intenção, modelo, output_dir)
    tasks = [(prompt, intention, model, output_dir) for prompt, intention in prompts for model in models]

    # Processar as tarefas em paralelo
    with Pool(num_workers) as pool:
        metadata = pool.map(process_single_prompt, tasks)

    print(f"Total de prompts processados (não vazios): {total_prompts}")
    return metadata

# Executar o script
if __name__ == "__main__":
    metadata = process_prompts(positive_prompts_file, negative_prompts_file, models, output_directory, num_workers)

    # Salvar os metadados em um arquivo CSV
    metadata_df = pd.DataFrame(metadata)
    metadata_df.to_csv("metadata.csv", index=False)

    print("Processamento concluído. Metadados salvos em 'metadata.csv'.")

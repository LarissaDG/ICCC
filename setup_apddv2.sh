#!/bin/bash

# Script para configurar e executar o pipeline APDDv2

# Carregar módulos necessários
module load python3.10.12
module load cuda/11.8.0  # Ajuste conforme a versão do CUDA no cluster

# Define variáveis
ZIP_URL="https://drive.usercontent.google.com/download?id=1ap5dhuEgpPC5PrJozAu2VFmUNIRZrar2&export=download&authuser=0"
FOLDER_URL="https://drive.google.com/drive/folders/1AOVKmSqZCW09J_Ypr7KzSYfRxQre-w_m"
REPO_URL="https://github.com/BestiVictory/APDDv2.git"
FILE_ID="1ap5dhuEgpPC5PrJozAu2VFmUNIRZrar2"
OUTPUT_ZIP="APDDv2-images.zip"

# Atualizar pip e instalar virtualenv, caso necessário
pip install --upgrade pip virtualenv

# Passo 1: Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando um ambiente virtual..."
    python3 -m venv venv
else
    echo "Ambiente virtual já existe. Pulando esta etapa."
fi
source venv/bin/activate

# Instalar o gdown se não estiver disponível
if ! command -v gdown &> /dev/null
then
    echo "gdown não encontrado. Instalando..."
    pip install gdown
fi

# Passo 2: Baixar imagens e salvar na pasta APDDv2/APDDv2images
echo "Verificando a existência do arquivo zip..."
# Baixar o arquivo zip apenas se ele não existir
echo "Verificando a existência do arquivo zip..."
if [ ! -f "$OUTPUT_ZIP" ]; then
    echo "Baixando o arquivo do Google Drive..."
    gdown --id "$FILE_ID" -O "$OUTPUT_ZIP"
    echo "Download concluído: $OUTPUT_ZIP"
else
    echo "Arquivo zip já existe, pulando download."
fi

# Verificar se o comando unzip está disponível
echo "Verificando a disponibilidade do unzip..."
if ! command -v unzip &> /dev/null
then
    echo "unzip não encontrado. Instalando unzip..."
    sudo apt-get update && sudo apt-get install -y unzip
else
    echo "unzip já está instalado."
fi

# Passo 3: Clonar repositório do GitHub
echo "Verificando a existência do repositório clonado..."
if [ ! -d "APDDv2" ]; then
    echo "Clonando o repositório..."
    git clone "$REPO_URL"
else
    echo "Repositório já existe, pulando clonagem."
fi

# Descompactar o arquivo zip apenas se a pasta não existir
echo "Verificando a existência da pasta descompactada..."
if [ ! -d "images" ]; then
    echo "Descompactando o arquivo zip..."
    unzip OUTPUT_ZIP -d APDDv2images
    echo "Imagens movidas para APDDv2/APDDv2images."
    mv APDDv2images APDDv2
else
    echo "Pasta descompactada já existe, pulando extração."
fi

cd APDDv2 || exit

# Instalar dependências
if [ ! -f "requirements_installed" ]; then
    echo "Instalando dependências..."
    pip3 install -r requirements.txt && touch requirements_installed
else
    echo "Dependências já foram instaladas, pulando esta etapa."
fi

# Baixar todos os arquivos do Google Drive apenas se a pasta não existir
echo "Verificando a existência da pasta de arquivos do Google Drive..."
if [ ! -d "1AOVKmSqZCW09J_Ypr7KzSYfRxQre-w_m" ]; then
    echo "Baixando arquivos do Google Drive..."
    if ! command -v gdown &> /dev/null
    then
        echo "gdown não encontrado. Instalando gdown..."
        pip3 install gdown
    fi
    gdown --folder "$FOLDER_URL"
else
    echo "Arquivos do Google Drive já foram baixados, pulando esta etapa."
fi

# Passo 5: Executar scripts eval.py e demo.py
# Testar no ArtCLIP apenas se eval.py existir
echo "Verificando e executando eval.py..."
if [ -f "eval.py" ]; then
    python eval.py || echo "Erro ao executar eval.py. Verifique as dependências."
else
    echo "eval.py não encontrado, pulando."
fi

# Obter pontuação estética apenas se demo.py existir
echo "Verificando e executando demo.py..."
if [ -f "demo.py" ]; then
    python demo.py || echo "Erro ao executar demo.py. Verifique as dependências."
else
    echo "demo.py não encontrado, pulando."
fi

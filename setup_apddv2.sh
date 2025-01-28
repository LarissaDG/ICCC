#!/bin/bash

# Script para configurar e executar o pipeline APDDv2

# Carregar módulos necessários
#module load python3.10.12
#module load cuda/11.8.0  # Ajuste conforme a versão do CUDA no cluster

# Define variáveis
ZIP_URL="https://drive.usercontent.google.com/download?id=1ap5dhuEgpPC5PrJozAu2VFmUNIRZrar2&export=download&authuser=0"
FOLDER_URL="https://drive.google.com/drive/folders/1AOVKmSqZCW09J_Ypr7KzSYfRxQre-w_m"
REPO_URL="https://github.com/BestiVictory/APDDv2.git"
FILE_ID="1ap5dhuEgpPC5PrJozAu2VFmUNIRZrar2"
OUTPUT_ZIP="APDDv2-images.zip"

# Atualizar pip e instalar virtualenv, caso necessário
pip install --upgrade pip virtualenv

# Passo 1: Criar ambiente virtual, caso não exista
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi
source venv/bin/activate

# Instalar gdown, se necessário
if ! command -v gdown &> /dev/null; then
    echo "gdown não encontrado. Instalando..."
    pip install gdown
fi

# Passo 2: Baixar o arquivo ZIP se não existir
if [ ! -f "$OUTPUT_ZIP" ]; then
    echo "Baixando o arquivo do Google Drive..."
    gdown --id "$FILE_ID" -O "$OUTPUT_ZIP"
fi

# Verificar e instalar unzip, se necessário
if ! command -v unzip &> /dev/null; then
    echo "unzip não encontrado. Instalando..."
    sudo apt-get update && sudo apt-get install -y unzip
fi

# Passo 3: Clonar o repositório do GitHub se não existir
if [ ! -d "APDDv2" ]; then
    echo "Clonando repositório do GitHub..."
    git clone "$REPO_URL"
fi

# Passo 4: Descompactar o arquivo ZIP, se a pasta "images" não existir
if [ ! -d "images" ]; then
    echo "Descompactando o arquivo ZIP..."
    unzip "$OUTPUT_ZIP" -d APDDv2images
    mv APDDv2images APDDv2
fi

cd APDDv2 || exit

# Instalar dependências, se necessário
if [ ! -f "requirements_installed" ]; then
    echo "Instalando dependências..."
    pip install -r requirements.txt && touch requirements_installed
fi

# Passo 5: Baixar arquivos do Google Drive, se a pasta não existir
if [ ! -d "1AOVKmSqZCW09J_Ypr7KzSYfRxQre-w_m" ]; then
    echo "Baixando arquivos do Google Drive..."
    gdown --folder "$FOLDER_URL"
fi

# Passo 6: Comentar a linha antiga e adicionar a nova linha no demo.py
echo "Modificando demo.py para usar o novo arquivo de pesos..."

# Comentar a linha original e adicionar a nova linha usando sed
sed -i 's|score_model = load_model("./modle_weights/1.Score/AesCLIP_reg_weight--e4-train0.4393-test0.6835_best.pth", device)|# score_model = load_model("./modle_weights/1.Score/AesCLIP_reg_weight--e4-train0.4393-test0.6835_best.pth", device)\n    score_model = load_model("./modle_weights/1.Score_reg_weight--e4-train0.4393-test0.6835_best.pth", device)|' demo.py

# Passo 7: Executar eval.py e demo.py, se existirem
if [ -f "eval.py" ]; then
    echo "Executando eval.py..."
    python eval.py || echo "Erro ao executar eval.py."
fi

if [ -f "demo.py" ]; then
    echo "Executando demo.py..."
    python demo.py || echo "Erro ao executar demo.py."
fi

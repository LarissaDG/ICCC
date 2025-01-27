#!/bin/bash

# Define variáveis
REPO_URL="https://github.com/comfyanonymous/ComfyUI.git"
HF_TOKEN="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"  # Substitua pelo seu token Hugging Face

# Clonar o repositório, se não existir
if [ ! -d "ComfyUI" ]; then
    echo "Clonando o repositório..."
    git clone "$REPO_URL"
else
    echo "Repositório já existe. Pulando esta etapa."
fi
cd ComfyUI

# Criar e ativar um ambiente virtual, se não existir
if [ ! -d "venv" ]; then
    echo "Criando um ambiente virtual..."
    python3 -m venv venv
else
    echo "Ambiente virtual já existe. Pulando esta etapa."
fi
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip3 install --upgrade pip  # Garante que o pip está atualizado
pip3 install -r requirements.txt

# Instalar PyTorch para CPU
echo "Instalando PyTorch para CPU..."
pip uninstall -y torch torchvision torchaudio
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu --index-url https://download.pytorch.org/whl/cpu


# Criar diretório de checkpoints, se não existir
if [ ! -d "./models/checkpoints" ]; then
    echo "Criando diretório de checkpoints..."
    mkdir -p ./models/checkpoints/
else
    echo "Diretório de checkpoints já existe. Pulando esta etapa."
fi

# Baixar o modelo, se não existir
MODEL_PATH="./models/checkpoints/v1-5-pruned-emaonly.ckpt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "Baixando o modelo do Hugging Face..."
    wget --header="Authorization: Bearer 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" -O ./models/checkpoints/v1-5-pruned-emaonly.ckpt https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt
    
    # Verificar se o download foi bem-sucedido
    if [ $? -eq 0 ]; then
        echo "Modelo baixado com sucesso!"
    else
        echo "Erro ao baixar o modelo. Verifique seu token ou a conexão com a internet."
        exit 1
    fi
else
    echo "Modelo já existe. Pulando esta etapa."
fi

# Configurar para usar a CPU no ComfyUI
echo "Forçando o uso de CPU no ComfyUI..."
MODEL_MANAGEMENT_FILE="./comfy/model_management.py"

if grep -q "torch.device(torch.cuda.current_device())" "$MODEL_MANAGEMENT_FILE"; then
    sed -i 's/torch.device(torch.cuda.current_device())/torch.device("cpu")/g' "$MODEL_MANAGEMENT_FILE"
    echo "Configuração ajustada para usar CPU."
else
    echo "Configuração para CPU já estava ajustada."
fi

echo "Processo concluído. Iniciando o ComfyUI."
python3 main.py

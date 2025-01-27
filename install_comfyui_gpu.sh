#!/bin/bash

# Carregar módulos necessários
module load python3.10.12
module load cuda/11.8.0  # Ajuste conforme a versão do CUDA no cluster

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

# Atualizar o pip
echo "Atualizando o pip..."
pip3 install --upgrade pip

# Instalar dependências
echo "Instalando dependências..."
pip3 install -r requirements.txt

# Instalar PyTorch com suporte à GPU
echo "Instalando PyTorch com suporte à GPU..."
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

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
    wget --header="Authorization: Bearer $HF_TOKEN" -O "$MODEL_PATH" https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt
    
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

# Configurar para permitir conexões externas no ComfyUI
echo "Configurando o ComfyUI para aceitar conexões externas..."
START_FILE="./main.py"

if ! grep -q "\-\-listen" "$START_FILE"; then
    sed -i '/if __name__ == "__main__":/a \ \ \ \ parser.add_argument("--listen", action="store_true", help="Allow external connections")' "$START_FILE"
    echo "Configuração para '--listen' adicionada."
else
    echo "Configuração para '--listen' já existe."
fi

echo "Processo concluído. Iniciando o ComfyUI com suporte a conexões externas."
python3 main.py --listen

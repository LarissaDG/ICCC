#!/bin/bash
#SBATCH --job-name=ldg-gen-image         # Nome do job
#SBATCH --time=00:20:00                 # Tempo máximo de execução (HH:MM:SS)
#SBATCH --nodes=1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=laladg18@gmail.com

set -x

# Carregar módulos necessários
module load python3.10.12
module load cuda/11.8.0  # Ajuste conforme a versão do CUDA no cluster

# Definir o diretório de cache do Hugging Face
export HF_HOME="/home_cerberus/disk2/larissa.gomide/.cache/huggingface"

# Verificar se o diretório de cache existe, se não, criar
if [ ! -d "$HF_HOME" ]; then
    echo "[PRINT] Creating cache directory at $HF_HOME"
    mkdir -p $HF_HOME
fi
 
if [ -d "/home_cerberus/disk2/larissa.gomide/" ]  
then 
  echo "      [PRINT] /home_cerberus/disk2/larissa.gomide/ exists..." 
 
  if [ -d "/home_cerberus/disk2/larissa.gomide/exp_notebook_venv" ] 
  then 
    echo "      [PRINT] exp_venv exists..." 
 
    source /home_cerberus/disk2/larissa.gomide/exp_notebook_venv/bin/activate 
  else 
    echo "      [PRINT] exp_venv doesnt exists, creating it..." 
 
    python3 -m venv /home_cerberus/disk2/larissa.gomide/exp_notebook_venv/ 
    source /home_cerberus/disk2/larissa.gomide/exp_notebook_venv/bin/activate 
 
  fi 
 
  set -x 
  pwd  
 
  echo "[PRINT] Installing required packages..."
  python3 -m pip install --upgrade pip
  pip install -U diffusers
  pip install torch
  pip install transformers
  pip install accelerate
  pip install --upgrade protobuf sentencepiece
  pip install protobuf==3.20.3
  pip install pandas
  pip install pollinations


  python3 mono.py
 
else 
  echo "      [PRINT] /home_cerberus/disk2/larissa.gomide/ Creating..." 
  mkdir /home_cerberus/disk2/larissa.gomide/ 
  python3 -m venv /home_cerberus/disk2/larissa.gomide/exp_notebook_venv/ 
  source /home_cerberus/disk2/larissa.gomide/exp_notebook_venv/bin/activate 
 
  set -x 
  pwd  
 
  echo "[PRINT] Installing required packages..."
  python3 -m pip install --upgrade pip
  pip install -U diffusers
  pip install torch
  pip install transformers
  pip install accelerate
  pip install --upgrade protobuf sentencepiece
  pip install protobuf==3.20.3
  pip install pandas
  pip install pollinations

  python3 mono.py
fi
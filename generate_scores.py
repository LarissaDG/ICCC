import os
import sys
sys.path.append('/home_cerberus/disk3/larissa.gomide/APDDv2/')
import torch
import numpy as np
import warnings
import models.clip as clip
warnings.filterwarnings("ignore")
from models.aesclip import AesCLIP_reg
from PIL import ImageFile
from PIL import Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
import argparse
import pandas as pd


os.environ['HOME'] = '/scratch/larissa.gomide/minha_home/'
os.environ['TRANSFORMERS_CACHE'] = "/scratch/larissa.gomide/minha_home/.cache/huggingface"
os.environ['CLIP_CACHE'] = "/scratch/larissa.gomide/minha_home/.cache/clip"
os.environ['HF_HOME'] = "/scratch/larissa.gomide/minha_home/.cache/huggingface"
os.environ['XDG_CACHE_HOME'] = "/scratch/larissa.gomide/minha_home/.cache"
os.environ['MPLCONFIGDIR'] = '/scratch/larissa.gomide/minha_home/.matplotlib'

def init():
    parser = argparse.ArgumentParser(description="PyTorch Aesthetic Scoring")
    args = parser.parse_args()
    return args

opt = init()

def get_score(opt, y_pred):
    """
    Retorna a predição do modelo e seu valor numérico em numpy.
    """
    score_np = y_pred.data.cpu().numpy()
    return y_pred, score_np

def load_model(weight_path, device):
    """
    Tenta carregar o modelo AesCLIP_reg a partir do caminho do peso.
    Em caso de falha, exibe uma mensagem e retorna None.
    """
    try:
        # O peso base do AesCLIP é fixo
        base_weight = "/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/0.AesCLIP_weight--e11-train2.4314-test4.0253_best.pth"
        model = AesCLIP_reg(clip_name='ViT-B/16', weight=base_weight)
        model.load_state_dict(torch.load(weight_path))
        model.to(device)
        model.eval()
        print(f"Modelo carregado com sucesso: {weight_path}")
        return model
    except Exception as e:
        print(f"Falha ao carregar modelo de {weight_path}: {e}")
        return None

def evaluate_image(image_path, models_dict, preprocess, opt, device):
    """
    Dada uma imagem (caminho) e um dicionário de modelos,
    processa a imagem com o preprocess do CLIP e retorna um dicionário
    com os scores para cada métrica.
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Erro ao abrir imagem {image_path}: {e}")
        return {col: np.nan for col in models_dict.keys()}
    
    try:
        image_input = preprocess(image).unsqueeze(0).to(device)
    except Exception as e:
        print(f"Erro ao preprocessar imagem {image_path}: {e}")
        return {col: np.nan for col in models_dict.keys()}
    
    scores = {}
    for col, model in models_dict.items():
        if model is not None:
            try:
                pred = model(image_input)
                _, pred_val = get_score(opt, pred)
                # Se for um único valor, extraí-lo
                if isinstance(pred_val, np.ndarray) and pred_val.size == 1:
                    pred_val = pred_val.item()
                # Ajuste especial para o score total (multiplica por 10)
                if col == "Total aesthetic score":
                    pred_val = pred_val * 10
                scores[col] = pred_val
            except Exception as e:
                print(f"Erro ao prever {col} para imagem {image_path}: {e}")
                scores[col] = np.nan
        else:
            scores[col] = np.nan
    return scores

def process_csv(input_csv, output_csv, models_dict, preprocess, opt, device, cols_to_compare):
    """
    Abre o CSV com encoding 'utf-8' (ou 'latin1' em caso de falha), 
    para cada linha avalia a imagem (caminho presente em 'generated_filename')
    e preenche as colunas de comparação com os scores retornados pelos modelos.
    Ao final, salva a tabela atualizada no arquivo de saída.
    """
    try:
        df = pd.read_csv(input_csv, encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler {input_csv} com utf-8: {e}. Tentando latin1...")
        df = pd.read_csv(input_csv, encoding="latin1")
    
    for idx, row in df.iterrows():
        image_path = row.get("generated_filename")
        if not image_path or not os.path.exists(image_path):
            print(f"Imagem não encontrada para a linha {idx}: {image_path}")
            for col in cols_to_compare:
                df.loc[idx, col] = np.nan
            continue
        
        scores = evaluate_image(image_path, models_dict, preprocess, opt, device)
        for col in cols_to_compare:
            df.loc[idx, col] = scores.get(col, np.nan)
        print(f"Linha {idx} processada.")
    
    df.to_csv(output_csv, index=False)
    print(f"Arquivo salvo: {output_csv}")

def main():
    # Define o dispositivo
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # Carrega o preprocess do CLIP (ViT-B/16)
    _, preprocess = clip.load('ViT-B/16', device)
    
    # Carrega os modelos com try/except (não interrompe a execução em caso de falha)
    score_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/1.Score_reg_weight--e4-train0.4393-test0.6835_best.pth", device)
    theme_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/2.Theme and logic_reg_weight--e5-train0.3792-test0.5953_best.pth", device)
    creativity_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/3.Creativity_reg_weight--e5-train0.4212-test0.7122_best.pth", device)
    layout_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/4.Layout and composition_reg_weight--e6-train0.2783-test0.6342_best.pth", device)
    space_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/5.Space and perspective_reg_weight--e7-train0.2168-test0.5998_best.pth", device)
    # O modelo 6 (Sense of Order) foi renomeado para Model_6.pth
    sense_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/Model_6.pth", device)
    light_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/7.Light and shadow_reg_weight--e7-train0.1937-test0.6518_best.pth", device)
    color_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/8.Color_reg_weight--e5-train0.2905-test0.5871_best.pth", device)
    details_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/9.Details and texture_reg_weight--e4-train0.4385-test0.7034_best.pth", device)
    overall_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/10.The overall_reg_weight--e3-train0.5131-test0.6343_best.pth", device)
    mood_model = load_model("/home_cerberus/disk3/larissa.gomide/APDDv2/modle_weights/11.Mood_reg_weight--e7-train0.3108-test0.7097_best.pth", device)
    
    # Mapeia os modelos para os nomes das colunas a serem preenchidas
    cols_to_compare = [
        "Total aesthetic score", "Theme and logic", "Creativity", "Layout and composition",
        "Space and perspective", "The sense of order", "Light and shadow", "Color",
        "Details and texture", "The overall", "Mood"
    ]
    models_dict = {
        "Total aesthetic score": score_model,
        "Theme and logic": theme_model,
        "Creativity": creativity_model,
        "Layout and composition": layout_model,
        "Space and perspective": space_model,
        "The sense of order": sense_model,
        "Light and shadow": light_model,
        "Color": color_model,
        "Details and texture": details_model,
        "The overall": overall_model,
        "Mood": mood_model
    }
    
    # Processa a tabela SMALL
    input_csv_small = "/home_cerberus/disk3/larissa.gomide/oficial/amostraGauss/sampled_SMALL_with_gen.csv"
    output_csv_small = "/home_cerberus/disk3/larissa.gomide/oficial/amostraGauss/sampled_SMALL_with_gen_scored.csv"
    print("Processando tabela SMALL...")
    process_csv(input_csv_small, output_csv_small, models_dict, preprocess, opt, device, cols_to_compare)
    
    # Processa a tabela BIG
    input_csv_big = "/home_cerberus/disk3/larissa.gomide/oficial/amostraGauss/sampled_BIG_with_gen.csv"
    output_csv_big = "/home_cerberus/disk3/larissa.gomide/oficial/amostraGauss/sampled_BIG_with_gen_scored.csv"
    print("Processando tabela BIG...")
    process_csv(input_csv_big, output_csv_big, models_dict, preprocess, opt, device, cols_to_compare)

if __name__ == "__main__":
    main()


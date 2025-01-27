from diffusers import StableDiffusionPipeline
import torch

# Inicializar o modelo
pipeline = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipeline = pipeline.to("cuda")  # Usar GPU

# Configurações do prompt e parâmetros
#prompt = "A beautiful landscape with mountains and a clear blue sky"
prompt = "An ugly woman"
output_path = "generated_image.png"

# Gerar a imagem
image = pipeline(prompt).images[0]

# Salvar a imagem
image.save(output_path)
print(f"Imagem salva em: {output_path}")
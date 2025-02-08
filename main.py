from fastapi import FastAPI, HTTPException
import requests
from PIL import Image
from io import BytesIO
import os

# Configurar o Client ID do Imgur (use variável de ambiente no Render)
CLIENT_ID = "63b37faba7aabcb"

# Criar a API
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "The split_Image API is online!"}

# Função para validar a URL da imagem
async def is_valid_url(url: str) -> bool:
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        return response.status_code == 200
    except requests.RequestException:
        return False

# Rota para processar a imagem
@app.get("/process-image/")
async def process_image(img_url: str):
    # Validar URL da imagem
    if not is_valid_url(img_url):
        raise HTTPException(status_code=400, detail="URL da imagem inválida ou inacessível.")

    # Baixar a imagem
    response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
    img = Image.open(BytesIO(response.content))

    # Verificar se a imagem é válida
    if img.format not in ["JPEG", "PNG", "GIF"]:
        raise HTTPException(status_code=415, detail="Formato de imagem não suportado. Apenas JPEG, PNG e GIF são aceitos.")

    # Definir coordenadas dos recortes
    boxes = [
        (40, 40, 900, 900),
        (940, 40, 1800, 900),
        (40, 940, 900, 1800),
        (940, 940, 1800, 1800)
    ]

    imgur_links = []

    for i, box in enumerate(boxes):
        recorte = img.crop(box)
        file_name = f"recorte_{i+1}.png"
        recorte.save(file_name)

        # Upload para Imgur
        with open(file_name, "rb") as f:
            response = requests.post(
                "https://api.imgur.com/3/upload",
                headers={"Authorization": f"Client-ID {CLIENT_ID}"},
                files={"image": f}
            )

        if response.status_code == 200:
            imgur_links.append(response.json()["data"]["link"])
        else:
            imgur_links.append(f"Erro no upload: {response.json().get('data', {}).get('error', 'Desconhecido')}")

        # Remover o arquivo local
        os.remove(file_name)

    return {"imgur_links": imgur_links}

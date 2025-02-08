from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from PIL import Image
from io import BytesIO
import os

# Configurar o Client ID do Imgur
CLIENT_ID = "63b37faba7aabcb"

# Criar a API com FastAPI
app = FastAPI()

# Modelo de entrada (recebe a URL da imagem)
class ImageRequest(BaseModel):
    img_url: str

# Rota para processar a imagem
@app.post("/process-image/")
def process_image(request: ImageRequest):
    try:
        # Baixar a imagem
        response = requests.get(request.img_url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(response.content))

        # Definir coordenadas dos recortes
        boxes = [
            (40, 40, 900, 900),
            (940, 40, 1800, 900),
            (40, 940, 900, 1800),
            (940, 940, 1800, 1800)
        ]

        imgur_links = []

        # Processar e enviar para o Imgur
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

            # Verificar resposta do Imgur
            if response.status_code == 200:
                imgur_links.append(response.json()["data"]["link"])
            else:
                imgur_links.append("Erro no upload")

            # Remover o arquivo local
            os.remove(file_name)

        return {"imgur_links": imgur_links}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

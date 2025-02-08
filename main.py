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

async def process_image(img_url, q):
        # Baixar a imagem
        response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(response.content))

        # Definir coordenadas dos recortes
        boxes = [
            (40, 40, 900, 900),
            (940, 40, 1800, 900),
            (40, 940, 900, 1800),
            (940, 940, 1800, 1800)
        ]

        recorte = img.crop(boxes[q-1])
        file_name = "temp.png"
        recorte.save(file_name)
        response = requests.post(
                    "https://api.imgur.com/3/image",
                    headers={"Authorization": "Client-ID 63b37faba7aabcb"},
                    files={"image": open(file_name, "rb")}
                )

        return {"imgur_link": response.json()["data"]["link"]}

from fastapi import FastAPI, HTTPException
import requests
from PIL import Image
from io import BytesIO
import os

# Carregar o CLIENT_ID a partir de variáveis de ambiente
CLIENT_ID = "63b37faba7aabcb"

# Criar a API
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "The split_Image API is online!"}

@app.get("/process-image")
async def process_image(img_url: str, q: int):
    # Validar que q está dentro do intervalo esperado
    if q not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="O valor de 'q' deve ser entre 1 e 4.")

    # Baixar a imagem
    response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao baixar a imagem.")
    
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

    # Upload da imagem para o Imgur
    with open(file_name, "rb") as img_file:
        response = requests.post(
            "https://api.imgur.com/3/image",
            headers={"Authorization": f"Client-ID {CLIENT_ID}"},
            files={"image": img_file}
        )
    
    # Verificar se a resposta é válida e está em formato JSON
    try:
        response_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Erro ao processar a resposta do Imgur. A resposta não é JSON.")

    # Verificar se o upload foi bem-sucedido
    if response.status_code != 200 or "data" not in response_data or "link" not in response_data["data"]:
        raise HTTPException(status_code=500, detail="Erro ao enviar a imagem para o Imgur.")

    # Retornar o link da imagem no Imgur
    return {"imgur_link": response_data["data"]["link"]}

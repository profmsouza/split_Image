from fastapi import FastAPI, HTTPException
import requests
from PIL import Image
from io import BytesIO
import os

# Configurar o Client ID do Imgur (use variável de ambiente no Render)
CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

# Criar a API
app = FastAPI()

# Rota para processar a imagem
@app.get("/process-image/")
def process_image(img_url: str):
    try:
        # Baixar a imagem
        response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Erro ao baixar a imagem. Status: {response.status_code}")
        
        img = Image.open(BytesIO(response.content))

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
                upload_response = requests.post(
                    "https://api.imgur.com/3/upload",
                    headers={"Authorization": f"Client-ID {CLIENT_ID}"},
                    files={"image": f}
                )

            # Verificar a resposta do Imgur
            if upload_response.status_code == 200:
                imgur_links.append(upload_response.json()["data"]["link"])
            else:
                # Detalhes do erro de upload
                error_message = upload_response.json().get('data', {}).get('error', 'Erro desconhecido')
                imgur_links.append(f"Erro no upload: {error_message}")

            # Remover o arquivo local
            os.remove(file_name)

        return {"imgur_links": imgur_links}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os
import base64
from io import BytesIO
import json
from fastapi.responses import StreamingResponse
import requests
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Response, status, Form
from pydantic import BaseModel
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()


FOTOR_API_KEY= os.getenv("FOTOR_API_KEY")
MAX_STUDIO_KEY=os.getenv("MAX_STUDIO_KEY")

# Static Dictionaries
text2img_style=[{'name': 'B&W', 'id': '88c4c378-6566-4a24-9450-072b1d6f9576', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/r64xy6aat3uh.jpg'}, {'name': 'Oil Painting', 'id': '2ffc5f83d4574cefa59638cda871c834', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/5xtz576shzbc.png'}, {'name': 'Ukiyo-e', 'id': '818d8d769c54473ca4342ac36ace9777', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/yp1sv9c8wnrw.png'}, {'name': '3D', 'id': 'aea8b4f46e0d46a3b3ef96204979c022', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/rsrqpf7v3mst.jpg'}, {'name': 'Art Nouveau', 'id': 'b6cbf0311d9948f6941bca1866302b4f', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/lqlyhvw0ruf3.png'}, {'name': 'Japanese Anime', 'id': 'eb4afa5c4e7f41d79c391569d7affacb', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/u9nrit40xnof.jpg'}, {'name': 'Photography 1', 'id': '69fbd669d434418b9c1414f9476f50e1', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/069ez4479xcq.jpg'}, {'name': 'Anime illustration', 'id': '73d53e3c-e1b7-4b8b-9f01-36376879a170', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/06z591khfqc6.png'}, {'name': 'Psychedelic Pop', 'id': '70107397b1a24ad38f0c731e4d519018', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/5fmglknanjdd.png'}, {'name': "90's Anime", 'id': '0a8f1974-413f-4f00-bcfb-2c40a0108ce2', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/tzp1i5oadijn.jpg'}, {'name': 'Line Drawing', 'id': 'e582391f-7ab5-4cb0-add9-e275d040f50d', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/djk0z2qnhwj9.jpg'}, {'name': 'None', 'id': 'bb43a4fa-105c-444a-9485-2707e147a538', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/2cjnfm01sgbw.jpg'}, {'name': 'Cartoon', 'id': 'efd34eb3-7eeb-4fa2-8f92-1c007601ad26', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/4plcywnt9s7t.jpg'}, {'name': 'Photography 3', 'id': 'fb635fa3-e2fd-4f59-99e1-318d01e078e4', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/5a61d47x6r1c.jpg'}, {'name': 'Digital Art', 'id': 'b350e73e-9092-4ac6-8455-f1a199634e79', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/rskwaasqq9se.jpg'}, {'name': 'Photography 2', 'id': 'b082c8ee-ceb5-4e15-8acd-0c3af3c5fccb', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/209ap64t1rlg.jpg'}, {'name': 'Art Oils', 'id': '8de6450e-781f-4331-abf6-3abef3418dc6', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/tlzz7y7pjrws.jpg'}, {'name': 'Tee Printing', 'id': 'c1dd6e9f-d573-450d-b083-98fdc8e88ddd', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/ni49174se7yt.jpg'}, {'name': 'Cinematic', 'id': '14f570be-29d4-451a-ba72-39f92e324b9c', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/uhgtz698jloy.jpg'}, {'name': 'Neonpunk', 'id': '4ec158a3-737d-42ce-9742-6f9f199ed024', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/yqhk8jzwnowa.jpg'}, {'name': 'None', 'id': '3d546352-4d28-4f27-addf-9063649d4765', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/zuxg4ixfu40p.jpg'}, {'name': 'Pixel Art', 'id': 'c9aedf8f-4ddb-48b1-b98e-e959f6c9e9df', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/teauo5you13o.jpg'}, {'name': 'Logo', 'id': '6fd123ec-ac32-4146-9adf-b6264f128ac3', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/bs1c9fat0rn4.jpg'}, {'name': '3D Cartoon', 'id': '42c9a54f-8964-4f49-b741-f403d921f2ba', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/7bt4cdqmqcqo.jpg'}, {'name': 'Color Manga', 'id': 'e81a863f-c093-4a9c-bc8d-60b9b85f42b3', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/8osa2ndgux1h.jpg'}, {'name': 'Anime', 'id': '99d61f0e-f6c8-4769-9f4c-e2276c16970c', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/bij6jpquh9ug.jpg'}, {'name': 'Psychedelic', 'id': '49cc4c28-22bc-42fa-ab6b-2c392185c2b2', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/185w5i9s26er.jpg'}, {'name': 'Colored Pencil Drawing', 'id': 'e65e33dd-0d1a-4966-af06-1db3738017d1', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/i7rol6bmvxio.jpg'}, {'name': 'Chinese Ink Painting', 'id': '7aed6f1a-adc7-4e2a-9394-48e5db36e27e', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/cva58ri9o55i.jpg'}, {'name': 'Icon', 'id': 'e7f792c0-a952-407e-83f1-069dd63d6e45', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/13b0d1pplfpp.jpg'}, {'name': 'Chinese Illustration', 'id': '60f20609-8e0e-49e3-89a8-2d3b4b30ebc6', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/k1tkfjdvevf1.jpg'}, {'name': 'Acrylic Painting', 'id': '5b860185-656d-4c2a-88b7-f6041f4908bb', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/j2ubca96rmfs.jpg'}, {'name': 'Tattoo Art', 'id': '7b3b1f40-60b0-41df-8280-238baae78c38', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/p2txcn2de3yk.jpg'}, {'name': 'B&W Tattoo', 'id': 'bd60f732-0b41-4346-84f1-b411549c6633', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/mic9qc9crbw1.jpg'}, {'name': 'Halloween Art', 'id': '47fca709-f279-4f94-a612-1a39660ba7f6', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/h68y2ogwkxuo.jpg'}, {'name': 'Creepy Tattoo', 'id': 'e7786560-1654-4bec-a325-44954bc5c3fc', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/5jbzm11nh5a1.jpg'}, {'name': 'Photography 4', 'id': '6b8d16cf-9402-4c22-b1e8-39eccce3436b', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/2ip1trb5vwt2.jpg'}, {'name': 'Tattoo (Legacy)', 'id': '2663381b-b446-496e-b044-2e3e5fa6a02e', 'image_url': 'https://pub-static.fotor.com/assets/aiImageConfig/template/h9cpi98sa41p.jpg'}]

# Pydantic Models
class ArtEffect(BaseModel):
    template_id : Optional[str] = "ca39d44f-e8c8-4a3e-9d09-c3f96cb2fe60"

class Text2ImgBaseModel(BaseModel):
    prompt: str
    size: Optional[float] = 1.1
    template_id: Optional[str] = "bb43a4fa-105c-444a-9485-2707e147a538"
    negative_prompt: Optional[str] = "Generate Image using of given Prompt"

class AgeChanger(BaseModel):
    age: Optional[str] = "baby"

# APIS
@app.get("/")
def index():
    return {"message": "Running Well"}

@app.post("/age/changer/")
async def age_changer(file: UploadFile = File(...), age: str = Form(...)):
    try:
        file_const = await file.read()
        image_base64 = base64.b64encode(file_const).decode("utf-8")
        payload = {
            'image': image_base64,
            'age': age,
        }
        response = requests.post(
            'https://api.maxstudio.ai/age-changer',
            headers={
                'x-api-key': MAX_STUDIO_KEY,
                'Content-Type': 'application/json'
            },
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print('Request Error:', str(error))
        return {"error": "Failed to connect to age changer API"}
    except Exception as error:
        print('Error:', str(error))
        return {"error": str(error)}



@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    url = f"https://api.maxstudio.ai/age-changer/{job_id}"
    try:
        response = requests.get(url, headers={'x-api-key': MAX_STUDIO_KEY})
        response.raise_for_status()
        data = response.json()
        if data["status"] not in ["failed", "not-found", "completed"]:
            return Response(status_code=status.HTTP_102_PROCESSING)
        if data["status"] == "completed":
            # Decode the Base64 string
            # Decode Base64
            image_bytes = base64.b64decode(data.get("result"))
            # Create an in-memory file
            image_stream = BytesIO(image_bytes)
            # Return image as response
            # return StreamingResponse(image_stream, media_type="image/jpeg")
            return data
    except requests.exceptions.RequestException as error:
        print('Request Error:', str(error))
        return {"error": "Failed to connect to age changer API"}
    except Exception as error:
        print('Error:', str(error))
        return {"error": str(error)}

@app.get("/text/img/style")
def text_2_img_style():
    return text2img_style

@app.post("/text/img")
def text_2_img(text_request: Text2ImgBaseModel):
    size = text_request.size
    template_id = text_request.template_id
    negative_prompt = text_request.negative_prompt
    try:
        prompt = text_request.prompt
        url = "https://api-b.fotor.com/v1/aiart/text2img"

        payload = json.dumps({
        "content": prompt,
        "sizeId": "6361e03bc09cb851c66328a4",
        "templateId": template_id,
        "negativePrompt": negative_prompt,
        })
        headers = {
        'Authorization': f'Bearer {FOTOR_API_KEY}',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print('Request Error:', str(error))
        return {"error": "Failed to connect to age changer API"}
    except Exception as error:
        print('Error:', str(error))
        return {"error": str(error)}

@app.post('/art/effect/')
async def ai_art_effect(file: UploadFile):
    try:
        url = "https://api-b.fotor.com/v1/aiart/img2img"

        file_cont = await file.read()

        payload = {
        "templateId": "b485f845-76ed-44b2-b1c5-1abd1e061259",
        "negativePrompt": "",
        "userImageUrl": file_cont,
        "strength": 0.5,
        "format": "jpg"
        }
        headers = {
        'Authorization': f'Bearer {FOTOR_API_KEY}',
        'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print('Request Error:', str(error))
        return {"error": "Failed to connect to age changer API"}
    except Exception as error:
        print('Error:', str(error))
        return {"error": str(error)}

@app.get("/task/{task_id}")
def get_task(task_id: str):
    url = f"https://api-b.fotor.com/v1/aiart/tasks/{task_id}/"

    headers = {
    'Authorization': f'Bearer {FOTOR_API_KEY}'
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)
    return response.json()
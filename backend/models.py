import os
import requests
from typing import Dict
from dotenv import load_dotenv  # Import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_URL = "https://api-inference.huggingface.co/models/naver-clova-ix/donut-base"
HF_API_KEY = os.environ.get('HF_API_KEY')

def query_donut(image_base64: str) -> Dict:
    """Sends an image to Hugging Face's Donut model and retrieves structured text."""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"image": image_base64}
        )
        return response.json()
    except Exception as e:
        print(f"Error querying Donut model: {str(e)}")
        return {"text": ""}
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình ứng dụng
UPLOAD_FOLDER = 'static/uploads/original/'
PROCESSED_FOLDER = 'static/uploads/processed/'
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Cấu hình mô hình Gemini
GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = {
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
}
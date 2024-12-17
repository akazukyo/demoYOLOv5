import pytesseract
import cv2
import re
import urllib.parse
from PIL import Image
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def ocr_image(cropped_img):
    text = pytesseract.image_to_string(cropped_img, config='--psm 13')
    return clean_ndc_code(text)

def clean_text(text):
    if not text:
        return ''
    text = text.replace('\r', '').replace('\t', ' ')
    cleaned_text = re.sub(r'\bNDC\b\s*', '', text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def clean_ndc_code(ndc_code):
    if not ndc_code:
        return ''
    ndc_code = ndc_code.strip()
    ndc_code = re.sub(r'[\r\n]', '', ndc_code)
    ndc_code = re.sub(r'\bNDC\b\s*', '', ndc_code, flags=re.IGNORECASE)
    ndc_code = re.sub(r'[^0-9\-]', '', ndc_code)
    return urllib.parse.quote(ndc_code)
import os
import torch
import cv2
from flask import Flask, request, render_template
from PIL import Image
from config import UPLOAD_FOLDER, PROCESSED_FOLDER
from image_processing import ocr_image
from api_interaction import fetch_drug_info_from_openfda
from data_processing import validate_and_normalize_ndc


import pytesseract
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['PROCESSED_FOLDER']):
    os.makedirs(app.config['PROCESSED_FOLDER'])

try:
    modelYolov5s = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)
    modelYolov5s.conf = 0.5
except Exception as e:
    print(f"Error loading YOLOv5 model: {e}")
    modelYolov5s = None



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    error_message = None
    drug_info = None
    original_file_path = None
    image_path = None 
    if request.method == 'POST':
        search_value = request.form.get('search')
        if search_value and re.match(r'^\d{3,5}-\d{2,4}-\d{1,2}$', search_value):
            drug_info = fetch_drug_info_from_openfda(ndc_code=search_value)
            if not drug_info:
                error_message = "No drug information found for this NDC code."
            return render_template('result.html', drug_info=drug_info, error_message=error_message, yolo_image_path=image_path)

        if 'file' not in request.files:
            error_message = 'No files selected!'
            return render_template('index.html', error_message=error_message)

        file = request.files['file']
        if file.filename == '':
            error_message = 'No file selected for upload!'
            return render_template('index.html', error_message=error_message)

        if file:
            try:
                img = Image.open(file)
                ocr_text = pytesseract.image_to_string(img)
                # if not ocr_text.strip():
                #     img = img.rotate(180, expand=True)

                original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                img.save(original_file_path)
                image_path = original_file_path

                clean_file_name = os.path.splitext(file.filename)[0]
                processed_subfolder = os.path.join(app.config['PROCESSED_FOLDER'], clean_file_name)

                if not os.path.exists(processed_subfolder):
                    os.makedirs(processed_subfolder)

                if modelYolov5s:
                    results = modelYolov5s(original_file_path)
                    results.render()

                    for i, img_with_boxes in enumerate(results.ims):
                        yolov5_output_path = os.path.join(processed_subfolder, f'{clean_file_name}_yolov5_output_{i}.jpg')
                        img_bgr = cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(yolov5_output_path, img_bgr)

                    image_path = yolov5_output_path
                    boxes = results.xyxy[0].cpu().numpy()
                    img = cv2.imread(original_file_path)

                    drug_name_text = ''
                    package_ndc_text = ''

                    if len(boxes) == 0:
                        error_message = "No object recognized from the image."
                    else:
                        for i, box in enumerate(boxes):
                            x_min, y_min, x_max, y_max, conf, class_id = map(int, box)
                            cropped_img = img[y_min:y_max, x_min:x_max]
                            recognized_text = ocr_image(cropped_img)

                            if class_id == 0:
                                drug_name_text = recognized_text
                            elif class_id == 1:
                                package_ndc_text = recognized_text

                            cropped_image_path = os.path.join(processed_subfolder, f'cropped_{i}.jpg')
                            success = cv2.imwrite(cropped_image_path, cropped_img)
                            if not success:
                                print(f"Failed to save cropped image to: {cropped_image_path}")

                    if package_ndc_text:
                        drug_info = fetch_drug_info_from_openfda(ndc_code=validate_and_normalize_ndc(package_ndc_text), brand_name=drug_name_text)
                        if not drug_info:
                            error_message = "No drug information found for this NDC code."
                    else:

                        image_path = original_file_path
                        error_message = "No NDC package recognized from the image."
                    
                    if not drug_info and not error_message:
                        error_message = "Unable to process data."

            except Exception as e:
                error_message = f"Error processing image: {e}"

        return render_template('result.html', drug_info=drug_info, error_message=error_message, yolo_image_path=image_path)

    return render_template('index.html', error_message=error_message)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER']) 
    app.run(debug=True)
import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO
import os
import glob
import json
import time
from shutil import move

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

ocr = PaddleOCR(use_angle_cls=True, lang='en')  # need to run only once to download and load model into memory
model = YOLO("best.pt")

input_folder =  r"C:\Users\USER\OneDrive\Documents\aqua\input images"
processed_folder = 'processed_images'
predictions_folder = 'runs/detect/'

if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

labels = {
    0: 'Discount_Percentage', 1: 'Due_Date', 2: 'Email_Client', 3: 'Name_Client', 4: 'Products', 
    5: 'Remise', 6: 'Subtotal', 7: 'Tax', 8: 'Tax_Precentage', 9: 'Tel_Client', 
    10: 'billing address', 11: 'invoice date', 12: 'invoice number', 13: 'shipping address', 14: 'total'
}

def process_image(image_path):
    model.predict(image_path, save=True, conf=0.25, save_conf=True, save_txt=True)
    
    # Find all folders that match the naming pattern 'predict*'
    folders = glob.glob(os.path.join(predictions_folder, 'predict*'))
    
    # If any folder is found, sort them based on their modification time to get the latest one
    if folders:
        latest_folder = max(folders, key=os.path.getmtime)  # Get the most recent folder
        print(f"Latest prediction folder: {latest_folder}")
    else:
        print("No prediction folders found.")
        return
    
    labels_path = os.path.join(latest_folder, 'labels')
    # Find all txt files in the labels directory
    txt_files = glob.glob(os.path.join(labels_path, '*.txt'))
    
    results = {}
    
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Each line in the txt file corresponds to a detected object
                # Assuming the format is: class x_center y_center width height confidence
                parts = line.strip().split()
                if len(parts) == 6:
                    class_id, x_center, y_center, width, height, confidence = map(float, parts)
                    class_id = int(class_id)  # Convert class_id to integer
                    
                    # Load the original image
                    img = cv2.imread(image_path)
                    img_height, img_width, _ = img.shape
                    
                    # Calculate the bounding box coordinates
                    x_min = int((x_center - width / 2) * img_width)
                    y_min = int((y_center - height / 2) * img_height)
                    x_max = int((x_center + width / 2) * img_width)
                    y_max = int((y_center + height / 2) * img_height)
                    
                    # Crop the detected object from the image
                    cropped_img = img[y_min:y_max, x_min:x_max]
                    
                    # Use PaddleOCR to extract text from the cropped image
                    ocr_result = ocr.ocr(cropped_img, cls=True)
                    
                    # Extract only the text from the OCR result
                    extracted_text = [item[1][0] for item in ocr_result[0]] if ocr_result and ocr_result[0] else "No text found"
                    
                    # Get the label for the class_id
                    label = labels.get(class_id, "Unknown")
                    
                    # Add the extracted text to the results dictionary
                    results[label] = extracted_text
    
    # Print the results in JSON format
    print(json.dumps(results, indent=4))

while True:
    # Get all image files in the input folder
    image_files = glob.glob(os.path.join(input_folder, '*.jpg'))
    
    if not image_files:
        print("No images found. Waiting for images...")
        time.sleep(5)
        continue
    
    for image_file in image_files:
        process_image(image_file)
        # Move the processed image to the processed folder
        move(image_file, os.path.join(processed_folder, os.path.basename(image_file)))
    
    # Sleep for a short period before checking for new images again
    time.sleep(5)
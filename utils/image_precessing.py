import cv2
import numpy as np
from PIL import Image

def process_image(image):
    img = Image.open(image)
    img = np.array(img)
    
    img = cv2.resize(img, (224, 224))  
    
    img = img / 255.0
    
    return img

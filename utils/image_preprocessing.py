import pytesseract
from PIL import Image
from torchvision.transforms import functional as F
from torchvision.models.detection import fasterrcnn_resnet50_fpn
import torch

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def detect_objects(image_path):
    # Carregar o modelo pré-treinado
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    # Carregar e preparar a imagem
    image = Image.open(image_path)
    image_tensor = F.to_tensor(image).unsqueeze(0)

    # Detecção de objetos
    with torch.no_grad():
        predictions = model(image_tensor)

    # Processar e retornar os resultados
    boxes = predictions[0]['boxes']
    labels = predictions[0]['labels']
    scores = predictions[0]['scores']

    return boxes, labels, scores

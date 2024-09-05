import pytesseract
from PIL import Image
from torchvision.transforms import functional as F
from torchvision.models.detection import fasterrcnn_resnet50_fpn
import torch

def extract_text_from_image(image_path):
    # Abrir a imagem e garantir que está em RGB
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Usar pytesseract para extrair texto
    text = pytesseract.image_to_string(image)
    return text

def detect_objects(image_path):
    # Carregar o modelo pré-treinado no COCO dataset
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    # Carregar e preparar a imagem
    image = Image.open(image_path)
    
    # Converter a imagem para RGB se necessário
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Transformar a imagem em tensor e adicionar uma dimensão extra
    image_tensor = F.to_tensor(image).unsqueeze(0)

    # Realizar a detecção de objetos
    with torch.no_grad():
        predictions = model(image_tensor)

    # Processar e retornar os resultados
    boxes = predictions[0]['boxes'].cpu().numpy()
    labels = predictions[0]['labels'].cpu().numpy()
    scores = predictions[0]['scores'].cpu().numpy()

    return boxes, labels, scores

import io
from PIL import Image
import torch
from torchvision import models, transforms

# Configuração do modelo pré-treinado
model = models.resnet18(pretrained=True)
model.eval()

# Transformação para pré-processar a imagem
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def process_image(screenshot):
    """
    Processa a imagem usando o modelo de visão computacional pré-treinado.
    """
    # Ler a imagem do arquivo
    image = Image.open(io.BytesIO(screenshot.read()))
    # Pré-processar a imagem
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)
    
    with torch.no_grad():
        output = model(input_batch)
    
    # Obter a classe prevista
    _, predicted_class = torch.max(output, 1)
    
    # Mapeamento de classes para uma descrição
    class_descriptions = {
        0: "Class 0 Description",
        1: "Class 1 Description",
        # Adicione outras classes conforme necessário
    }
    
    class_label = predicted_class.item()
    description = class_descriptions.get(class_label, "Unknown")
    
    return description

def generate_test_cases(processed_image, description):
    """
    Gera casos de teste baseados na descrição da imagem e na descrição fornecida.
    """
    return [
        f"Test Case 1: Verify that the image is categorized as '{processed_image}' with the description '{description}'.",
        f"Test Case 2: Ensure the feature described as '{description}' is displayed correctly for the '{processed_image}' category."
    ]

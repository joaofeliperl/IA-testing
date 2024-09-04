import torch
from torchvision.models.detection import FasterRCNN, fasterrcnn_resnet50_fpn

def load_custom_model(model_path, num_classes):
    backbone = fasterrcnn_resnet50_fpn(pretrained=True).backbone
    model = FasterRCNN(backbone, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path))
    model.eval()  
    return model

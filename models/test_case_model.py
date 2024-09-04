import torch
import signal  # Para capturar SIGINT
import sys  # Para encerrar o script de forma limpa
from torch.utils.data import DataLoader
from torchvision.models.detection import FasterRCNN, fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.datasets import VOCDetection
from torchvision.transforms import ToTensor
import os

# Flag to track interruption
interrupted = False

# Handler para capturar o Ctrl + C e salvar o checkpoint antes de encerrar
def signal_handler(sig, frame):
    global interrupted
    print("\nInterrupção detectada. Salvando checkpoint e encerrando...")
    interrupted = True

# Registrar o handler para SIGINT
signal.signal(signal.SIGINT, signal_handler)

# Custom transform para imagens
class CustomTransform:
    def __call__(self, img):
        return ToTensor()(img)

# Custom transform para alvos (anotações)
class CustomTargetTransform:
    def __call__(self, target):
        return transform_target(target)

def transform_target(target):
    boxes = []
    labels = []
    for obj in target['annotation']['object']:
        bbox = obj['bndbox']
        boxes.append([int(bbox['xmin']), int(bbox['ymin']), int(bbox['xmax']), int(bbox['ymax'])])
        labels.append(1)

    boxes = torch.tensor(boxes, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.int64)
    return {'boxes': boxes, 'labels': labels}

def save_checkpoint(epoch, model, optimizer, loss, folder_name="checkpoints", file_name="checkpoint.pth.tar"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    full_path = os.path.join(folder_name, file_name)

    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, full_path)
    print(f"Checkpoint salvo no epoch {epoch + 1} em {full_path}")

def load_latest_checkpoint(folder_name, model, optimizer):
    if not os.path.exists(folder_name):
        print(f"Nenhum diretório encontrado: {folder_name}, iniciando do zero.")
        return 0, None

    checkpoint_files = [f for f in os.listdir(folder_name) if f.startswith("checkpoint") and f.endswith(".pth.tar")]
    if len(checkpoint_files) == 0:
        print(f"Nenhum arquivo de checkpoint encontrado em {folder_name}, iniciando do zero.")
        return 0, None

    checkpoint_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    latest_checkpoint = checkpoint_files[-1]
    full_path = os.path.join(folder_name, latest_checkpoint)

    try:
        checkpoint = torch.load(full_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        epoch = checkpoint['epoch']
        loss = checkpoint['loss']
        print(f"Checkpoint carregado: {latest_checkpoint}, continuando a partir do epoch {epoch + 1}")
        return epoch + 1, loss
    except FileNotFoundError:
        print(f"Checkpoint não encontrado em {full_path}, iniciando do zero.")
        return 0, None

def evaluate_model(model, data_loader):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for images, targets in data_loader:
            images = list(image for image in images)
            targets = [{k: v for k, v in t.items()} for t in targets]
            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())
            total_loss += losses.item()
    average_loss = total_loss / len(data_loader)
    print(f"Validation Loss: {average_loss:.4f}")
    return average_loss

def train_model(model, optimizer, lr_scheduler, num_epochs, train_loader, val_loader, start_epoch=0, save_every_n_batches=10):
    global interrupted
    for epoch in range(start_epoch, num_epochs):
        print(f"Iniciando Epoch: {epoch + 1}")
        model.train()
        epoch_loss = 0
        for i, (images, targets) in enumerate(train_loader):
            images = list(image for image in images)
            targets = [{k: v for k, v in t.items()} for t in targets]

            optimizer.zero_grad()
            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())
            losses.backward()
            optimizer.step()

            if (i + 1) % save_every_n_batches == 0:
                print(f"Epoch [{epoch + 1}/{num_epochs}], Batch [{i + 1}], Loss: {losses.item()}")
                save_checkpoint(epoch, model, optimizer, losses.item(), file_name=f"checkpoint_batch_{i+1}.pth.tar")

            epoch_loss += losses.item()

            # Verificar se houve interrupção
            if interrupted:
                print(f"Treinamento interrompido no batch {i + 1} do epoch {epoch + 1}.")
                save_checkpoint(epoch, model, optimizer, epoch_loss)
                sys.exit(0)

        lr_scheduler.step()
        print(f"Epoch [{epoch + 1}/{num_epochs}] completado. Loss média: {epoch_loss / len(train_loader)}")
        save_checkpoint(epoch, model, optimizer, epoch_loss)
        evaluate_model(model, val_loader)

    torch.save(model.state_dict(), 'fasterrcnn_model.pth')

if __name__ == "__main__":
    img_transform = CustomTransform()
    target_transform = CustomTargetTransform()

    # Carregar datasets
    train_dataset = VOCDetection(root='./data/VOCdevkit/VOC2012', download=False, transform=img_transform)
    val_dataset = VOCDetection(root='./data/VOCdevkit/VOC2012', download=False, transform=img_transform)

    # Função de collate personalizada
    def custom_collate_fn(batch):
        images, targets = zip(*batch)
        images = list(img for img in images)
        targets = [target_transform(target) for target in targets]
        return images, targets

    # Criar data loaders
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, collate_fn=custom_collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False, collate_fn=custom_collate_fn)

    # Carregar o modelo pretreinado Faster R-CNN
    backbone = fasterrcnn_resnet50_fpn(weights='DEFAULT').backbone
    model = FasterRCNN(backbone, num_classes=2)

    # Modificar a cabeça do classificador (se necessário)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes=2)

    optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    # Carregar o último checkpoint, se disponível
    start_epoch, _ = load_latest_checkpoint(folder_name="checkpoints", model=model, optimizer=optimizer)

    # Treinar o modelo
    train_model(model, optimizer, lr_scheduler, num_epochs=10, train_loader=train_loader, val_loader=val_loader, start_epoch=start_epoch)

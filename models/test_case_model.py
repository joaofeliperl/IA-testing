import torch
from torch.utils.data import DataLoader
from torchvision.models.detection import FasterRCNN, fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.datasets import VOCDetection
from torchvision.transforms import ToTensor

# Custom transform for images
class CustomTransform:
    def __call__(self, img):
        return ToTensor()(img)  # Convert image to tensor

# Custom transform for targets (annotations)
class CustomTargetTransform:
    def __call__(self, target):
        return transform_target(target)  # Transform the target using the transform_target function

# Function to transform target annotations
def transform_target(target):
    boxes = []  # List to store bounding boxes
    labels = []  # List to store corresponding classes
    for obj in target['annotation']['object']:
        bbox = obj['bndbox']
        boxes.append([int(bbox['xmin']), int(bbox['ymin']), int(bbox['xmax']), int(bbox['ymax'])])
        labels.append(1)  # Assuming all boxes belong to the same class (1)

    boxes = torch.tensor(boxes, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.int64)
    return {'boxes': boxes, 'labels': labels}

# Function to save checkpoints
def save_checkpoint(epoch, model, optimizer, loss, file_name="checkpoint.pth.tar"):
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, file_name)
    print(f"Checkpoint saved at epoch {epoch + 1}")

# Function to load checkpoints
def load_checkpoint(file_name, model, optimizer):
    checkpoint = torch.load(file_name)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    print(f"Checkpoint loaded, resuming from epoch {epoch + 1}")
    return epoch, loss

# Function to evaluate the model
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

# Function to train the model
def train_model(model, optimizer, lr_scheduler, num_epochs, train_loader, val_loader, start_epoch=0):
    for epoch in range(start_epoch, num_epochs):
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

            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch + 1}/{num_epochs}], Batch [{i + 1}], Loss: {losses.item()}")

            epoch_loss += losses.item()
        
        lr_scheduler.step()
        print(f"Epoch [{epoch + 1}/{num_epochs}] completed. Average Training Loss: {epoch_loss / len(train_loader)}")

        # Save checkpoint
        save_checkpoint(epoch, model, optimizer, epoch_loss)

        # Evaluate the model on the validation set
        evaluate_model(model, val_loader)

    torch.save(model.state_dict(), 'fasterrcnn_model.pth')

if __name__ == "__main__":
    img_transform = CustomTransform()
    target_transform = CustomTargetTransform()

    # Load datasets
    train_dataset = VOCDetection(root='./data/VOCdevkit/VOC2012', download=True, transform=img_transform)
    val_dataset = VOCDetection(root='./data/VOCdevkit/VOC2012', download=True, transform=img_transform)

    # Custom collate function
    def custom_collate_fn(batch):
        images, targets = zip(*batch)
        images = list(img for img in images)
        targets = [target_transform(target) for target in targets]
        return images, targets

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, collate_fn=custom_collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False, collate_fn=custom_collate_fn)

    # Load the pre-trained Faster R-CNN model
    backbone = fasterrcnn_resnet50_fpn(weights='DEFAULT').backbone
    model = FasterRCNN(backbone, num_classes=2)

    # Modify the classifier head (if necessary)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes=2)

    optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    # Load checkpoint if available
    start_epoch = 0
    try:
        start_epoch, _ = load_checkpoint("checkpoint.pth.tar", model, optimizer)
    except FileNotFoundError:
        print("No checkpoint found, starting from scratch.")

    # Train the model
    train_model(model, optimizer, lr_scheduler, num_epochs=10, train_loader=train_loader, val_loader=val_loader, start_epoch=start_epoch)

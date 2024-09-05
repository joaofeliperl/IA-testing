import torch
from torchvision.models.detection import FasterRCNN, fasterrcnn_resnet50_fpn
import os
import pickle

# Função para carregar o modelo customizado com base no checkpoint
def load_custom_model(model_path, num_classes):
    try:
        # Carregar a arquitetura do modelo
        print(f"Carregando a arquitetura do Faster R-CNN com ResNet50 FPN.")
        backbone = fasterrcnn_resnet50_fpn(weights='DEFAULT').backbone  # Usando 'weights' em vez de 'pretrained'
        model = FasterRCNN(backbone, num_classes=num_classes)
        
        # Carregar o checkpoint completo (sem weights_only=True)
        print(f"Carregando o checkpoint do modelo de: {model_path}")
        checkpoint = torch.load(model_path)  # Carregar o arquivo completo, não só os pesos
        
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])  # Carregar o estado do modelo
            print("Checkpoint carregado com sucesso.")
        else:
            print("Erro: 'model_state_dict' ausente no checkpoint.")
        
        # Colocar o modelo em modo de avaliação
        model.eval()
        return model
    
    except FileNotFoundError:
        print(f"Erro: O arquivo de checkpoint {model_path} não foi encontrado.")
        return None
    
    except KeyError as e:
        print(f"Erro: Chave {e} ausente no checkpoint.")
        return None
    
    except pickle.UnpicklingError as e:
        print(f"Erro ao deserializar o arquivo de checkpoint: {e}")
        return None
    
    except Exception as e:
        print(f"Erro inesperado ao carregar o modelo: {e}")
        return None

# Função para verificar se os arquivos de checkpoint estão corrompidos
def check_checkpoints(folder_name="checkpoints"):
    if not os.path.exists(folder_name):
        print(f"Nenhum diretório encontrado: {folder_name}")
        return

    checkpoint_files = [f for f in os.listdir(folder_name) if f.startswith("checkpoint") and f.endswith(".pth.tar")]

    if len(checkpoint_files) == 0:
        print(f"Nenhum arquivo de checkpoint encontrado em {folder_name}.")
        return

    for checkpoint_file in checkpoint_files:
        full_path = os.path.join(folder_name, checkpoint_file)
        try:
            # Tentar carregar o checkpoint para verificar sua integridade
            with open(full_path, 'rb') as f:
                pickle.load(f)
            checkpoint = torch.load(full_path)
            if 'model_state_dict' in checkpoint:
                print(f"{checkpoint_file}: OK")
            else:
                print(f"{checkpoint_file}: Corrompido - 'model_state_dict' ausente.")
        except pickle.UnpicklingError as e:
            print(f"{checkpoint_file}: Corrompido - Erro de Unpickling ({e})")
        except Exception as e:
            print(f"{checkpoint_file}: Corrompido - {e}")

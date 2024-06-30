from torchvision import transforms
from pathlib import Path
import torch

SCRAPNET_CLASSES = [
    "10",
    "30",
    "50",
]

IMAGE_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ConvertImageDtype(torch.float32)
])

def is_valid_model_input(x: torch.Tensor, size: int):
    if x.dim() != 3:
        return False
    if x.size(0) != 3:
        return False
    if x.size(1) != size:
        return False
    if x.size(2) != size:
        return False
    return True

def is_valid_dataset(path: str):
    root = Path(path)
    if not root.is_dir():
        return False
    class_folders = [p.as_posix() for p in root.iterdir()]
    if len(class_folders) != 3:
        return False
    valid_folders = list(map(lambda x: (root / x).as_posix(), SCRAPNET_CLASSES))
    for folder in class_folders:
        if not folder in valid_folders:
            return False
    return True


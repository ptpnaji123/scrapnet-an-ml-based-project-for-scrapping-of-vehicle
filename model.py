import torch
from torch import nn
from utils import SCRAPNET_CLASSES, IMAGE_TRANSFORM
from PIL import Image

class ScrapnetModel(nn.Module):
    def __init__(self, classes: list[str] = SCRAPNET_CLASSES, image_size = 224):
        super().__init__()
        self.classes = classes
        self.num_classes = len(classes)
        self.image_size = image_size
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=3),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=3, stride=2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=3, stride=2),
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=3, stride=2),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * (self.image_size // 28) * (self.image_size // 28), 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, self.num_classes),
            nn.Softmax(0)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.fc(x)

        return x
    
    def predict(self, image: str) -> str:
        image = Image.open(image)
        x = IMAGE_TRANSFORM(image)
        x = x.unsqueeze(0)
        self.eval()
        with torch.no_grad():
            x = self(x)
        x = x.squeeze(0)
        x = torch.argmax(x, dim=0)
        x = self.classes[x.item()]
        return x
    
    def from_pretrained(path: str):
        model = ScrapnetModel()
        model.load_state_dict(torch.load(path)["model_state_dict"])
        return model


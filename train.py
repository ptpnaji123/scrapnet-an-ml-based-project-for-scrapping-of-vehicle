from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from model import ScrapnetModel
from utils import IMAGE_TRANSFORM, is_valid_dataset
from tqdm import tqdm
from pathlib import Path
import torch
import argparse

DEFAULT_EPOCHS = 10
DEFAULT_BATCH_SIZE = 32

def main(args):
    assert is_valid_dataset(args.data), "dataset folder is not valid"
    model = ScrapnetModel()
    dataset = ImageFolder(args.data, transform=IMAGE_TRANSFORM)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    if args.checkpoint:
        model = ScrapnetModel.from_pretrained(args.checkpoint)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        optimizer.load_state_dict(torch.load(args.checkpoint)["optimizer_state_dict"])

    model.train()
    loss = 0.0  
    for epoch in range(args.epoch):
        running_loss = 0.0
        for i, data in enumerate(tqdm(dataloader, desc=f"Epoch [{epoch}/{args.epoch}], Loss: {loss}")):
            inputs, labels = data
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        loss = running_loss / i
        running_loss = 0.0

    save_file = Path(args.save)
    save_file.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }, save_file)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", required=True)
    parser.add_argument("-s", "--save", required=True)
    parser.add_argument("-e", "--epoch", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("-b", "--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("-c", "--checkpoint")

    
    args = parser.parse_args()
    main(args)



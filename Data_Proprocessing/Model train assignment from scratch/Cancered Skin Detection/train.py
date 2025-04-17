# train.py
import os
from torchvision import datasets, transforms, models
import torch
from torch import nn, optim

data_dir = 'dataset'
model_path = 'model/cat_dog_model.pth'

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

dataset = datasets.ImageFolder(data_dir, transform=transform)
loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)

model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # 2 classes: cat, dog

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

print("Training...")
for epoch in range(3):  # Keep it low for fast training
    running_loss = 0.0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"Epoch {epoch+1}, Loss: {running_loss:.4f}")

os.makedirs("model", exist_ok=True)
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")

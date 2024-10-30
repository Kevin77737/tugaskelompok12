# -*- coding: utf-8 -*-
"""tugas sekar.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ryyl8Ytli5gwVtWezZcnbiVRqz4aiVXB

# Import Library
"""

import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout

# Transformer modules
from transformers import ViTFeatureExtractor, ViTForImageClassification
from transformers import TrainingArguments, Trainer

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

"""# Import File, Extract, & Ubah CSV

Import File
"""

import zipfile
import os

# Path file ZIP dan folder tujuan ekstraksi
zip_path = '/content/Full_Process_Traces_2.zip'
extract_path = '/content/Full_Process_Traces'  # Ganti path agar lebih sederhana

# Ekstrak file ZIP
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Periksa isi folder setelah diekstraksi
print("File di folder setelah ekstraksi:")
print(os.listdir(extract_path))

"""Mengubah dataset ke CSV

# Preprocessing Data
"""

import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

# Path folder yang berisi file log
log_dir = '/content/Full_Process_Traces'

# Inisialisasi list untuk menyimpan data dan label
all_events = []
all_labels = []

# Loop melalui semua file di folder log_dir
for filename in os.listdir(log_dir):
    file_path = os.path.join(log_dir, filename)

    # Pastikan file adalah file teks (log file)
    if os.path.isfile(file_path) and filename.endswith(".log"):
        try:
            with open(file_path, 'r') as f:
                # Baca semua baris dalam file log
                lines = f.readlines()

                # Ekstrak event dan label dari setiap baris
                # Asumsi format: <event> <label>
                # Anda perlu menyesuaikan ini dengan format data Anda
                for line in lines:
                    parts = line.strip().split(' ')
                    event = ' '.join(parts[:-1])  # Gabungkan semua bagian kecuali label
                    label = parts[-1]  # Bagian terakhir adalah label

                    all_events.append(event)
                    all_labels.append(label)

        except Exception as e:
            print(f"Error saat memproses '{file_path}': {e}")

# Encode label (jika perlu)
label_encoder = LabelEncoder()
all_labels = label_encoder.fit_transform(all_labels)

# Tokenisasi dan Padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_events)
# Change 'tokenizer.texts_to' to 'tokenizer.texts_to_sequences' to call the correct method
sequences = tokenizer.texts_to_sequences(all_events)

"""# Membangun Model TB-Detector Berbasis Transformer"""

import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout
from transformers import ViTFeatureExtractor, ViTForImageClassification
from transformers import TrainingArguments, Trainer
import warnings
import zipfile
import os
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import subprocess
import torch
import torch.nn as nn
from transformers import BertForSequenceClassification


# Suppress warnings
warnings.filterwarnings("ignore")

class Config:
    """Configuration class for model parameters"""
    MAX_LENGTH = 512
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 2e-5
    TRAIN_SIZE = 0.8
    VAL_SIZE = 0.2
    RANDOM_STATE = 42
    NUM_LABELS = 2
    TBDETECTOR_REPO = "https://github.com/dazhi-ui/TBDetector.git"
    TBDETECTOR_PATH = "TBDetector"


def clone_tbdetector():
    """Clone TBDetector repository if not exists"""
    if not os.path.exists(Config.TBDETECTOR_PATH):
        subprocess.run(["git", "clone", Config.TBDETECTOR_REPO])
        print(f"TBDetector repository cloned to {Config.TBDETECTOR_PATH}")
    else:
        print(f"TBDetector repository already exists in {Config.TBDETECTOR_PATH}")


class TBDetectorModel(nn.Module):
    """TBDetector model integrating with the GitHub repository"""
    def __init__(self):
        super(TBDetectorModel, self).__init__()
        # Ensure TBDetector is cloned
        clone_tbdetector()
        # Base BERT model
        self.bert = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=Config.NUM_LABELS)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        return outputs


# ... (rest of your code from the previous response) ...

# Tokenisasi dan Padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_events)
sequences = tokenizer.texts_to_sequences(all_events) # Corrected method call
padded_sequences = pad_sequences(sequences, maxlen=Config.MAX_LENGTH, padding='post', truncating='post')

# ... (rest of your code) ...

"""# Menggunakan TensorBoard"""

import datetime
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping
import numpy as np # Import numpy for debugging

# Setup directory untuk log TensorBoard
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
# Callback lainnya (misalnya EarlyStopping)
early_stopping_callback = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

"""# Melatih Model"""

tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_events)
sequences = tokenizer.texts_to_sequences(all_events)
padded_sequences = pad_sequences(sequences, maxlen=Config.MAX_LENGTH, padding='post', truncating='post')

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

# Dummy Config class for parameters
class Config:
    TRAIN_SIZE = 0.8
    RANDOM_STATE = 42
    LEARNING_RATE = 0.001
    EPOCHS = 10
    PRINT_INTERVAL = 1

# Dummy model definition
class TBDetectorModel(nn.Module):
    def __init__(self):
        super(TBDetectorModel, self).__init__()
        self.fc1 = nn.Linear(100, 50)  # Assuming padded_sequences shape (1000, 100)
        self.fc2 = nn.Linear(50, 10)    # Assuming 10 output classes

    def forward(self, x):
        x = self.fc1(x)
        x = nn.ReLU()(x)
        x = self.fc2(x)
        return x

# Example padded_sequences and all_labels
padded_sequences = np.random.rand(1000, 100)  # Simulated input
all_labels = np.random.randint(0, 10, size=(1000,))  # Simulated labels

# Print shapes for debugging
print("Shape of padded_sequences:", padded_sequences.shape)
print("Shape of all_labels:", np.array(all_labels).shape)

# Check if padded_sequences is empty
if padded_sequences.size == 0:
    print("Error: padded_sequences is empty. Check your data preprocessing.")
    exit()  # Stop execution to prevent the error

# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    padded_sequences, all_labels, train_size=Config.TRAIN_SIZE, random_state=Config.RANDOM_STATE
)

# Convert data to PyTorch tensors with correct dtype
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)  # Change to float32
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_val_tensor = torch.tensor(X_val, dtype=torch.float32)      # Change to float32
y_val_tensor = torch.tensor(y_val, dtype=torch.long)

# Create the TBDetector model
model = TBDetectorModel()

# Define optimizer and loss function
optimizer = torch.optim.AdamW(model.parameters(), lr=Config.LEARNING_RATE)
loss_fn = nn.CrossEntropyLoss()

# Training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
X_train_tensor = X_train_tensor.to(device)
y_train_tensor = y_train_tensor.to(device)
X_val_tensor = X_val_tensor.to(device)
y_val_tensor = y_val_tensor.to(device)

num_epochs = Config.EPOCHS
for epoch in range(num_epochs):
    model.train()  # Set the model to training mode
    optimizer.zero_grad()  # Clear the gradients

    # Forward pass
    outputs = model(X_train_tensor)  # Forward pass through the model
    loss = loss_fn(outputs, y_train_tensor)  # Calculate loss

    # Backward pass and optimization
    loss.backward()  # Backpropagation
    optimizer.step()  # Update model parameters

    # Print training progress
    if (epoch + 1) % Config.PRINT_INTERVAL == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Validation step
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():  # Disable gradient calculation
        val_outputs = model(X_val_tensor)  # Forward pass on validation data
        val_loss = loss_fn(val_outputs, y_val_tensor)  # Calculate validation loss
        _, predicted = torch.max(val_outputs, 1)  # Get the predicted class
        correct = (predicted == y_val_tensor).sum().item()  # Count correct predictions
        val_accuracy = correct / y_val_tensor.size(0)  # Calculate validation accuracy

        # Print validation metrics
        print(f'Validation Loss: {val_loss.item():.4f}, Validation Accuracy: {val_accuracy:.4f}')

"""# Menjalankan TensorBoard"""

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from sklearn.model_selection import train_test_split

# Your model, training data, and configurations here
# ...

# Set up TensorBoard writer
writer = SummaryWriter(log_dir='logs/fit')

# Training loop
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()

    # Forward pass and loss calculation
    outputs = model(X_train_tensor)
    loss = loss_fn(outputs, y_train_tensor)

    # Backward pass
    loss.backward()
    optimizer.step()

    # Log metrics to TensorBoard
    writer.add_scalar('Loss/train', loss.item(), epoch)
    # Optionally log other metrics such as accuracy here

# Close the writer after training
writer.close()

"""# Evaluasi Model"""

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from sklearn.model_selection import train_test_split

# Your model, training data, and configurations here
# ...
# Split data into training, validation, and test sets
X_train, X_temp, y_train, y_temp = train_test_split(
    padded_sequences, all_labels, train_size=Config.TRAIN_SIZE, random_state=Config.RANDOM_STATE
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, train_size=0.5, random_state=Config.RANDOM_STATE
)

# Convert test data to PyTorch tensors and move to device
X_test = torch.tensor(X_test, dtype=torch.float32).to(device)
y_test = torch.tensor(y_test, dtype=torch.long).to(device)

def evaluate(model, X_test, y_test):
    """
    Evaluates the model on the test data and returns the loss and accuracy.

    Args:
        model (nn.Module): The PyTorch model to evaluate.
        X_test (torch.Tensor): The test data.
        y_test (torch.Tensor): The test labels.

    Returns:
        tuple: A tuple containing the loss and accuracy.
    """
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():  # Disable gradient calculation
        outputs = model(X_test)  # Forward pass on test data
        loss = loss_fn(outputs, y_test)  # Calculate loss
        _, predicted = torch.max(outputs, 1)  # Get the predicted class
        correct = (predicted == y_test).sum().item()  # Count correct predictions
        accuracy = correct / y_test.size(0)  # Calculate accuracy

    return loss.item(), accuracy  # Return loss and accuracy

# ... (Rest of your code remains the same)

# Assuming you have X_test and y_test loaded as PyTorch tensors
# and moved to the correct device (CPU or GPU)
loss, accuracy = evaluate(model, X_test, y_test)  # Call the evaluate function
print(f"Test Accuracy: {accuracy * 100:.2f}%")
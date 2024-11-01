# -*- coding: utf-8 -*-
"""tugas keamanan cerdas kelompok 12.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/149k7kUc_eC_O1wM5xPcjxLtx0K7zAU1Q

Import
"""

!pip install matplotlib seaborn plotly
!pip install transformers
!pip install scikit-learn
!pip install transformers datasets
!pip install datasets
!pip install --upgrade datasets

import pandas as pd
import os
import zipfile
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report, accuracy_score
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, Dataset
from google.colab import files
import torch
from tqdm import tqdm
from sklearn.metrics import classification_report, accuracy_score
import logging
logging.basicConfig(level=logging.INFO)

"""ekstrak file"""

uploaded = files.upload()
zip_file_name = 'Full_Process_Traces 2.zip'
extract_folder_name = 'datasets'
with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
    zip_ref.extractall(extract_folder_name)
os.listdir(extract_folder_name)

"""untuk membaca data"""

def load_adfa_ids(dataset_dir):
    data = []
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:

            try:
                with open(os.path.join(root, file), 'r', encoding='latin-1') as f:
                    sequence = f.readlines()
                    sequence = [line.strip() for line in sequence]
                    data.append(sequence)
            except UnicodeDecodeError:

                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-16') as f:
                        sequence = f.readlines()
                        sequence = [line.strip() for line in sequence]
                        data.append(sequence)
                except UnicodeDecodeError:
                    print(f"Error reading file: {file}. Skipping...")
    return [' '.join(seq) for seq in data]

normal_data = load_adfa_ids('datasets/Full_Trace_Training_Data/')
attack_data = load_adfa_ids('datasets/Full_Trace_Attack_Data/')

combined_data = normal_data + attack_data

# Create a DataFrame with sequences only
df = pd.DataFrame({
    'sequence': combined_data
})

# Shuffle the DataFrame
df = df.sample(frac=1).reset_index(drop=True)

"""Display data

"""

print(df.head(5))
print(df.info())

"""display data"""

total_count = len(df)

# Create a simple bar plot
plt.figure(figsize=(6, 6))
plt.bar(['Total Sequences'], [total_count], color='lightblue')
plt.title('Total Count of Sequences')
plt.ylabel('Count')
plt.show()

"""sample dataframe"""

data = {
    'sequence': [['call1', 'call2', 'call3'], ['call4', 'call5']],
    'label': [0, 1]  # Example labels (0 for normal, 1 for attack)
}
df = pd.DataFrame(data)

# Print the DataFrame to verify
print(df)

"""Splitting data training dan testing"""

train_data, test_data = train_test_split(df, test_size=0.3, random_state=42)

# Optionally reset the indices of the train and test DataFrames
train_data.reset_index(drop=True, inplace=True)
test_data.reset_index(drop=True, inplace=True)

"""Proses tokenisasi"""

df['sequence'] = df['sequence'].apply(lambda x: ' '.join(x))


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


tokenized = tokenizer(
    df['sequence'].tolist(),
    padding='max_length',
    truncation=True,
    max_length=100,
    return_tensors='pt'
)


input_ids = tokenized['input_ids']
attention_mask = tokenized['attention_mask']


print("Input IDs:", input_ids)
print("Attention Mask:", attention_mask)

from transformers import BertModel
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()  # Set the model to evaluation mode

# Get embeddings
with torch.no_grad():  # No need to track gradients
    outputs = model(input_ids, attention_mask=attention_mask)
    embeddings = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
    pooled_embeddings = torch.mean(embeddings, dim=1)


print("Pooled Embeddings:", pooled_embeddings)

conn = sqlite3.connect('embeddings.db')

# Save embeddings to a table
embeddings_df = pd.DataFrame(pooled_embeddings)
embeddings_df.to_sql('embeddings', conn, if_exists='replace', index=False)

conn.close()

"""Data baru untuk pendeteksian anomali"""

X = pooled_embeddings.numpy()

# Create One-Class SVM model
oc_svm = OneClassSVM(kernel='rbf', gamma='auto', nu=0.1)

# Fit model on normal data
oc_svm.fit(X)

new_raw_data = test_data
new_tokenized = tokenizer(
    new_raw_data['sequence'].tolist(),
    padding='max_length',
    truncation=True,
    max_length=100,
    return_tensors='pt'
)
new_input_ids = new_tokenized['input_ids']
new_attention_mask = new_tokenized['attention_mask']
with torch.no_grad():
    new_outputs = model(new_input_ids, attention_mask=new_attention_mask)
    new_embeddings = new_outputs.last_hidden_state
    new_pooled_embeddings = torch.mean(new_embeddings, dim=1)

# Predict on new data
new_data = new_pooled_embeddings.numpy() # Your new dataset here

"""Analisa Anomali"""

predictions = oc_svm.predict(new_data)

# Identify anomalies
anomalies = predictions == -1
print("Anomalous Data Points Indices:", np.where(anomalies)[0])

"""Analisa hasil"""

anomaly_indices = np.where(anomalies)[0]

# Output the anomalous data points
anomalous_data = new_data[anomaly_indices]
print("Anomalous Data Points:")
print(anomalous_data)

"""Evaluasi performa hasil"""

num_normal = len(new_raw_data) // 2  # Assuming first half is normal
num_anomalous = len(new_raw_data) - num_normal

true_labels = [1] * num_normal + [0] * num_anomalous

# Convert -1 and 1 predictions to 0 and 1 for compatibility
predicted_labels = (predictions + 1) // 2  # Convert -1 to 0 and 1 to 1

from sklearn.metrics import precision_score, recall_score, f1_score
# Calculate metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

# Print the results
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1:.2f}")

# Print detailed classification report
print(classification_report(true_labels, predicted_labels))

"""gambar hasil"""

from sklearn.decomposition import PCA
print(new_data.shape)  # This will output (n_samples, n_features)

# Apply PCA
pca = PCA(n_components=1)
reduced_data = pca.fit_transform(new_data)

# Plot
plt.figure(figsize=(10, 6))

# Scatter plot for normal data (only one component)
plt.scatter(reduced_data[~anomalies, 0], [0] * len(reduced_data[~anomalies]), label='Normal', alpha=0.5)

# Scatter plot for anomaly data (only one component)
plt.scatter(reduced_data[anomalies, 0], [0] * len(reduced_data[anomalies]), label='Anomalies', color='red')

plt.legend()
plt.title('Anomaly Detection using One-Class SVM')
plt.xlabel('PCA Component 1')
plt.ylabel('Value (constant, since n_components=1)')
plt.show()
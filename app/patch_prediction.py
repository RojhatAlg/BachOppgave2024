import labels as labels
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
import psycopg2

# Code doesn't work yet...
class PatchPredictionModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(PatchPredictionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def fetch_data_from_postgresql():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        user='root',
        password='password',
        database='db_commits'
    )
    cursor = conn.cursor()

    # Execute SQL query to fetch data
    cursor.execute("SELECT * FROM urls")

    # Fetch all rows of the result
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return data

# Define functions for preparing data, training, and inference

def prepare_data():
    # Fetch a data point from the database
    data_point = fetch_data_from_postgresql()
    input_data = data_point

    return input_data

def train_model(model, X_train, y_train, epochs, learning_rate):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item()}')

def predict(model, input_data):
    with torch.no_grad():
        model.eval()
        output = model(input_data)
        predicted_patch = torch.argmax(output, dim=1)
        return predicted_patch.item()

if __name__ == '__main__':
    # Main code to train the model and make predictions
    input_size = 4  # Define the input size based on your data
    hidden_size = 64  # Define the size of hidden layers
    output_size = 2  # Define the output size based on your data

    model = PatchPredictionModel(input_size, hidden_size, output_size)

    input_data = prepare_data()

    train_model(model, input_data, labels, epochs=100, learning_rate=0.001)

    # Example inference
    # Replace this with your actual data preparation code, this is just a test...
    input_data_for_prediction = torch.tensor([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]], dtype=torch.float32)
    predicted_patch = predict(model, input_data_for_prediction)
    print(f'Predicted patch: {predicted_patch}')

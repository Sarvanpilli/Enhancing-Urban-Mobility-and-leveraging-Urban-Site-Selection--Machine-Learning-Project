import pandas as pd
from sklearn.impute import SimpleImputer

# Step 1: Read the CSV file into a DataFrame
file_path = 'Dataset/dataset.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Step 2: Remove duplicate rows
df = df.drop_duplicates()

# Step 3: Replace NaN values in specified columns with the mean
columns_to_process = ['Latitude', 'Longitude']
for col in columns_to_process:
    if df[col].isnull().any():  # Check if NaN values exist in the column
        imputer = SimpleImputer(strategy='mean')
        df[col] = imputer.fit_transform(df[[col]])

output_file_path = "Dataset/updated_dataset1.csv"
df.to_csv(output_file_path, index=False)
    

# Display the preprocessed DataFrame
print(df)

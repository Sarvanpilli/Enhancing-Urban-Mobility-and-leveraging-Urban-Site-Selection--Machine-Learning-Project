import numpy as np
import math
import pandas as pd
import csv
def custom_function(number):
    if number < 0:
        return 0
    else:
        return math.floor(number)

def map_random_points_from_csv(south, west, north, east, n, points_csv, csv_filename="random_points_mapped.csv", encoding='latin1'):
    # Load points from CSV
    print(n)
    df = pd.read_csv(points_csv, encoding=encoding)
    points = list(zip(df['Latitude'], df['Longitude']))  # Adjust column names as per your CSV
    df2= pd.read_csv("Dataset/convolution_result.csv", encoding=encoding)
    points_ = list(zip(df2['Row'], df2['Column'], df2['Value']))

    # Extracting only the 'Value' from points_
    values = [value for _, _, value in points_]  
    print(values)   
    # Map each point to its corresponding row, column, and value
    data = [("Latitude", "Longitude", "Row", "Column", "Value")]
    z1=[]
    z2=[]
    q=[]
    i=0
    print(values)
    for lat, lon in points:
        # Calculate latitude and longitude based on row and column indices
        
        row =(lat-south)/((north-south)/n)
        col =(lon-west)/((east-west)/n)

        # Assign a random value (for example, 1)
        value = np.random.randint(1, 10)
        print(custom_function(row), custom_function(col))
        if(custom_function(row)<n and custom_function(col)<n):
            data.append((lat, lon, custom_function(row), custom_function(col), values[(((n*custom_function(row))+custom_function(col)))]))
            z1.append(custom_function(row))
            z2.append(custom_function(col))
            q.append(values[(((n*custom_function(row))+custom_function(col)))])
        else:
            data.append((lat, lon, n-1, n-1, 0))
            z1.append(n-1)
            z2.append(n-1)
            q.append(values[(((n*(n-1))+n-1))])
            
        
        i=i+1
        


# Save the modified DataFrame back to a CSV file
    df3 = pd.read_csv('Dataset/updated_dataset2.csv')
    print(df3)
    df3['Row'] = z1
    
    df3['Column'] = z2
    df3['Value'] = q
    print(df3)
    df3.to_csv('Dataset/dataset1.csv', index=False)
    # Write to CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
        

    print(f"CSV file '{csv_filename}' created successfully.")
    print("Random points mapped to rows, columns, and values.")

# Example input parameters
south, west = 17.692450476217097, 83.21295693558632
north, east = 17.743471383940076, 83.33250866030242
n = 6

# Example: Load points from dataset.csv and map them
dataset_csv = "Dataset/updated_dataset2.csv"
map_random_points_from_csv(south, west, north, east, n, dataset_csv)

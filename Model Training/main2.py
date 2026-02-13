import osmnx as ox
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import logging
import csv
import numpy as np
from scipy.signal import convolve2d

# Example input parameters
south, west = 17.692450476217097, 83.21295693558632
north, east = 17.743471383940076, 83.33250866030242
radius = 700
n = 6
kernel = np.array([[0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
                   [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                   [0.2, 0.4, 0.6, 0.6, 0.6, 0.4, 0.2],
                   [0.2, 0.4, 0.6, 0.8, 0.6, 0.4, 0.2],
                   [0.2, 0.4, 0.6, 0.6, 0.6, 0.4, 0.2],
                   [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                   [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],])

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def divide_into_blocks(south, west, north, east, n):
    """
    Divide a bounding box into n x n blocks and calculate the center points of each block.
    
    Parameters:
    south (float): The southern latitude of the bounding box.
    west (float): The western longitude of the bounding box.
    north (float): The northern latitude of the bounding box.
    east (float): The eastern longitude of the bounding box.
    n (int): The number of blocks in each dimension (total blocks will be n x n).
    
    Returns:
    list: A list of tuples, where each tuple represents the center point (latitude, longitude) of a block.
    """
    # Calculate block sizes
    delta_lat = (north - south) / n
    delta_lon = (east - west) / n

    centers = []
    for i in range(n):
        for j in range(n):
            # Calculate center point of each block
            center_lat = south + delta_lat * (i )
            center_lon = west + delta_lon * (j )
            centers.append((center_lat, center_lon))

    return centers

@lru_cache(maxsize=None)
def fetch_nodes(center_point, radius):
    try:
        G = ox.graph_from_point(center_point, dist=radius, simplify=False, truncate_by_edge=True, retain_all=True)
        return G
    except ValueError as e:
        if "No data elements in server response" in str(e):
            logging.warning(f"No data elements found for center point {center_point}")
        else:
            logging.error(f"Error fetching nodes for center point {center_point}: {e}")
        return None

def density(south, west, north, east, radius, n, csv_filename="Dataset/node_counts.csv"):
    # Divide the bounding box into n x n blocks and calculate centers
    centers = divide_into_blocks(south, west, north, east, n)

    def count_nodes(center_point):
        G = fetch_nodes(center_point, radius)
        if G:
            num_points = len(G.nodes())
        else:
            num_points = 0
        return center_point, num_points

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(count_nodes, centers))

    # Prepare data for CSV
    data = [("Center Point", "Latitude", "Longitude", "Number of Points")]
    matrix = np.zeros((n, n), dtype=int)
    
    index = 0
    for i in range(n):
        for j in range(n):
            center, num_points = results[index]
            latitude, longitude = center
            data.append((str(center), str(latitude), str(longitude), str(num_points)))
            matrix[i, j] = num_points
            index += 1
            print(index)

    # Write to CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{csv_filename}' created successfully.")
    print("Node count matrix:")
    print(matrix)
    return matrix

def convolve(matrix, kernel=kernel, csv_filename="Dataset/convolution_result.csv"):
    convolution_result = convolve2d(matrix, kernel, mode='same')
    data = [("Row", "Column", "Value")]

    for i in range(convolution_result.shape[0]):
        for j in range(convolution_result.shape[1]):
            data.append((i, j, convolution_result[i, j]))

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{csv_filename}' created successfully.")
    print("Convolution result matrix:")
    print(convolution_result)

# Call the main function with the input parameters
node_count_matrix = density(south, west, north, east, radius, n)
convolve(node_count_matrix, kernel)
    

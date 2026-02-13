import numpy as np
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point
from geopy.distance import distance

# Function to find the nearest node in a graph to a given point
def find_nearest_node(graph, point):
    nodes = list(graph.nodes(data=True))
    nearest_node = None
    min_dist = float('inf')
    # Ensure correct order (longitude, latitude) for Point creation
    point_geom = Point(float(point[1]), float(point[0]))
    
    for node, data in nodes:
        node_geom = Point(float(data['x']), float(data['y']))
        dist = point_geom.distance(node_geom)
        if dist < min_dist:
            min_dist = dist
            nearest_node = (node, data)
    
    nearest_node_id, nearest_node_data = nearest_node
    return nearest_node_id, nearest_node_data

# Function to plot the shortest path on a graph
def plot_shortest_path(graph, route):
    fig, ax = ox.plot_graph_route(graph, route, route_linewidth=6, node_size=0, bgcolor='k', edge_color='w', edge_linewidth=0.2)
    plt.show()

# Function to get the street network within a bounding box
def get_street_network(south, west, north, east, network_type='drive'):
    bbox = (north, south, east, west)
    return ox.graph_from_bbox(*bbox, network_type=network_type)

# Function to get primary roads within a bounding box
def get_primary_roads(south, west, north, east):
    bbox = (north, south, east, west)
    return ox.graph_from_bbox(*bbox, network_type='drive', custom_filter='["highway"="primary"]')

# Function to get secondary roads within a bounding box (if needed)
def get_secondary_roads(south, west, north, east):
    bbox = (north, south, east, west)
    return ox.graph_from_bbox(*bbox, network_type='drive', custom_filter='["highway"="secondary"]')

# Function to compute shortest distances to primary roads for each point of interest
def shortest_distances_primary(south, west, north, east, points):
    distances = []
    bbox = (north, south, east, west)
    G = ox.graph_from_bbox(*bbox, network_type='drive')  # Whole road network
    primary_roads = ox.graph_from_bbox(*bbox, network_type='drive', custom_filter='["highway"="primary"]')

    for point in points:
        # Find nearest nodes in both primary roads and whole network
        nearest_node_id_primary, nearest_node_data_primary = find_nearest_node(primary_roads, point)
        nearest_node_id_whole, nearest_node_data_whole = find_nearest_node(G, point)
        
        try:
            # Calculate distance in meters between the two nearest nodes
            distance1 = distance((nearest_node_data_primary['y'], nearest_node_data_primary['x']), (nearest_node_data_whole['y'], nearest_node_data_whole['x'])).meters
            distances.append((nearest_node_data_primary['y'], nearest_node_data_primary['x'], distance1))
        except (ValueError, TypeError):
            # Handle cases where distance calculation fails
            distances.append((nearest_node_data_primary['y'], nearest_node_data_primary['x'], None))
        
        # Print details for debugging
        print(f"Nearest Node in Primary Roads: {nearest_node_id_primary}")
        print(f"Coordinates: ({nearest_node_data_primary['y']}, {nearest_node_data_primary['x']})")
        print(f"Nearest Node in Whole Network: {nearest_node_id_whole}")
        print(f"Coordinates: ({nearest_node_data_whole['y']}, {nearest_node_data_whole['x']})")

    return distances
def shortest_distances_secondary(south, west, north, east, points):
    distances = []
    bbox = (north, south, east, west)
    G = ox.graph_from_bbox(*bbox, network_type='drive')  # Whole road network
    secondary_roads = ox.graph_from_bbox(*bbox, network_type='drive', custom_filter='["highway"="secondary"]')

    for point in points:
        # Find nearest nodes in both primary roads and whole network
        nearest_node_id_secondary, nearest_node_data_secondary = find_nearest_node(secondary_roads, point)
        nearest_node_id_whole, nearest_node_data_whole = find_nearest_node(G, point)
        
        try:
            # Calculate distance in meters between the two nearest nodes
            distance1 = distance((nearest_node_data_secondary['y'], nearest_node_data_secondary['x']), (nearest_node_data_whole['y'], nearest_node_data_whole['x'])).meters
            distances.append((nearest_node_data_secondary['y'], nearest_node_data_secondary['x'], distance1))
        except (ValueError, TypeError):
            # Handle cases where distance calculation fails
            distances.append((nearest_node_data_secondary['y'], nearest_node_data_secondary['x'], None))
        
        # Print details for debugging
        print(f"Nearest Node in Primary Roads: {nearest_node_id_secondary}")
        print(f"Coordinates: ({nearest_node_data_secondary['y']}, {nearest_node_data_secondary['x']})")
        print(f"Nearest Node in Whole Network: {nearest_node_id_whole}")
        print(f"Coordinates: ({nearest_node_data_whole['y']}, {nearest_node_data_whole['x']})")

    return distances

# Load the dataset from CSV
file_path = "Dataset/updated_dataset1.csv"
df = pd.read_csv(file_path, encoding='latin-1')
# Define bounding box coordinates
south, west = 17.692450476217097, 83.21295693558632
north, east = 17.743471383940076, 83.33250866030242


# Extract points of interest from the dataset
points = list(zip(df['Latitude'], df['Longitude']))  # Adjust column names as per your dataset
print(points)
# Compute shortest distances to primary roads for each point
distances_primary = shortest_distances_primary(south, west, north, east, points)
distances_secondary = shortest_distances_secondary(south, west, north, east, points)
print([points])
# Update dataframe with computed distances

for idx, (y, x, distance) in enumerate(distances_primary):
    df.at[idx, 'Nearest_Primary_Road Distance'] = distance if distance is not None else np.nan
    df.at[idx, 'Nearest_Primary_Road '] = "Primary" if distance is not None else ""
# Update dataframe with computed distances
for idx, (y, x, distance) in enumerate(distances_secondary):
    df.at[idx, 'Nearest_Secondary_Road Distance'] = distance if distance is not None else np.nan
    df.at[idx, 'Nearest_Secondary_Road '] = "Secondary" if distance is not None else ""







# Save the updated dataframe to a new CSV file
output_file_path = "Dataset/updated_dataset2.csv"
df.to_csv(output_file_path, index=False)

print(f"Updated dataset saved to {output_file_path}")

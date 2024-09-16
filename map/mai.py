from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pyautogui
import csv
from math import radians, sin, cos, sqrt, atan2
import math
import os

categories = {
  "Event Venue": [
        "Conference Center", "Convention Center", "Stadium", "Arena"
    ],
}

def extract_coordinates_from_url(url: str) -> tuple:
    def isnum(s):
        return s.isdigit()
    
    try:
        parts = url.split("/")
        print(parts)
        coordinates = []
        char = '.'
        string_part = parts[6]
        indexes = [i for i, c in enumerate(string_part) if c == char][:2]
        i = 0
        print(indexes)

        for char_index in indexes:
            
                
                if char_index >= 2 and isnum(parts[6][char_index - 1]) and isnum(parts[6][char_index - 2]):
                    coordinates.append(parts[6][char_index - 2:char_index + 7])
                    
                    i = i + 1
                else:
                    coordinates.append(parts[6][char_index - 1:char_index + 7])
                    
                    i = i + 1
                if i == 2:
                    lat, lng = coordinates[0], coordinates[1]
                    return float(lat), float(lng)
        return 'N/A', 'N/A'
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return 'N/A', 'N/A'

def haversine_distance(lon1, lon2, lat1, lat2):
    """
    Calculate the distance between two points on the Earth's surface given their longitudes and latitudes using the Haversine formula.
    
    Parameters:
        lon1 (float): Longitude of the first point in degrees.
        lon2 (float): Longitude of the second point in degrees.
        lat1 (float): Latitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
    
    Returns:
        float: Distance between the two points in meters.
    """
    # Earth's radius in meters
    R = 6378137
    
    # Convert degrees to radians
    lon1_rad = radians(lon1)
    lon2_rad = radians(lon2)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    
    # Calculate differences
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Haversine formula
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def move_point(lat, lon, distance_lat, distance_lon):
    # Radius of the Earth in meters
    R = 6371000
    
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate the change in latitude in radians
    delta_lat = distance_lat / R
    
    # Calculate the change in longitude in radians
    delta_lon = distance_lon / (R * math.cos(lat_rad))
    
    # Calculate the new latitude and longitude in radians
    new_lat_rad = lat_rad + delta_lat
    new_lon_rad = lon_rad + delta_lon
    
    # Convert the new latitude and longitude back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)
    
    return new_lat, new_lon

def moving_metre(latitude1, longitude1, distance_lat, distance_lon, side):
    if side == "lat": 
        new_lat, _ = move_point(latitude1, longitude1, distance_lat, distance_lon)
        dis = new_lat - latitude1
        return dis
    elif side == "lng":
        _, new_lon = move_point(latitude1, longitude1, distance_lat, distance_lon)
        dis = new_lon - longitude1
        return dis

def click_update_button(driver):
    """Function to click the update button"""
    try:
        update_button = driver.find_element(By.XPATH, '//button[@role="checkbox" and contains(@class, "D6NGZc")]')
        update_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Error clicking update button: {e}")

def move_mouse_to_position(x, y, duration=0.5):
    pyautogui.moveTo(x, y, duration=duration)

def scroll_up():
    pyautogui.scroll(10)

def scroll_down():
    pyautogui.scroll(-100)

def scroll_down_n(n):
    for _ in range(n):  # Adjust the range to scroll more if needed
        move_mouse_to_position(500, 500)
        scroll_down()
        time.sleep(1)  # Allow the results to load

def perform_search(driver, search_query):
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)

def go_fullscreen():
    """Function to toggle full screen mode using pyautogui"""
    pyautogui.press('f11')
    time.sleep(1)

def zoom_in(driver):
    """Function to zoom in on the map"""
    try:
        zoom_in_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Zoom in"]')
        zoom_in_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Error clicking zoom in button: {e}")

def zoom_in_ntimes(n,driver):
    for _ in range(n):
        zoom_in(driver)
def zoom_until_label_and_width(driver, desired_label, desired_width_px):
    retries = 10  # Maximum number of retries
    while retries > 0:
        try:
            # Find the button containing the zoom label and width style
            button = driver.find_element(By.XPATH, '//button[contains(@class, "LNGekf")]')
            click_update_button(driver)
            # Extract the label text
            label_element = button.find_element(By.XPATH, './/label[contains(@id, "U5ELMd")]')
            label = label_element.text
            
            # Extract the width style and parse the pixel value
            width_style = button.find_element(By.XPATH, './/div[contains(@class, "Ty7QWe")]').get_attribute("style")
            width_px = int(width_style.split(":")[-1].strip(" px;"))
            
            # Print the current label and width for debugging
            print(f"Current label: {label}, Current width: {width_px}px")
            
            # Check if both conditions are met
            if label == desired_label and width_px >= desired_width_px:
                print(f"Desired zoom level reached with label: {label} and width: {width_px}px")
                break
            
            # Click on the zoom button to zoom in
            zoom_in(driver)
            
            
        except Exception as e:
            print(f"Error during zoom: {e}")
            retries -= 1
            time.sleep(1)  # Wait a bit before retrying
    if retries == 0:
        print("Failed to reach the desired zoom level")


def set_starting_location(driver, latitude, longitude):
    # Go to the specific coordinates on Google Maps
    driver.get(f"https://www.google.com/maps/@{latitude},{longitude},15z")
    time.sleep(1)  # Allow the page to load

def move_rectangle(latitude1, longitude1, latitude2, longitude2, driver, distance_lat, distance_lng, categories, scroll_n=4, num_result=5 , zoom=3):
    d_latitude = moving_metre(latitude1, longitude1, distance_lat, 0, "lat")
    d_longitude = moving_metre(latitude1, longitude1, 0, distance_lng,"lng")
    data = [['Name', 'Rating', 'Number of Reviews', 'Latitude', 'Longitude', "Category","Sub-Category"]]
    append_list_to_csv(f"Dataset/dataset.csv",data)
    print(int(abs(latitude1-latitude2)/d_latitude))
    print(int(abs(longitude1-longitude2)/d_longitude))
    for i in range(int(abs(longitude1-longitude2)/d_longitude)):
       for j in range(int(abs(latitude1-latitude2)/d_latitude)):
             print(latitude1+j*d_latitude,longitude1+i*d_longitude)
             set_starting_location(driver, latitude1+j*d_latitude,longitude1+i*d_longitude)
             for c,sc in categories.items():
                 for search_query in sc:
                    perform_search(driver, search_query)
                    click_update_button(driver)
                    zoom_until_label_and_width(driver, desired_label='200 m', desired_width_px=57)
                    scroll_down_n(scroll_n)
                    get_info(latitude1, longitude1, latitude2, longitude2,driver,num_result,c,search_query)
             
def append_list_to_csv(csv_file_path, data_list):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    # Open the CSV file in append mode
    with open(csv_file_path, 'a', newline='') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)
        
        # Write each row of data to the CSV file
        for row in data_list:
            csv_writer.writerow(row)

def get_info(latitude1, longitude1, latitude2, longitude2,driver,num_result, c, search_query):
    # Extract data using BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    place_elements = soup.find_all('div', class_='Nv2PK', limit=num_result)
    data = []
    folder_name = f"Dataset/{c}_folder"
    os.makedirs(folder_name, exist_ok=True) 
    for place in place_elements:
        name = place.find('div', class_='qBF1Pd').text if place.find('div', class_='qBF1Pd') else 'N/A'
        rating = place.find('span', class_='MW4etd').text if place.find('span', class_='MW4etd') else 'N/A'
        reviews = place.find('span', class_='UY7F9').text if place.find('span', 'UY7F9') else 'N/A'

        # Extracting coordinates
        maps_link = place.find('a', class_='hfpxzc')
        if maps_link and 'href' in maps_link.attrs:
            lat, lng = extract_coordinates_from_url(maps_link['href'])
        else:
            lat, lng = ('N/A', 'N/A')

        data.append([name, rating, reviews,lat,lng,c,search_query])

    folder_name = f"Dataset/{c}_folder"
    os.makedirs(folder_name, exist_ok=True) 
    append_list_to_csv(f"Dataset/{c}_folder/{search_query}.csv",data)
    append_list_to_csv(f"Dataset/dataset.csv",data)


def main():
    #search_query = input("Enter search query: ")
    #num_results = int(input("Enter the number of results to extract: "))
    #latitude1 = input("Enter tip latitude: ")
    #longitude1 = input("Enter tip longitude: ")
    #latitude2 = input("Enter bottom latitude: ")
    #longitude2 = input("Enter bottom longitude: ")

    driver = webdriver.Chrome()
    driver.maximize_window()
    # Go to Google Maps
    driver.get('https://www.google.com/maps')
    #move_rectangle(latitude1,longitude1,latitude2,longitude2,driver,search_query, search_query)    
    move_rectangle(38.8363592557036, -77.04835828729044,38.97469056279769, -77.01340485076507,driver,950,600,categories)
    driver.quit()

if __name__ == "__main__":
    main()
    
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load data from CSV
df = pd.read_csv('output.csv')

# Check and drop unnecessary columns if they exist
columns_to_drop = ['Name']
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# Define categories and subcategories
categories = {
    "Shop": [
        "Stationery", "Diary", "Beauty Parlour", "Clothing", "Electronics",
        "Grocery", "Jewellery", "Furniture", "Sporting Goods", "Toys",
        "Pharmacy", "Convenience Store", "Hardware Store", "Shoe Store"
    ],
    "Shopping Mall": [
        "Departmental Store", "Jewelry Store", "Food Court", "Cinema"
    ],
    "Fuel Station": [
        "Electrical Charging Station", "Petrol Pump", "LPG Station"
    ],
    "Office": [
        "Corporate Office", "Co-working Space", "Law Firm", "Accounting Firm",
        "Advertising Agency", "Non-Profit Organization", "Insurance Agency",
        "Travel Agency", "Media Company"
    ],
    "Pilgrimage Place": [
        "Temple", "Church", "Mosque", "Gurudwara", "Monastery", "Shrine"
    ],
    "Restaurant": [
        "Fast Food", "Fine Dining", "Cafe", "Bakery", "Bar", "Pub",
        "Food Truck", "Buffet", "Pizzeria", "Ice Cream Parlor"
    ],
    "Entertainment": [
        "Movie Theater", "Amusement Park", "Museum", "Sports Complex",
        "Concert Hall", "Zoo", "Comedy Club"
    ],
    "Hotel": [
        "Budget", "Mid-Range", "Luxury", "Hostel", "Resort", "Bed & Breakfast"
    ],
    "Hospital": [
        "General Hospital", "Specialty Hospital", "Children's Hospital",
        "Maternity Hospital", "Rehabilitation Center", "Mental Health Clinic",
        "Dental Clinic", "Eye Clinic", "Veterinary Clinic"
    ],
    "Educational Institute": [
        "School", "College", "University", "Art School", "Music School",
        "Tuition Center", "Dance School", "Driving School"
    ],
    "Financial Institution": [
        "Bank", "ATM", "Investment Firm"
    ],
    "Government Building": [
        "Post Office", "Police Station", "Fire Station", "Courthouse",
        "City Hall", "Library"
    ],
    "Outdoor Space": [
        "Park", "Lake", "Forest", "Garden", "River", "Waterfall"
    ],
    "Transportation": [
        "Airport", "Train Station", "Bus Stop", "Taxi Stand"
    ],
    "Personal Care": [
        "Laundry", "Hair Salon"
    ],
    "Fitness & Wellness": [
        "Gym", "Yoga Studio"
    ],
    "Event Venue": [
        "Conference Center", "Convention Center", "Stadium", "Arena"
    ]
}

# One-hot encode categorical variables
df = pd.get_dummies(df, columns=['Category', 'Sub-Category'])

# Create list of columns for features
category_columns = [f'Category_{cat}' for cat in categories.keys()]
subcategory_columns = [f'Sub-Category_{sub}' for subs in categories.values() for sub in subs]

# Combine all feature columns
feature_columns = category_columns + subcategory_columns 
# Ensure all feature columns are in the DataFrame
for col in feature_columns:
    if col not in df.columns:
        df[col] = 0

# Split into features (X) and target variables (y)
X = df[feature_columns]
y_latitude = df['Latitude']
y_longitude = df['Longitude']

# Split data into training and testing sets
X_train, X_test, y_lat_train, y_lat_test, y_long_train, y_long_test = train_test_split(X, y_latitude, y_longitude, test_size=0.2, random_state=42)

# Initialize models
models = {
    'RandomForest': RandomForestRegressor(random_state=42),
    'GradientBoosting': GradientBoostingRegressor(random_state=42)
}

# Evaluate each model
results = {}
for name, model in models.items():
    # Train the model for Latitude
    model.fit(X_train, y_lat_train)
    y_pred_lat = model.predict(X_test)
    print(len(y_pred_lat))
    mse_lat = mean_squared_error(y_lat_test, y_pred_lat)
    r2_lat = r2_score(y_lat_test, y_pred_lat)
    
    # Train the model for Longitude
    model.fit(X_train, y_long_train)
    y_pred_long = model.predict(X_test)
    mse_long = mean_squared_error(y_long_test, y_pred_long)
    r2_long = r2_score(y_long_test, y_pred_long)
    
    results[name] = {
        'Latitude': {'MSE': mse_lat, 'R-squared': r2_lat},
        'Longitude': {'MSE': mse_long, 'R-squared': r2_long}
    }

# Display results
for name, result in results.items():
    print(f"Model: {name}")
    print(f"Latitude - Mean Squared Error: {result['Latitude']['MSE']}")
    print(f"Latitude - R-squared: {result['Latitude']['R-squared']}")
    print(f"Longitude - Mean Squared Error: {result['Longitude']['MSE']}")
    print(f"Longitude - R-squared: {result['Longitude']['R-squared']}")
    print("------------------------")

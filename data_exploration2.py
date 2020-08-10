# OSM Project
# data_exploration.py

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from pykalman import KalmanFilter

seaborn.set()

# Reference: https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def distance(points):
    def deg2Rad(deg):
        return deg * (np.pi / 180)
    R = 6371 * 1000
    data = points.diff(periods = 1)
    data = data.rename(columns = {"lat": "deltaLat", "lon": "deltaLon"})
    data['dLat'] = data['deltaLat'].apply(deg2Rad)
    data['dLon'] = data['deltaLon'].apply(deg2Rad)
    data['prodLat'] = np.cos(deg2Rad(points['lat'])) * np.cos(deg2Rad(points['lat'].shift(periods = 1)))
    data['a'] = np.sin(data['dLat'] / 2) ** 2 + data['prodLat'] * np.sin(data['dLon'] / 2) ** 2
    return np.sum(R * 2 * np.arctan2(np.sqrt(data['a']), np.sqrt(1 - data['a'])))



def main():
    input_file = sys.argv[1]
    data = pd.read_json(input_file, lines = True)
    data2 = data[['name', 'amenity', 'tags']]

    # Amenity graph
    #pd.value_counts(data['amenity']).plot.barh(figsize=(10,45), title='Amenity Counts')

    # Filter only food amenities: 
    food = data2[data2['amenity'].str.contains("restaurant|food|cafe|pub|bar|ice_cream|food_court|bbq|bistro") & ~data2['amenity'].str.contains("disused")]
    food = food.dropna()
    #print(food)
    
    # Filter large chain restaurants
    brand = food[food.apply(lambda x: 'brand' in x['tags'], axis = 1)]
    #pd.value_counts(brand['name']).plot.barh(figsize=(10,25), title='Counts for Chain Restaurants')
    
    # Question: Are there areas in the city with more pizza restaurants?
    # Filter pizza restaurants
    def filter_pizza(tags):
        return 'pizza' in tags.values()
    
    pizza = food[food['tags'].apply(filter_pizza)]

    

if __name__ == '__main__':
    main()

# OSM Project
# data_exploration.py

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pykalman import KalmanFilter


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
    #print(data.dtypes)
    
    # take a look at all the amenities
    data2 = data[['amenity', 'tags']]
    print(data2)
    #unique = data['amenity'].unique()
    #print(unique.size)
    pd.value_counts(data['amenity']).plot.barh(figsize=(10,45), title='Amenity Counts')
    # 

    # (Mostly) Useless Amenities: 
    # [bench, waste_basket, drinking_water, bicycle_parking, post_box, ]
    

if __name__ == '__main__':
    main()

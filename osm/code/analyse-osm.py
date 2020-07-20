import sys
import numpy as np
import pandas as pd

def main():
    file = sys.argv[1]
    data = pd.read_json(file, lines = True)
    
    # lat, lon, timestamp, amenity, name, tags
    #print(data.dtypes)
    print(data['timestamp'])
    print(data['name'])
    print(data['amenity'])
    print(data['tags'])
    
if __name__ == '__main__':
    main()
    
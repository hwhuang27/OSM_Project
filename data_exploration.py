
# data_exploration.py

import sys
import numpy as np
import pandas as pd
from pprint import pprint


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


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.8f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.8f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    points.apply(append_trkpt, axis = 1, trkseg = trkseg, doc = doc)
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent = ' ')


# python3 data_exploration.py ./osm/amenities-vancouver.json.gz output.gpx
def main():
    input_file = sys.argv[1]
    data = pd.read_json(input_file, lines = True)
    print(data)


    """ GPX file """
    # output_file = sys.argv[2]
    # data = data.sort_values(by = 'timestamp').reset_index(drop = True)
    # print(data)
    # output_gpx(data[['lat', 'lon']], output_file)


    """ center of the map """
    # print(data.lat.mean(), data.lon.mean())


    """ tags """
    # for i in range(20):
    #     pprint(data['tags'].iloc[i], indent = 4)

    # print(data[data.apply(lambda x: 'brand' not in x['tags'], axis = 1)])


    """ wiki data """
    # wiki = data[data.apply(lambda x: 'wikidata' and 'brand:wikidata' in x['tags'], axis = 1)]
    # print(wiki)
    # for i in range(20):
    #     pprint(wiki['tags'].iloc[i], indent = 4)


    """ fast food """
    # fast_food = data[data['amenity'] == 'fast_food']
    # print(fast_food)


    """ opening hours """
    food = data[data['amenity'].str.contains("restaurant|food|cafe|pub|bar|ice_cream|food_court|bbq|bistro") & ~data['amenity'].str.contains("disused")]
    food = food.dropna()
    food = food[food.apply(lambda x: 'opening_hours' in x['tags'], axis = 1)]

    print(food)
    print(food[food['amenity'] == 'fast_food'])
    for i in range(40):
        print(food['tags'].iloc[i]['opening_hours'])





if __name__ == '__main__':
    main()

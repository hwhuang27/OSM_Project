# OSM Project
# data_exploration.py

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
seaborn.set()


def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]   # viewing dataframes for testing purposes
    
    data = pd.read_json(input_file, lines = True)
    #data = data[['lat', 'lon', 'name', 'amenity', 'tags']]
    #print(data)

    # Amenity graph
    #pd.value_counts(data['amenity']).plot.barh(figsize=(10,45), title='Amenity Counts')

    # ----- Wikidata section -----
    # Filter entries with a wikidata tag
    wiki = data[data.apply(lambda x: 'wikidata' and 'brand:wikidata' in x['tags'], axis = 1)]


    # ----- Food section -----
    # Filter only food amenities: 
    food = data[data['amenity'].str.contains("restaurant|food|cafe|pub|bar|ice_cream|food_court|bbq|bistro") & ~data['amenity'].str.contains("disused")]
    food = food.dropna()
    
    # Question: What are the most popular types of restaurants in this city?
    # Follow-up: ...
    # This is to be a rough estimate of some of the most popular types of restaurants in Vancouver.
    # It is a rough estimate because some tags overlap (e.g japanese and sushi)
    # --> Maybe we can take out culture tags (chinese, japanese, thai, etc.)
    
    cuisine = food[food.apply(lambda x: 'cuisine' in x['tags'], axis = 1)]

    def get_cuisine_type(tags):
        return tags.get("cuisine")
    
    cuisine = cuisine.copy()
    cuisine['type'] = cuisine['tags'].apply(get_cuisine_type)
    cuisine = cuisine[['type']]
    
    # cleanup
    cuisine['type'] = cuisine['type'].str.replace(' ', '_')
    cuisine['type'] = cuisine['type'].str.replace(', ', ';')
    cuisine['type'] = cuisine['type'].str.replace(',_', ';')
    
    # explode
    # reference: https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python
    cuisine = cuisine['type'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
    
    # more cleanup + to lowercase
    cuisine = cuisine.loc[cuisine.str.len() < 30]
    cuisine = cuisine.str.lstrip('_')
    cuisine = cuisine.str.lower()
    
    # aggregate counts
    cuisine = cuisine.to_frame()
    cuisine.columns = ['type']
    
    # https://stackoverflow.com/questions/48770035/adding-a-count-column-to-the-result-of-a-groupby-in-pandas
    cuisine = cuisine.groupby(['type']).size().to_frame('count').reset_index()
    cuisine = cuisine.sort_values(by=['count'], ascending=False)
    
    # todo: plot the data

    cuisine.to_csv(output_file)
    
   
    # Question: Are there areas in the city with more pizza restaurants?
    # Filter pizza restaurants
    def filter_pizza(tags):
        return 'pizza' in tags.values()
    
    pizza = food[food['tags'].apply(filter_pizza)]
    pizza = pizza[['lat', 'lon', 'name']]

    # Question: TBD (something about chain restaurants)
    # Filter chain restaurants
    brand = food[food.apply(lambda x: 'brand' in x['tags'], axis = 1)]
    #pd.value_counts(brand['name']).plot.barh(figsize=(10,25), title='Counts for Chain Restaurants')



if __name__ == '__main__':
    main()

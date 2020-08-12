# CMPT354 Data Science Project (OSM)
# David Huang

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans

def get_clusters(X):
    # get_clusters() from Exercise 8 
    model = make_pipeline(
        KMeans(n_clusters=7, algorithm='elkan')
        
        # Cities to look at:
        # ['Vancouver', 'Burnaby', 'Richmond', 'Coquitlam', 'Langley', 'Surrey', 'Abbotsford']   
    )
    model.fit(X)
    return model.predict(X)

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]   # viewing dataframes for testing purposes
    
    data = pd.read_json(input_file, lines = True)
    #data = data[['lat', 'lon', 'name', 'amenity', 'tags']]

    # ----- Reduce and plot data set (amenities)  -----
    
    # We followed a couple rough guidelines for keeping amenities ...
    # 1) Should be of use for both locals and tourists alike
    # 2) Should be interesting or give something of value to a person
    # 3) Shouldn't be too saturated that you can find it everywhere (with exceptions like restaurants)
    
    # General reasoning for removing amenities ...
    # kept bicycle_rental, removed bicycle_parking because ...
    # rentals are still useful for tourists and locals alike, but
    # bicycle parking is too saturated, not a lot of use when you can find a spot anywhere
    
    reduced = data[['lat', 'lon', 'name', 'amenity', 'tags']]
    throwaways = ("bench|bicycle_parking|waste_basket|post_box|drinking_water|"
                  "parking_entrance|post_office|recycling|waste_disposal|"
                  "fire_station|bicycle_repair_station|kindergarten|compressed_air|"
                  "parking_space|shower|studio|motorcycle_parking|science|vacuum_cleaner|"
                  "construction|language_school|prep_school|loading_dock|smoking_area|"
                  "lounge|sanitary_dump_station|seaplane terminal|workshop|driving_school|"
                  "scrapyard|letter_box|post_depot|cram_school|Pharmacy|healthcare|"
                  "office|financial|lobby|first_aid|shop|clothes|payment_terminal|chiropractor|"
                  "ranger_station|housing co-op|waste_transfer_station|motorcycle_rental|"
                  "trash|training|EVSE|safety|watering_place|atm;bank|hunting_stand|storage|"
                  "nursery|water_point|car_rep|disused:restaurant|public_building|ATLAS_clean_room")
    
    reduced = reduced[~reduced['amenity'].str.contains(throwaways)]
    
    # original amenity graph
    #pd.value_counts(data['amenity']).plot.barh(figsize=(8,20), title='Amenity Counts', alpha=0.6, color=['blue', 'cyan'])
    #ac = pd.value_counts(data['amenity']).plot.barh(figsize=(8,20), title='Amenity Counts', alpha=0.6, color=['blue', 'cyan'])
    #ac.figure.savefig('amenity_counts.png')
    
    # reduced amenity graph
    #pd.value_counts(reduced['amenity']).plot.barh(figsize=(6,18), title='Amenity Counts (Reduced)', alpha=0.6, color=['green','teal'])
    #acr = pd.value_counts(reduced['amenity']).plot.barh(figsize=(6,18), title='Amenity Counts (Reduced)', alpha=0.6, color=['green','teal'])
    #acr.figure.savefig('amenity_reduced.png')

    
    # ----- Wikidata section -----
    # Filter entries with a wikidata tag
    wiki = reduced[reduced.apply(lambda x: 'wikidata' and 'brand:wikidata' in x['tags'], axis = 1)]

    # ----- Food section -----
    # Filter only food amenities: 
    food = data[data['amenity'].str.contains("restaurant|food|cafe|pub|bar|ice_cream|food_court|bbq|bistro") & ~data['amenity'].str.contains("disused")]
    food = food.dropna()
    
    # Question: What are the top restaurant types in this city? 
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
    
    # filter low count entries / filter cultural tags -> plot the data
    cuisine = cuisine[cuisine['count'] > 20]
    
    # plot [Top Restaurant Types] 
    plt.figure(figsize=(14,10))
    plt.barh(np.arange(len(cuisine)), cuisine['count'], height=0.7, alpha=0.8, color='bg')
    plt.yticks(np.arange(len(cuisine)), cuisine['type'])
    plt.xlabel('Count')
    plt.title('Top Restaurant types in Vancouver')
    plt.savefig('top_restaurants_analysis/top_restaurant_types.png')
    plt.clf()
    
    # plot [Top Restaurant Types] excluding cultural tags
    cuisine = cuisine[~cuisine['type'].str.contains("chinese|japanese|vietnamese|indian|mexican|italian|thai|asian|greek|korean|american|regional|portuguese|french|malaysian|mediterranean")]
    plt.figure(figsize=(14,10))
    plt.barh(np.arange(len(cuisine)), cuisine['count'], height=0.7, alpha=0.8, color='bg')
    plt.yticks(np.arange(len(cuisine)), cuisine['type'])
    plt.xlabel('Count')
    plt.title('Top Restaurant types in Vancouver (excluding cultural tags)')
    plt.savefig('top_restaurants_analysis/top_restaurant_types_no_cultural_tags.png')
    plt.clf()
    
    #cuisine.to_csv(output_file)
    
    # Question: How do the densities of pizza restaurants look like in each city?
    # Filter pizza restaurants
    def filter_pizza(tags):
        return 'pizza' in tags.values()
    
    pizza = food[food['tags'].apply(filter_pizza)]
    pizza = pizza[['lat', 'lon']]
    pnp_lat = pizza['lat'].to_numpy()
    pnp_lon = pizza['lon'].to_numpy()
    
    # center-of-city coordinates, courtesy of google
    city_labels = ['Vancouver', 'Burnaby', 'Richmond', 'Coquitlam', 'Langley', 'Surrey', 'Abbotsford']
    cities_lat = np.array([49.2827, 49.2488, 49.1666, 49.2838, 49.1042, 49.1913, 49.0504])
    cities_lon = np.array([-123.1207, -122.9805, -123.1336, -122.7932, -122.6604, -122.8490, -122.3045])
    
    # let's make those clusters
    pizza_clusters = get_clusters(pizza)
    
    # set custom labels for center-of-city points
    # reference: https://stackoverflow.com/questions/5147112/how-to-put-individual-tags-for-a-scatter-plot
    plt.subplots_adjust(bottom = 0.1)
    plt.title('Pizza Restaurant Densities')
    plt.scatter(pizza['lat'], pizza['lon'], marker='o', c=pizza_clusters, cmap='Set2', alpha=0.9, s=110)
    for label, x, y in zip(city_labels, cities_lat, cities_lon):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20,20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.4),
            arrowprops=dict(arrowstyle = 'simple', connectionstyle='arc3,rad=0')) 
    
    plt.savefig('pizza_clusters_analysis/pizza_clusters.png')   
    
    # Question: TBD (something about chain restaurants)
    # Filter chain restaurants
    brand = food[food.apply(lambda x: 'brand' in x['tags'], axis = 1)]
    #pd.value_counts(brand['name']).plot.barh(figsize=(10,25), title='Counts for Chain Restaurants')
    

if __name__ == '__main__':
    main()

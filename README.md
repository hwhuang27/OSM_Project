# CMPT353_OSM_Project



## Prerequisites

### Environment:

- `Python3` 
- `Jupyter notebook` 



### Required Libraries:

**Installation**:

```
pip install numpy pandas scipy matplotlib jupyter folium seaborm scikit-learn
```



## Project Structure

### Folders

- `./amenity_counts/`: Contains figures for amenity counts
- `./exploration/`: Contains scratch work in the data exploration step
- `./osm/`: Contains input data files
- `./parks_analysis/`: Contains figures for the park analysis
- `./pizza_clusters_analysis/`: Contains figures for the pizza clusters analysis
- `./top_restaurants_analysis/`: Contains figures for the top restaurants analysis

### Files

- `./fast_food.ipynb`: Codes and results for fast food restaurants study
- `./get_opening_hours.py`: Program that extracts opening hours data from the data file
- `./opening_hours.ipynb`:Codes and results for opening hours analysis
- `./opening_hours.json`: Opening hours data for restaurants, output file of `get_opening_hours.py` 
- `./various_questions.py`: Program that generates figures for various questions



## Instructions

### Input data file

The main input data files is `./osm/amenities-vancouver.json.gz` in the project folder. 



### Get figures for various questions

**Program**: `various_questions.py` 



**How to run:** 

```bash
py various_questions.py osm\amenities-vancouver.json.gz osm\parks.csv output.csv
```

OR

```bash
python3 various_questions.py osm\amenities-vancouver.json.gz osm\parks.csv output.csv
```

Requires `amenities-vancouver.json.gz` and `parks.csv` file in the `osm` folder.



**Files produced (in order):**

1. `amenity_counts/amenity_counts.png` 
2. `amenity_counts/amenity_reduced.png` 
3. `top_restaurants_analysis/top_restaurant_types.png` 
4. `top_restaurants_analysis/top_restaurant_types_no_cultural_tags.png` 
5. `top_restaurants_analysis/coffee_shop_follow_up.png` 
6. `pizza_clusters_analysis/pizza_clusters.png` 
7. `parks_analysis/washroom_ratio.png` 



### Extract opening hours data

**Program**: `get_opening_hours.py` 



**How to run**:

```bash
python3 get_opening_hours.py ./osm/amenities-vancouver.json.gz
```

Requires the `amenities-vancouver.json.gz` in the `osm` folder



**Files produced**:

1. `opening_hours.json` 






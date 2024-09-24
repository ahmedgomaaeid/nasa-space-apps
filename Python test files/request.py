import requests
import folium
import folium.plugins
from folium import Map, TileLayer
from pystac_client import Client
import pandas as pd
import matplotlib.pyplot as plt

from dataclasses import dataclass
from typing import List,Dict, Optional
import json
def write_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
@dataclass
class Asset:
    href: str
    type: str
    roles: List[str]
    title: str
    proj_bbox: List[float]
    proj_epsg: float
    proj_shape: List[float]
    description: str
    raster_bands: List[dict]
    proj_geometry: dict
    proj_projjson: dict
    proj_transform: List[float]
    proj_wkt2:Optional[any]
    rel: Optional[str]=None

@dataclass
class Link:
    rel: str
    type: str
    href: str
    title:Optional[str]=None
    method:Optional[str]=None

@dataclass
class Features:
    id: str
    bbox: List[float]
    type: str
    links: List[Link]
    assets: Dict[str, Asset]
    geometry: Dict
    properties: Dict
    stac_version: str
    stac_extensions: List
    collection: str

@dataclass
class Data:
    type: str
    context: Dict
    features: List[Features]
    links: List[Link]
# Assuming your data is stored in a variable called `data`
# Provide the STAC and RASTER API endpoints
# The endpoint is referring to a location within the API that executes a request on a data collection nesting on the server.
def parse_links(links_data: List[Dict]) -> List[Link]:
    return [Link(**link) for link in links_data]

# Function to convert dictionary entries into `Asset` dataclass
def parse_assets(assets_data: Dict[str, Dict]) -> Dict[str, Asset]:
    # Create a mapping for keys that need to be transformed
    key_mapping = {
        'proj:bbox': 'proj_bbox',
        'proj:epsg': 'proj_epsg',
        'proj:shape': 'proj_shape',
        'raster:bands': 'raster_bands',
        'proj:geometry': 'proj_geometry',
        'proj:projjson': 'proj_projjson',
        'proj:transform': 'proj_transform',
        'proj:wkt2':'proj_wkt2'
    }
    
    parsed_assets = {}
    for counter,(key, value) in enumerate(assets_data.items()):
        if(key=="rendered_preview"):
            continue
        # Transform keys according to the mapping
        transformed_value = {key_mapping.get(k, k): v for k, v in value.items()}
        # Print transformed value for debugging
        # print(f"Transformed asset data for key '{key}': {transformed_value}")

        # Ensure all required fields are present
        try:
            parsed_assets[key] = Asset(**transformed_value)
        except TypeError as e:
            print(f"Error creating Asset for key '{key}': {e} in index {counter}")
            # Handle missing fields if needed, e.g., skip or set defaults
            continue  # Skip this asset if there’s an error

    return parsed_assets


# Convert the API response into a `Features` object
def parse_features(features_data: List[Dict]) -> List[Features]:
    features_list = []
    for feature in features_data:
        # Manually parse `links` and `assets` fields
        links = parse_links(feature["links"])
        assets = parse_assets(feature["assets"])
        
        # Create a `Features` object
        features_list.append(Features(
            id=feature["id"],
            bbox=feature["bbox"],
            type=feature["type"],
            links=links,
            assets=assets,
            geometry=feature["geometry"],
            properties=feature["properties"],
            stac_version=feature["stac_version"],
            stac_extensions=feature["stac_extensions"],
            collection=feature["collection"]
        ))
    return features_list
# The STAC API is a catalog of all the existing data collections that are stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# The RASTER API is used to fetch collections for visualization
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"
# Choose a color map for displaying the first observation (event)
# Please refer to matplotlib library if you'd prefer choosing a different color ramp.
# For more information on Colormaps in Matplotlib, please visit https://matplotlib.org/stable/users/explain/colors/colormaps.html
# Create a function that would search for a data collection in the US GHG Center STAC API

# First, we need to define the function
# The name of the function = "get_item_count"
# The argument that will be passed through the defined function = "collection_id"
collection_name = "oco2-mip-co2budget-yeargrid-v1"
# Apply the function created above "get_item_count" to the data collection
# number_of_items = get_item_count(collection_name)

# Get the information about the number of granules found in the collection
# items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={6}").json()
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={276}").json()
print(type(items))
print(list(items.keys()))
# Print the total number of items (granules) found
print(f"Found {len(items)} items")

features = parse_features(items["features"])
links = parse_links(items["links"])

# Create a `Data` object
data_parsed = Data(
    type=items["type"],
    context=items["context"],
    features=features,
    links=links
)
write_json_to_file(items, 'items.json')
# Access properties from the parsed `Data` object
# Now we create a dictionary where the start datetime values for each granule is queried more explicitly by year and month (e.g., 2020-02)
items = {item.properties["start_datetime"]: item for item in data_parsed.features} 

# Next, we need to specify the asset name for this collection
# The asset name is referring to the raster band containing the pixel values for the parameter of interest
# For the case of the OCO-2 MIP Top-Down CO₂ Budgets collection, the parameter of interest is “ff”
asset_name = "ff" #fossil fuel
# Fetching the min and max values for a specific item

# Hardcoding the min and max values to match the scale in the GHG Center dashboard
rescale_values = {"max": 450, "min": 0}
color_map = "purd"

# Make a GET request to retrieve information for the 2020 tile which is the 1st item in the collection
# To retrieve the first item in the collection we use "0" in the "(items.keys())[0]" statement

# 2020
co2_flux_1 = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{data_parsed.features[0].collection}/items/{data_parsed.features[0].id}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"

    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    # Pass the minimum and maximum values for rescaling
    f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# Return the response in JSON format
).json()

# Print the properties of the retrieved granule to the console
# Make a GET request to retrieve information for the 2019 tile which is the 2st item in the collection
# To retrieve the second item in the collection we use "1" in the "(items.keys())[1]" statement

# 2019
co2_flux_2 = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{data_parsed.features[1].collection}/items/{data_parsed.features[1].id}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"

    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    # Pass the minimum and maximum values for rescaling
    f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# Return the response in JSON format
).json()
print("data is collected")
# print(f"co2_flux_1={items}")
# Print the properties of the retrieved granule to the console
# The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable
# Name of the collection for CEOS National Top-Down CO₂ Budgets dataset 
map_ = folium.plugins.DualMap(location=(34, -118), zoom_start=6)

# Define the first map layer (2020)
map_layer_2020 = TileLayer(
    tiles=co2_flux_1["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution
    opacity=0.5, # Adjust the transparency of the layer
)

# Add the first layer to the Dual Map
map_layer_2020.add_to(map_.m1)

# Define the second map layer (2019)
map_layer_2019 = TileLayer(
    tiles=co2_flux_2["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution
    opacity=0.5, # Adjust the transparency of the layer
)

# Add the second layer to the Dual Map
map_layer_2019.add_to(map_.m2)

# Visualize the Dual Map
map_.save("out.html")
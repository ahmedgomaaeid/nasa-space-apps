import requests
# import folium
# import folium.plugins
# from folium import Map, TileLayer
# from pystac_client import Client
# import branca
# import pandas as pd
# import matplotlib.pyplot as plt
import json
import time
def write_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
# Provide the STAC and RASTER API endpoints
# The endpoint is referring to a location within the API that executes a request on a data collection nesting on the server.

# The STAC API is a catalog of all the existing data collections that are stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# The RASTER API is used to fetch collections for visualization
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable
# Name of the collection for the wetland methane emissions LPJ-EOSIM Model
collection_name = "lpjeosim-wetlandch4-daygrid-v2"

# Next, we need to specify the asset name for this collection
# The asset name is referring to the raster band containing the pixel values for the parameter of interest
asset_name = "ensemble-mean-ch4-wetlands-emissions"
# Fetch the collection from the STAC API using the appropriate endpoint
# The 'requests' library allows a HTTP request possible
# Create a function that would search for a data collection in the US GHG Center STAC API

# First, we need to define the function
# The name of the function = "get_item_count"
# The argument that will be passed through the defined function = "collection_id"

def get_item_count(collection_id):

    # Set a counter for the number of items existing in the collection
    counter_req=0
    count = 0

    # Define the path to retrieve the granules (items) of the collection of interest in the STAC API
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"

    # Run a while loop to make HTTP requests until there are no more URLs associated with the collection in the STAC API
    while True:

        # Retrieve information about the granules by sending a "get" request to the STAC API using the defined collection path
        response = requests.get(items_url)

        # If the items do not exist, print an error message and quit the loop
        if not response.ok:
            print("error getting items")
            exit()

        # Return the results of the HTTP response as JSON
        stac = response.json()
        count_item=int(stac["context"].get("returned", 0))
        counter_req+=1
        print(f"Found {count_item} items for req number {counter_req}")
        # Increase the "count" by the number of items (granules) returned in the response
        count += count_item
        # Retrieve information about the next URL associated with the collection in the STAC API (if applicable)
        next = [link for link in stac["links"] if link["rel"] == "next"]

        # Exit the loop if there are no other URLs
        if not next:
            break
        
        # Ensure the information gathered by other STAC API links associated with the collection are added to the original path
        # "href" is the identifier for each of the tiles stored in the STAC API
        items_url = next[0]["href"]
        # temp = items_url.split('/')
        # temp.insert(3, 'ghgcenter')
        # temp.insert(4, 'api')
        # temp.insert(5, 'stac')
        # items_url = '/'.join(temp)

    # Return the information about the total number of granules found associated with the collection
    return count
start_time = time.time()
# print("Requesting collection...")

# Fetch the collection
collection_response = requests.get(f"{STAC_API_URL}/collections/{collection_name}")
# Check if the request was successful
if collection_response.status_code != 200:
    print(f"Error fetching collection: {collection_response.status_code}")
    print(f"Response content: {collection_response.text}")
    exit()

# Convert collection response to JSON
collection = collection_response.json()
# Apply the function created above "get_item_count" to the data collection
number_of_items = get_item_count(collection_name)
print("Requesting items...")
print(f"Found {number_of_items} items")
# Fetch items (granules) for the collection
items_response = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit=99999")
# print("got response")
# # Check if the items request was successful
# if items_response.status_code != 200:
#     print(f"Error fetching items: {items_response.status_code}")
#     print(f"Response content: {items_response.text}")
#     exit()

# # Try to parse the items response as JSON
# try:
#     items = items_response.json()
# except requests.exceptions.JSONDecodeError as e:
#     print(f"Error decoding items JSON: {str(e)}")
#     print(f"Response content: {items_response.text}")
#     exit()

# print("Items received.")

# # Print the total number of items (granules) found
# print(f"Found {len(items['features'])} items")

# Stop the stopwatch
end_time = time.time()

# Calculate and print the total time taken
elapsed_time = end_time - start_time
print(f"Request completed in {elapsed_time:.4f} seconds")

# Save items to a JSON file
# write_json_to_file(items, 'items.json')


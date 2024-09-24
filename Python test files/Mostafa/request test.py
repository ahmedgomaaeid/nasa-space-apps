import requests
import json
import time

# Supabase function URL (update this with your actual URL)
url = "https://hkidyqqraenpcgwmyqik.supabase.co/functions/v1/Nasa_Space_Apps_Test"

# Supabase JWT token (replace with your actual token)
headers = {
    "Content-Type": "application/json"
}

# The request payload with the collection name
payload = {
    "collectionName": "odiac-ffco2-monthgrid-v2023"
}

# Start the stopwatch before making the request
start_time = time.time()
print("requesting...")
# Make the POST request to the Supabase function
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Stop the stopwatch after receiving the response
end_time = time.time()

# Calculate the total time taken (in seconds)
elapsed_time = end_time - start_time

# Check if the request was successful
if response.status_code == 200:
    # Print the JSON response
    result = response.json()
    print("Result:", result)
else:
    # Print an error message if the request failed
    print(f"Error {response.status_code}: {response.text}")

# Print the total time taken
print(f"Request completed in {elapsed_time:.4f} seconds")

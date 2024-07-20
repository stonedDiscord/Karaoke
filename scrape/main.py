import requests
import json
import time

# Define the endpoint URL
url = "https://www.clubdam.com/dkwebsys/search-api/GetMusicDetailInfoApi"

# Function to generate request numbers
def generate_request_numbers():
    for i in range(1164, 9999):
        for j in range(100):
            yield f"{i:04d}-{j:02d}"

# Function to fetch data for a given request number
def fetch_data(request_no):
    payload = {
        "modelTypeCode": "1",
        "requestNo": request_no,
        "compId": "1",
        "authKey": "2/Qb9R@8s*"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    return None

# Text file setup
text_file = "music_details.txt"

# Main data fetching loop
with open(text_file, 'a', encoding='utf-8') as file:
    for request_no in generate_request_numbers():
        try:
            print(request_no)
            data = fetch_data(request_no)
            if data:
                parsed = json.dumps(data, ensure_ascii=False)
                if "artistCode" in parsed:
                    file.write(parsed + '\n')
                    time.sleep(0.1)  # Sleep to avoid hitting rate limits
        except Exception as e:
            print(f"An error occurred for requestNo {request_no}: {e}")
            continue

print("Data fetching completed.")
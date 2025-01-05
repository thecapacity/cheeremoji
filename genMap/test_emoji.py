import requests
import time
import json

def fetch_json(remote_url):
    try:
        response = requests.get(remote_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching JSON: {e}")
        return {}

def check_value(key, value, data):
    print(f"Checking key: {key}, value: {value}")
    print(f"\tData: {data}")

    if key != data.get("code") or value != data.get("emoji"):
        print(f"Mismatch: expected key {key} and value {value}, got key {data.get('code')} and value {data.get('emoji')}")
        return False

    return True
 
if __name__ == "__main__":

    URL = "https://cheeremoji.com/static/emojiMap.json"
    json_data = fetch_json(URL)

    GOOD_KEYS = []
    BAD_KEYS = []

    for key, value in json_data.items():
        URL = f"http://localhost:8787/code/{key}"
        #data = fetch_json(URL)
        response = requests.post(URL, json={"code": key})
        response.raise_for_status()
        data = response.json()
      
        #print(f"Checking key: {key}, value: {value}")
        #print(f"\tTarget URL: {URL}")
        #print(f"\tResponse: {data}")

        #for t in range(2):
            #print(f"{t} ... Checking key: {key}, value: {value}", end="\r")
        time.sleep(2)

        URL = f"http://localhost:8787/"
        data = fetch_json(URL)      

        if check_value(key, value, data):
            #print(f"Key: {key} WORKS!")
            GOOD_KEYS.append(key)
        else:
            print(f"\tBAD KEY: {key}")
            BAD_KEYS.append(key)

    with open("good_keys.txt", "w") as good_file:
        for key in GOOD_KEYS:
            good_file.write(f"{key}\n")

    with open("bad_keys.txt", "w") as bad_file:
        for key in BAD_KEYS:
            bad_file.write(f"{key}\n")
            
    with open("good_keys.json", "w") as good_file:
        json.dump(GOOD_KEYS, good_file, indent=4)

    with open("bad_keys.json", "w") as bad_file:
        json.dump(BAD_KEYS, bad_file, indent=4)

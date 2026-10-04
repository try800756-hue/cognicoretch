import urllib.request
import json
import sys

GATEWAY_URL = "https://cognicoretch-gateway.onrender.com/api/v1/search?q="

def query_gateway(search_term):
    url = GATEWAY_URL + urllib.parse.quote(search_term)
    print(f"\n[+] Querying CogniCoreTech Gateway for: '{search_term}'...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CogniCoreTech-Client/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"\nStatus: {data.get('status').upper()}")
            print("-" * 50)
            for idx, item in enumerate(data.get('results', []), 1):
                print(f"{idx}. {item['title']}")
                print(f"   URL: {item['url']}")
                print(f"   Info: {item['snippet']}")
            print("-" * 50)
    except Exception as e:
        print(f"[-] Error connecting to gateway: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_gateway(" ".join(sys.argv[1:]))
    else:
        print("Usage: python client.py <your search query>")

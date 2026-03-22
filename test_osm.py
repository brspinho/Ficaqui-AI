import requests

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
(
  way["building"]["addr:street"](-10.9200,-37.0580,-10.9100,-37.0450);
  node["building"]["addr:street"](-10.9200,-37.0580,-10.9100,-37.0450);
);
out center;
"""
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()
print(f"Total elements: {len(data['elements'])}")
if data['elements']:
    first = data['elements'][0]
    print(first)

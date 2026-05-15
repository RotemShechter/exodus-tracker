import urllib.request
import xml.etree.ElementTree as ET
import json

# Your Garmin feed. Adjust the start date (?d1=) to the beginning of your voyage.
URL = "https://share.garmin.com/Feed/Share/Exodussail?d1=2026-04-01T00:00z"

def fetch_and_parse():
    try:
        # Garmin sometimes blocks default Python user-agents, so we spoof a browser
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            kml_data = response.read()

        root = ET.fromstring(kml_data)
        # KML uses namespaces which we must define to parse correctly
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        coordinates = []
        
        # Extract only the raw coordinates from each Point
        for placemark in root.findall('.//kml:Placemark', ns):
            point = placemark.find('.//kml:Point/kml:coordinates', ns)
            if point is not None:
                coord_str = point.text.strip()
                parts = coord_str.split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    # Leaflet/Windy expects [Latitude, Longitude]
                    coordinates.append([lat, lon])

        # Write out to a clean JSON file
        with open('track.json', 'w') as f:
            json.dump(coordinates, f)
            
        print(f"Successfully processed {len(coordinates)} track points.")

    except Exception as e:
        print(f"Error fetching or parsing track: {e}")

if __name__ == "__main__":
    fetch_and_parse()

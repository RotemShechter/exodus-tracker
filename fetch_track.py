import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Adjust the start date (?d1=) to the beginning of your voyage.
URL = "https://share.garmin.com/Feed/Share/Exodussail?d1=2026-04-01T00:00z"

def fetch_and_parse():
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            kml_data = response.read()

        root = ET.fromstring(kml_data)
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        track_data = []
        
        for placemark in root.findall('.//kml:Placemark', ns):
            point = placemark.find('.//kml:Point/kml:coordinates', ns)
            if point is not None:
                coord_str = point.text.strip()
                parts = coord_str.split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    
                    # Dictionary to hold our rich data
                    point_data = {
                        "lat": lat,
                        "lon": lon,
                        "time": "Unknown",
                        "speed": "0 km/h",
                        "course": "N/A",
                        "elevation": "0 m",
                        "event": "Tracking point"
                    }

                    # Extract ExtendedData if available
                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is not None:
                        for data in extended_data.findall('kml:Data', ns):
                            name = data.get('name')
                            value = data.find('kml:value', ns)
                            if value is not None and value.text:
                                val_text = value.text.strip()
                                if name == "Time UTC":
                                    # Format time nicely if possible
                                    try:
                                        dt = datetime.strptime(val_text, "%m/%d/%Y %I:%M:%S %p")
                                        point_data["time"] = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
                                    except:
                                        point_data["time"] = val_text
                                elif name == "Velocity":
                                    try:
                                        # If Garmin only gives us km/h
                                        if "km/h" in val_text and "kn" not in val_text:
                                            kmh_value = float(''.join(c for c in val_text if c.isdigit() or c == '.'))
                                            knots_value = kmh_value / 1.852
                                            point_data["speed"] = f"{knots_value:.1f} kn ({kmh_value:.1f} km/h)"
                                        
                                        # If Garmin gives us only knots (just in case they change the feed)
                                        elif "kn" in val_text and "km/h" not in val_text:
                                            knots_value = float(''.join(c for c in val_text if c.isdigit() or c == '.'))
                                            kmh_value = knots_value * 1.852
                                            point_data["speed"] = f"{knots_value:.1f} kn ({kmh_value:.1f} km/h)"
                                            
                                        # If it already has both, pass it straight through
                                        else:
                                            point_data["speed"] = val_text
                                            
                                    except ValueError:
                                        # Fallback if the string contains unexpected characters
                                        point_data["speed"] = val_text
                                elif name == "Course":
                                    point_data["course"] = val_text
                                elif name == "Elevation":
                                    point_data["elevation"] = val_text
                                elif name == "Event":
                                    point_data["event"] = val_text

                    track_data.append(point_data)

        with open('track.json', 'w') as f:
            json.dump(track_data, f)
            
        print(f"Successfully processed {len(track_data)} track points.")

    except Exception as e:
        print(f"Error fetching or parsing track: {e}")

if __name__ == "__main__":
    fetch_and_parse()

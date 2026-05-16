import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Adjust the start date (?d1=) to the beginning of your voyage.
URL = "https://share.garmin.com/Feed/Share/Exodussail?d1=2026-04-01T00:00z"

def format_time(raw_time_str):
    """
    Converts Garmin's raw time string (e.g., "5/16/2026 8:39:30 AM") 
    into a stacked, localized string: "Sat, 16 May 2026 11:39:30 IDT (08:39:30 GMT)"
    """
    try:
        # 1. Parse Garmin's specific KML time format
        dt = datetime.strptime(raw_time_str, "%m/%d/%Y %I:%M:%S %p")
        
        # 2. Assign UTC timezone to the raw time
        dt_utc = dt.replace(tzinfo=ZoneInfo("UTC"))
        
        # 3. Convert to Local Time (Asia/Jerusalem will automatically handle IST/IDT daylight savings)
        dt_local = dt_utc.astimezone(ZoneInfo("Asia/Jerusalem"))
        
        # 4. Format into the exact string expected by the dashboard
        local_str = dt_local.strftime("%a, %d %b %Y %H:%M:%S %Z")
        gmt_str = dt_utc.strftime("%H:%M:%S GMT")
        
        return f"{local_str} ({gmt_str})"
        
    except ValueError:
        # Fallback just in case Garmin changes their format
        return raw_time_str


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

                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is not None:
                        for data in extended_data.findall('.//kml:Data', ns):
                            name = data.get('name')
                            val = data.find('kml:value', ns)
                            if val is not None and val.text:
                                val_text = val.text.strip()

                                if name == "Time":
                                    # Pass the raw time through our new formatter!
                                    point_data["time"] = format_time(val_text)
                                    
                                elif name == "Velocity":
                                    try:
                                        if "km/h" in val_text and "kn" not in val_text:
                                            kmh_value = float(''.join(c for c in val_text if c.isdigit() or c == '.'))
                                            knots_value = kmh_value / 1.852
                                            point_data["speed"] = f"{knots_value:.1f} kn ({kmh_value:.1f} km/h)"
                                            
                                        elif "kn" in val_text and "km/h" not in val_text:
                                            knots_value = float(''.join(c for c in val_text if c.isdigit() or c == '.'))
                                            kmh_value = knots_value * 1.852
                                            point_data["speed"] = f"{knots_value:.1f} kn ({kmh_value:.1f} km/h)"
                                            
                                        else:
                                            point_data["speed"] = val_text
                                            
                                    except ValueError:
                                        point_data["speed"] = val_text
                                        
                                elif name == "Course":
                                    # Removes the space before the degree symbol
                                    point_data["course"] = val_text.replace(" °", "°")
                                elif name == "Elevation":
                                    point_data["elevation"] = val_text
                                elif name == "Event":
                                    point_data["event"] = val_text

                    track_data.append(point_data)

        if not track_data:
            print("No track points found in feed.")
            return

        # --- THE OPTIMIZATION BLOCK ---
        # 1. Grab the very last point for the dashboard instruments
        latest_payload = track_data[-1]
        
        # 2. Strip all text out of the history array to save megabytes
        history_payload = [[pt["lat"], pt["lon"]] for pt in track_data]

        # 3. Assemble the final lightweight structure
        optimized_output = {
            "latest": latest_payload,
            "history": history_payload
        }

        with open('track.json', 'w') as f:
            # indent=None minimizes the JSON into a single tight line
            json.dump(optimized_output, f, separators=(',', ':'))
            
        print(f"Successfully processed {len(track_data)} track points into optimized JSON.")

    except Exception as e:
        print(f"Error fetching or parsing track: {e}")

if __name__ == "__main__":
    fetch_and_parse()

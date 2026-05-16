# Exodus Live Tracker

A lightweight, serverless live-tracking marine dashboard built for the Exodus by Daniel Pinsky or any other garmin tracker data.

This project integrates Garmin satellite data with the Windy API to provide family, friends, and crew with a real-time, interactive map of the vessel's location, speed, course, and local weather conditions.

## Features

* **Serverless Architecture:** Completely static frontend (index.html). All data processing is handled upstream to generate a microscopic, lightning-fast track.json file.
* **Glassmorphism UI:** A sleek, semi-transparent floating dashboard.
* **Pulsing Status Indicator:** An automated visual heartbeat indicating data freshness:
  * **Green (Pulsing):** Active tracking (pinged within the last 60 mins).
  * **Orange (Slow Pulse):** Stale data (missed recent pings, 1-24 hours old).
  * **Red (Solid):** Offline (no data for over 24 hours).
* **Smart Unit Conversion:** Automatically parses incoming Garmin speed data and stacks it cleanly as Knots (primary) and km/h (secondary).
* **Dual Timezones:** Bypasses browser defaults to stack the viewer's Local Time on top of the raw satellite GMT/UTC timestamp.
* **Mobile and Windy Optimized:** The dashboard is injected directly into Leaflet's native UI container.
* **Auto-Polling:** The map quietly fetches new coordinates every 30 seconds and repaints the vessel's route without refreshing the webpage.

## Tech Stack

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Mapping Engine:** Leaflet.js (v1.4.0)
* **Weather Overlay:** Windy Map API
* **Data Format:** JSON (track.json)

## Deployment (GitHub Pages)

This tracker is designed to be hosted entirely for free using GitHub Pages.

1. Clone or fork this repository.
2. Obtain a free API key from Windy API and replace '{{WINDY_KEY}}' in the index.html file with your actual key.
3. Ensure your upstream Garmin data pipeline is correctly outputting to track.json in the root directory.
4. Go to your repository settings on GitHub -> Pages.
5. Set the source to deploy from the main branch.
6. (Optional) Add your custom domain to the GitHub Pages settings.

## Local Testing & Development

If you are modifying the UI or testing data formats, you can run the tracker locally. Because of Cross-Origin Resource Sharing (CORS) security, you must run a local server rather than just double-clicking the HTML file.

1. Start a local Python server:
   Open your terminal, navigate to the project folder, and run:
   python3 -m http.server 8000

2. View on your computer:
   Open your browser and navigate to http://localhost:8000

3. Test on your mobile phone:
   To test the mobile UI and Windy menu overlays, ensure your phone is on the same Wi-Fi network as your computer.
   * Find your computer's local IP address.
   * On your phone's browser, navigate to: http://YOUR_LOCAL_IP:8000

## Expected track.json Data Structure

The frontend expects a continuous JSON array of location objects.

```json
[
  {
    "lat": 39.3000,
    "lon": 22.9000,
    "elevation": "0 m",
    "course": "45",
    "speed": "4.9 kn",
    "time": "2026-05-16 14:30:00 UTC",
    "event": "Tracking message received"
  }
]

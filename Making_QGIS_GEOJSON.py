#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 14:47:52 2026

@author: gregory
"""
'''
CONTAINS code to wrtie the position files in glapagos dataset into a CSV

Second- COntains code to write the recorded and interpolated position files into a vector that has interpolated time since start
    SO a colour map can be apply for time 
    Alongm with the location and type of trigger can somewhat clearly compare spacial and time of type of trigger
    
OUTPUTS GEOJSON file see the qgis project for the map of this 
'''
import re
import csv
import pandas as pd

input_file = "data/galapagos/mermaid10/m10_pos.txt"
output_file = "data/galapagos/mermaid10/m10_pos.csv"

current_dive = None

with open(input_file) as f, open(output_file, "w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["Dive", "Point", "DateUTC", "Lon", "Lat"])

    for line in f:
        line = line.strip()

        # Dive number line (001, 002, etc.)
        if re.fullmatch(r"\d{3}", line):
            current_dive = line
            continue

        # Data line
        m = re.match(
            r"(\w+)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|None)\s+(\S+)\s+(\S+)",
            line,
        )

        if m:
            point, date, lon, lat = m.groups()

            # Skip rows without coordinates
            if lon == "None" or lat == "None":
                continue

            writer.writerow([current_dive, point, date, lon, lat])

print(f"Saved to {output_file}")

# %% Sorting the csv

m10_pos = pd.read_csv('data/galapagos/mermaid10/m10_pos.csv')

position = m10_pos['DateUTC','Lon','Lat']


# %% code by ai to create the gradual but time stamp

from lxml import etree
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime
import json
import csv
import glob
import os

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

# --- point this at a folder containing all your station KML files ---
KML_DIR = 'data/location_data'
OUT_DIR = 'data/location_data'
kml_files = sorted(glob.glob(os.path.join(KML_DIR, '*.kml')))


def get_gps_records(kml_path):
    """Parse the 'GPS points' folder of one station's KML into (time, lon, lat) tuples."""
    tree = etree.parse(kml_path)
    root = tree.getroot()
    doc = root.find('kml:Document', ns)

    gps_folder = None
    for folder in doc.findall('kml:Folder', ns):
        name_el = folder.find('kml:name', ns)
        if name_el is not None and name_el.text and name_el.text.strip() == 'GPS points':
            gps_folder = folder
            break
    if gps_folder is None:
        return []

    records = []
    for pm in gps_folder.findall('kml:Placemark', ns):
        name_el = pm.find('kml:name', ns)
        coord_el = pm.find('.//kml:coordinates', ns)
        if name_el is None or coord_el is None or not name_el.text:
            continue
        try:
            ts = datetime.strptime(name_el.text.strip(), '%d/%m/%y %H:%M')
        except ValueError:
            continue
        lon, lat, *_ = [float(v) for v in coord_el.text.strip().split(',')]
        records.append((ts, lon, lat))

    records.sort(key=lambda r: r[0])
    return records


# --- pass 1: load every station, find the single earliest fix across ALL of them ---
station_records = {}
for path in kml_files:
    station = os.path.splitext(os.path.basename(path))[0]  # e.g. "m10"
    recs = get_gps_records(path)
    if recs:
        station_records[station] = recs

overall_start = min(recs[0][0] for recs in station_records.values())
print('Overall first fix across all stations:', overall_start)

# --- pass 2: export each station's interpolated trajectory, days measured from overall_start ---
all_segment_features = []

for station, records in station_records.items():
    times = np.array([r[0] for r in records])
    lons = np.array([r[1] for r in records])
    lats = np.array([r[2] for r in records])

    t_num = mdates.date2num(times)
    t_fine = np.linspace(t_num[0], t_num[-1], 2000)
    lon_fine = np.interp(t_fine, t_num, lons)
    lat_fine = np.interp(t_fine, t_num, lats)

    overall_start_num = mdates.date2num(overall_start)

    # per-station points CSV
    with open(f'{OUT_DIR}/{station}_trajectory_points.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['lon', 'lat', 'datetime_utc', 'days_since_overall_start', 'station'])
        for lon, lat, t in zip(lon_fine, lat_fine, t_fine):
            dt = mdates.num2date(t)
            w.writerow([lon, lat, dt.strftime('%Y-%m-%dT%H:%M:%S'),
                        round(t - overall_start_num, 4), station])

    # segments for this station, added into one combined GeoJSON for all stations
    for i in range(len(lon_fine) - 1):
        mid_t = (t_fine[i] + t_fine[i + 1]) / 2
        mid_dt = mdates.num2date(mid_t)
        all_segment_features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon_fine[i], lat_fine[i]], [lon_fine[i + 1], lat_fine[i + 1]]]
            },
            "properties": {
                "station": station,
                "datetime_utc": mid_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                "days_since_overall_start": round(mid_t - overall_start_num, 4)
            }
        })

geojson = {"type": "FeatureCollection", "features": all_segment_features}
with open(f'{OUT_DIR}/all_stations_trajectory_segments.geojson', 'w') as f:
    json.dump(geojson, f)

print(f'{len(station_records)} stations processed')
print(f'{len(all_segment_features)} total segments written')


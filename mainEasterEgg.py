import json
from shapely.geometry import shape, Polygon, Point, LineString, MultiLineString
import matplotlib.pyplot as plt
from collections import Counter

# === 1. Load the GeoJSON file ===
with open("grad-challenge.geojson", "r") as f:
    geojson_data = json.load(f)

print(f"📦 Total features loaded: {len(geojson_data['features'])}")

# === 2. Extract all coordinates from all geometry types ===
all_coords = []

for feature in geojson_data["features"]:
    geom_type = feature["geometry"]["type"]
    coords = feature["geometry"]["coordinates"]

    if geom_type == "LineString":
        all_coords.extend(coords)

    elif geom_type == "Polygon":
        all_coords.extend(coords[0])

    elif geom_type == "MultiLineString":
        for line in coords:
            all_coords.extend(line)

    elif geom_type == "Point":
        all_coords.append(coords)

# === 3. Calculate bounding box + padding ===
min_lon = min(coord[0] for coord in all_coords)
max_lon = max(coord[0] for coord in all_coords)
min_lat = min(coord[1] for coord in all_coords)
max_lat = max(coord[1] for coord in all_coords)

padding_lon = (max_lon - min_lon) * 0.05
padding_lat = (max_lat - min_lat) * 0.05

min_lon -= padding_lon
max_lon += padding_lon
min_lat -= padding_lat
max_lat += padding_lat

# === 4. Create the bounding polygon ===
polygon_coords = [
    (min_lon, max_lat),
    (min_lon, min_lat),
    (max_lon, min_lat),
    (max_lon, max_lat),
    (min_lon, max_lat)
]
bounding_polygon = Polygon(polygon_coords)

# === 5. Print geometry types ===
geom_types = Counter()
for feature in geojson_data["features"]:
    geom_types[feature["geometry"]["type"]] += 1
print("Geometry Types:", dict(geom_types))

# === 6. Check for out-of-bounds or tiny features ===
print("\n🔎 Suspicious Features:")
for i, feature in enumerate(geojson_data["features"]):
    geom = shape(feature["geometry"])
    if geom.geom_type == "Point":
        lon, lat = geom.x, geom.y
        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            print(f"⚠️ Point #{i} is out of bounds: ({lon}, {lat})")
    elif geom.geom_type in ["LineString", "MultiLineString"]:
        if geom.length < 0.00001:
            print(f"⚠️ Feature #{i} has tiny length: {geom.length}")
    elif geom.geom_type == "Polygon":
        if geom.area < 0.00000001:
            print(f"⚠️ Polygon #{i} has tiny area: {geom.area}")

# === 6.5 Optional: Print shortest and longest features by length ===
lines = []
for i, feature in enumerate(geojson_data["features"]):
    geom = shape(feature["geometry"])
    if geom.geom_type in ["LineString", "Polygon", "MultiLineString"]:
        try:
            lines.append((i, geom.length))
        except AttributeError:
            lines.append((i, 0))

lines.sort(key=lambda x: x[1])
print("\n🔎 Geometry Lengths:")
print("Top 5 shortest features:", lines[:5])
print("Top 5 longest features:", lines[-5:])

# === 7. Plot all features ===
fig, ax = plt.subplots(figsize=(10, 10))

for i, feature in enumerate(geojson_data["features"]):
    geom = shape(feature["geometry"])

    if geom.geom_type == "LineString":
        x, y = geom.xy
        ax.plot(x, y, color="blue")

    elif geom.geom_type == "Polygon":
        x, y = geom.exterior.xy
        ax.plot(x, y, color="blue")

    elif geom.geom_type == "Point":
        ax.plot(geom.x, geom.y, 'ro', markersize=5)

    elif geom.geom_type == "MultiLineString":
        for line in geom:
            x, y = line.xy
            ax.plot(x, y, color="green")

# === 8. Plot the bounding box ===
box_x, box_y = bounding_polygon.exterior.xy
ax.plot(box_x, box_y, linestyle="--", color="red")

# Zoomed out to catch anything on the edges
ax.set_xlim(min_lon - 0.0005, max_lon + 0.0005)
ax.set_ylim(min_lat - 0.0005, max_lat + 0.0005)

plt.title("Full GeoJSON Scan with Auto Bounding Box")
plt.axis("equal")
plt.show()

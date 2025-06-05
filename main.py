import json
from shapely.geometry import shape, Polygon
import matplotlib.pyplot as plt

# 1. Load your GeoJSON file
with open("grad-challenge.geojson", "r") as f:
    geojson_data = json.load(f)

# 2. Collect all coordinates from LineString and Polygon features
all_coords = []

for feature in geojson_data["features"]:
    geom_type = feature["geometry"]["type"]
    coords = feature["geometry"]["coordinates"]

    if geom_type == "LineString":
        all_coords.extend(coords)

    elif geom_type == "Polygon":
        all_coords.extend(coords[0])  # Polygons are nested

    elif geom_type == "MultiLineString":
        for line in coords:
            all_coords.extend(line)

# 3. Calculate the bounding box
min_lon = min(coord[0] for coord in all_coords)
max_lon = max(coord[0] for coord in all_coords)
min_lat = min(coord[1] for coord in all_coords)
max_lat = max(coord[1] for coord in all_coords)

# Optional: Add some padding (5% of range)
padding_lon = (max_lon - min_lon) * 0.05
padding_lat = (max_lat - min_lat) * 0.05

min_lon -= padding_lon
max_lon += padding_lon
min_lat -= padding_lat
max_lat += padding_lat

# 4. Define bounding polygon using auto-detected bounds
polygon_coords = [
    (min_lon, max_lat),  # top-left
    (min_lon, min_lat),  # bottom-left
    (max_lon, min_lat),  # bottom-right
    (max_lon, max_lat),  # top-right
    (min_lon, max_lat)   # close polygon
]
bounding_polygon = Polygon(polygon_coords)

# 5. Filter features that intersect with the bounding polygon
inside_features = []
for feature in geojson_data["features"]:
    geom = shape(feature["geometry"])
    # if geom.intersects(bounding_polygon):
        inside_features.append(geom)

# 6. Plot the features inside the bounding box
fig, ax = plt.subplots(figsize=(8, 8))
for geom in inside_features:
    if geom.geom_type == "LineString":
        x, y = geom.xy
        ax.plot(x, y, color="blue")
    elif geom.geom_type == "Polygon":
        x, y = geom.exterior.xy
        ax.plot(x, y, color="blue")

# Draw the bounding polygon
box_x, box_y = bounding_polygon.exterior.xy
ax.plot(box_x, box_y, color='red', linestyle='--')

plt.title("Auto-Detected Bounding Box for GeoJSON")
plt.axis("equal")
plt.show()

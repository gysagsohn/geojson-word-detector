import json
from shapely.geometry import shape, Polygon
import matplotlib.pyplot as plt

# 1. Load the GeoJSON file
with open("grad-challenge.geojson", "r") as f:
    geojson_data = json.load(f)

# 2. Define the fixed bounding polygon from the question
polygon_coords = [
    (151.19982759600163, -33.889076995548066),
    (151.19982759600163, -33.88917835060116),
    (151.20015211737098, -33.88917835060116),
    (151.20015211737098, -33.889076995548066),
    (151.19982759600163, -33.889076995548066)
]
bounding_polygon = Polygon(polygon_coords)

# 3. Filter features that intersect with the bounding polygon
inside_features = []
for feature in geojson_data["features"]:
    geom = shape(feature["geometry"])
    if geom.intersects(bounding_polygon):
        inside_features.append(geom)

# 4. Plot the result
fig, ax = plt.subplots(figsize=(8, 8))
for geom in inside_features:
    if geom.geom_type == "LineString":
        x, y = geom.xy
        ax.plot(x, y, color="blue")
    elif geom.geom_type == "Polygon":
        x, y = geom.exterior.xy
        ax.plot(x, y, color="blue")  # draw polygon outline

# Draw the bounding polygon
poly_x, poly_y = bounding_polygon.exterior.xy
ax.plot(poly_x, poly_y, linestyle="--", color="red")

plt.title("Features Inside Fixed Polygon (from question)")
plt.axis("equal")
plt.show()

import pandas as pd
import os
import json

id_path = "../data/archive/NYC_subway_traffic_2017-2021.csv"
subway_data = pd.read_csv(id_path)
# 根据Unique ID进行去重
subway_data = subway_data.drop_duplicates(subset=["Unique ID"])
# 只保留unique id和经纬度
subway_data = subway_data[["Unique ID", "Latitude", "Longitude"]]

name_path = "../../Front/src/data/stations.geojson"
json_data = open(name_path).read()
data = json.loads(json_data)

# 提取所需信息
id_coordinates_mapping = {}
for feature in data["features"]:
    id = feature["properties"]["id"]
    coordinates = feature["geometry"]["coordinates"]
    id_coordinates_mapping[id] = coordinates

# 计算每个unique id最近的地铁站名，并将其存储在一个新的DataFrame中
id_name_mapping = {}
for id, coordinates in id_coordinates_mapping.items():
    min_distance = float("inf")
    closest_station = None
    for index, row in subway_data.iterrows():
        distance = (row["Latitude"] - coordinates[1]) ** 2 + (
            row["Longitude"] - coordinates[0]
        ) ** 2
        if distance < min_distance:
            min_distance = distance
            closest_station = row["Unique ID"]
    id_name_mapping[id] = closest_station

id_name_df = pd.DataFrame(
    id_name_mapping.items(), columns=["Unique ID", "Closest Station"]
)
id_name_df.to_csv("../data/id_name_map.csv", index=False)

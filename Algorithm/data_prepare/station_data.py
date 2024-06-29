import os
import pandas as pd
from tqdm import tqdm

# 设置路径
path = "../data/station_info"
map_path = "../data/id_name_map.csv"
# 初始化一个空的DataFrame，用于存储所有数据
all_data = pd.DataFrame(columns=["Unique ID", "Datetime", "Entries", "Exits"])

name_id_path = "../data/id_name_map.csv"
map_data = pd.read_csv(name_id_path)
# 把map_data转为map
id_name_mapping = {}
for index, row in map_data.iterrows():
    id_name_mapping[row["Closest Station"]] = row["Unique ID"]

# 处理文件
files = os.listdir(path)
for file in tqdm(files, desc="Processing files"):
    df = pd.read_csv(
        os.path.join(path, file),
        usecols=["Unique ID", "Datetime", "Entries", "Exits"],
    )
    all_data = pd.concat([all_data, df], ignore_index=True)

# 加入name列
all_data["Name"] = all_data["Unique ID"].map(id_name_mapping)
# 删除没有name的行
all_data = all_data.dropna(subset=["Name"])


# 将所有数据导出到新的CSV文件
all_data.to_csv("../data/all_station_info.csv", index=False)

import pandas as pd
import numpy as np
from tqdm import tqdm

# 读取数据
df = pd.read_csv('subway_data.csv')

# 将Datetime列转换为datetime类型，指定dayfirst=True，errors='coerce'将无效日期设置为NaT
df['Datetime'] = pd.to_datetime(df['Datetime'], dayfirst=True, errors='coerce')

# 删除无效日期行
df = df.dropna(subset=['Datetime'])

# 设置每4小时的时间间隔
time_interval = pd.Timedelta(hours=4)

# 定义函数以填补缺失时间段
def fill_missing_times(df, time_interval):
    # 初始化一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=df.columns)

    # 获取所有站点的Unique ID
    unique_ids = df['Unique ID'].unique()

    for unique_id in tqdm(unique_ids, desc="Processing stations"):
        station_data = df[df['Unique ID'] == unique_id].sort_values('Datetime')

        # 生成完整的时间序列
        start_time = station_data['Datetime'].min()
        end_time = station_data['Datetime'].max()
        full_time_range = pd.date_range(start=start_time, end=end_time, freq=time_interval)

        # 将站点数据的索引设置为Datetime
        station_data.set_index('Datetime', inplace=True)

        # 重新索引以包含完整的时间范围
        station_data = station_data.reindex(full_time_range)

        # 填充缺失的Unique ID和Name列
        station_data['Unique ID'] = unique_id
        station_data['Name'] = station_data['Name'].ffill().bfill()

        # 填充Entries和Exits列
        station_data['Entries'] = station_data['Entries'].interpolate(method='linear')
        station_data['Exits'] = station_data['Exits'].interpolate(method='linear')

        # 重置索引
        station_data.reset_index(inplace=True)
        station_data.rename(columns={'index': 'Datetime'}, inplace=True)

        # 将结果添加到结果DataFrame中
        result_df = pd.concat([result_df, station_data], ignore_index=True)

    return result_df

# 调用函数填补缺失时间段
filled_df = fill_missing_times(df, time_interval)

# 将结果保存到新的CSV文件中
filled_df.to_csv('filled_subway_data.csv', index=False)

print("缺失数据已填补并保存到 filled_subway_data.csv 文件中。")

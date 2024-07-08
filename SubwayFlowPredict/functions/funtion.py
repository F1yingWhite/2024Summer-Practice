import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import haversine
import pytz

# The number of CPU threads to use for multithreaded operations
N_THREADS = 1


# Haversine distance function definition
def haversine_distance(x):
    a_lat, a_lon, b_lat, b_lon = x[0]
    return haversine.haversine((a_lat, a_lon), (b_lat, b_lon))


# Multithreaded apply function for a dataframe. This uses multiprocessing to map a function to a series,
# vastly speeding up feature generation
def apply_multithreaded(data, func):
    # pool = multiprocessing.Pool(N_THREADS)  # Spawn a pool of processes
    data = data.values  # Retrieve a numpy array which can be iterated over

    result = func(data)  # Map the function over the data multi-threaded
    # pool.close()  # Close the threads
    return result


def preprocess_data(data, history_data, group_counts, db):
    sql = """
    select * from id_map"""

    db.is_connected()
    # 获取所有记录列表
    results = db.query(sql)
    # 转换为 DataFrame
    other_data = pd.DataFrame(results)
    columns_to_exclude = ['GTFS_Stop_ID']  # 替换为

    # 获取需要转换的列
    columns_to_convert = other_data.columns.difference(columns_to_exclude)

    # 将选中的列转换为float类型
    other_data[columns_to_convert] = other_data[columns_to_convert].astype(float)
    other_data['id'] = other_data['id'].astype(int)

    # 增加name列
    history_data = history_data.merge(other_data[['id', 'GTFS_Stop_ID']], on='id', how='left')
    # 重命名列
    history_data.rename(columns={'GTFS_Stop_ID': 'name'}, inplace=True)
    other_data.set_index('id', inplace=True)
    # 示例：假设输入数据为字典列表
    df = pd.DataFrame(data)
    # 获取纽约时区的当前时间
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)

    # 更新数据框中的各列
    df['month'] = now.month
    df['Week'] = now.weekday()
    df['holidays'] = 1 if now.month >= 5 else 0
    df['Time'] = now.hour
    df['Exits'] = 0
    df['Entries'] = 0

    # 为每个站点生成6个时间点的数据
    all_data = []
    for row in group_counts.itertuples():
        # 生成具体每个时间点的数据
        for hour in range(0, 21, 4):  # 从0到20点，每4小时一个点
            temp = df.copy()
            temp['Latitude'] = row.Latitude
            temp['Longitude'] = row.Longitude
            temp['Time'] = hour
            temp['Car-free Commute'] = other_data['Car-free Commute'][int(row.id)]
            temp['Born in NY State'] = other_data['Born in NY State'][int(row.id)]
            temp['Building Permits'] = other_data['Building Permits'][int(row.id)]
            temp['Foreign-born Population'] = other_data['Foreign-born Population'][int(row.id)]
            temp['id'] = row.id
            temp['Name'] = other_data['GTFS_Stop_ID'][int(row.id)]
            all_data.append(temp)

    # 将所有生成的数据合并为一个DataFrame
    result_df = pd.concat(all_data, ignore_index=True)
    combined_data = pd.concat([history_data, result_df], ignore_index=True)
    sorted_grouped_data = combined_data.groupby(['Latitude', 'Longitude']).apply(
        lambda x: x.sort_values(by='time')).reset_index(drop=True)
    sorted_grouped_data['series'] = sorted_grouped_data['Latitude'].astype(str) + "_" + sorted_grouped_data[
        'Longitude'].astype(str)
    sorted_grouped_data.reset_index(drop=True, inplace=True)
    sorted_grouped_data['IDX'] = sorted_grouped_data.index  # 使用 DataFrame 的索引作为 ID
    group_info = sorted_grouped_data.groupby(['Name', 'id']).size().reset_index(name='count')
    return sorted_grouped_data, now, group_info


def training(predict_data):
    from pytorch_forecasting import TimeSeriesDataSet
    max_encoder_length = 6 * 7 * 4
    max_prediction_length = 6
    # 创建数据集
    training = TimeSeriesDataSet(
        predict_data,
        time_idx="IDX",
        target=["Entries", "Exits"],
        group_ids=["series"],
        allow_missing_timesteps=True,
        min_encoder_length=1,
        max_encoder_length=max_encoder_length,
        min_prediction_length=1,
        max_prediction_length=max_prediction_length,
        static_categoricals=["series"],
        time_varying_known_reals=["Week", "holidays", "Time", "month"],
        time_varying_unknown_reals=[
            "Weather Encoded", "Max Temp", "Min Temp", "Wind",
            "Car-free Commute", "Born in NY State", "Building Permits", "Foreign-born Population", 'Latitude',
            'Longitude'
        ],
        add_encoder_length=True,
        add_relative_time_idx=True,
        add_target_scales=True
    )
    return training


def load_data(db):
    # 获取纽约时区
    ny_tz = pytz.timezone('America/New_York')

    # 获取纽约时区的明天凌晨的时间戳
    tomorrow = datetime.now(ny_tz) + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_timestamp = int(tomorrow.timestamp()) - 1

    # 获取纽约时区的 28 天前的时间戳
    thirty_days_ago = datetime.now(ny_tz) - timedelta(days=28)
    thirty_days_ago = thirty_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago_timestamp = int(thirty_days_ago.timestamp())

    # SQL 查询语句
    sql = f"""
    SELECT * 
    FROM processed_subway_data_future 
    WHERE time_idx BETWEEN {thirty_days_ago_timestamp} AND {tomorrow_timestamp}
    """

    db.is_connected()  
    # 获取所有记录列表
    results = db.query(sql)
    # 转换为 DataFrame
    data = pd.DataFrame(results)
    # 指定不需要转换为float的列
    columns_to_exclude = ['series']  # 请替换为实际列名

    # 获取需要转换的列
    columns_to_convert = data.columns.difference(columns_to_exclude)

    # 将选中的列转换为float类型
    data[columns_to_convert] = data[columns_to_convert].astype(float)

    data['time_idx'] = data['time_idx'].astype(int)
    data['time'] = pd.to_datetime(data['time_idx'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
    data['id'] = data['id'].astype(int)

    one_week_data_excluding_today = data.sort_values(by='id')
    sorted_grouped_data = one_week_data_excluding_today.groupby(['Latitude', 'Longitude']).apply(
        lambda x: x.sort_values(by='time')).reset_index(drop=True)
    filtered_data = sorted_grouped_data.drop_duplicates(subset=['Latitude', 'Longitude', 'month', 'Time', 'day'],
                                                        keep='first')
    group_counts = filtered_data.groupby(['Latitude', 'Longitude', 'id']).size().reset_index(name='count')
    return filtered_data, group_counts

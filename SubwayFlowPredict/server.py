import pickle
import logging
from datetime import timedelta
from flask_cors import CORS  # 导入 CORS
from pytorch_forecasting import TemporalFusionTransformer
from flask import Flask, jsonify, request
from pytorch_forecasting import TimeSeriesDataSet
from models import LSTM, CNN, RNN, GRU, CNN_LSTM, AttentionLSTM, SEQ2SEQ
from functions.funtion import preprocess_data, training, load_data, apply_multithreaded, haversine_distance
import pymysql
import xgboost as xgb
import pandas as pd
import numpy as np
from functions.utils import DataSource

# 加载模型
model_path = './save/checkpoints/epoch=16-step=11186.ckpt'
model = TemporalFusionTransformer.load_from_checkpoint(model_path)
model.eval()

hourly_speed_fill = 0.004006452469829587  #填充速度
# 加载保存的模型
xgb_model = xgb.Booster()
xgb_model.load_model('./saveModels/xgb/model_optim.mdl')
# 创建Flask应用程序
app = Flask(__name__)
CORS(app)  # 应用 CORS 到 Flask 应用
db = DataSource()

# 加载保存的目标编码器
with open('./saveModels/encoder/target_encoder.pkl', 'rb') as f:
    encoder = pickle.load(f)

max_encoder, min_encoder = 886902.6424518436, 423785.9913568781
# 配置日志记录
logging.basicConfig(level=logging.DEBUG)


# 定义API路由
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 从请求中获取数据
        data = request.json
        df = pd.DataFrame(columns=['天气'])
        # 添加单个值
        df.loc[len(df)] = [data['Weather Encoded']]
        #对天气进行目标编码
        t = encoder.transform(df['天气'])
        data['Weather Encoded'] = (t['天气'][0] - min_encoder) / (max_encoder - min_encoder)
        # 假设 preprocess_data 和 training 函数是导入自其他模块的预处理和训练函数
        history_data, group_counts = load_data(db)
        processed_data, now, group_info = preprocess_data([data], history_data, group_counts, db)

        trained_model = training(processed_data)

        # 假设 model 是你预训练好的 TemporalFusionTransformer 模型
        predict_dataset = TimeSeriesDataSet.from_dataset(trained_model, processed_data, predict=True,
                                                         stop_randomization=True)
        predict_dataloader = predict_dataset.to_dataloader(train=False, batch_size=64)

        # 假设 model.predict 返回的是一个 tensor，predictions 是预测结果的一个值
        predictions = model.predict(predict_dataloader)
        prediction_value = {
            'Entries': abs(predictions[0].cpu().detach().numpy()).tolist(),
            'Exits': abs(predictions[1].cpu().detach().numpy()).tolist()
        }

        # 预测的时间点
        hours = ['00:00:00', '04::00:00', '08:00:00', '12:00:00', '16:00:00', '20:00:00']

        # 创建最终数据列表
        final_data = []
        # 将日期部分向后推一天
        next_day = now + timedelta(days=1)
        for index, row in group_info.iterrows():
            if index >= len(min(prediction_value['Entries'], prediction_value['Exits'])):
                break
            for hour_index, hour in enumerate(hours):
                data_row = {
                    'id': row['id'],
                    'name': row['Name'],
                    'DateTime': str(next_day.strftime('%Y-%m-%d')) + ' ' + hour,
                    'Entries': int(prediction_value['Entries'][index][hour_index]),
                    'Exits': int(prediction_value['Exits'][index][hour_index])
                }
                final_data.append(data_row)
        final_data = pd.DataFrame(final_data)
        final_data.rename(columns={'id': 'Unique ID'}, inplace=True)
        success = db.insert_dataframe(final_data, 'new_all_station_info')
        if success:
            return jsonify({'msg': '插入成功'})
        else:
            return jsonify({'msg': '插入失败'})


    except pymysql.Error as e:

        print("Database error:", e)
        return jsonify({'error': str(e)}), 500

    except Exception as e:

        print("Error:", e)
        # 捕获异常，并返回错误信息
        return jsonify({'error': str(e)}), 500


@app.route('/predict_duration', methods=['POST'])
def predict_duration():
    try:
        data = request.json
        data = pd.DataFrame([data]).astype(float)
        data['unix_time'] = data['unix_time'].astype(int)
        timestamp = pd.to_datetime(data['unix_time'], unit='s')
        data['daily_minute'] = timestamp.dt.hour * 60 + timestamp.dt.minute
        data['day_of_week'] = timestamp.dt.dayofweek

        #计算欧几里得、曼哈顿，哈夫赛因距离
        data['dist_l1'] = np.abs(data['pickup_latitude'] - data['dropoff_latitude']) + np.abs(
            data['pickup_longitude'] - data['dropoff_longitude'])
        data['dist_l2'] = np.sqrt((data['pickup_latitude'] - data['dropoff_latitude']) ** 2 + (
                data['pickup_longitude'] - data['dropoff_longitude']) ** 2)
        # As haversine is not vectorised, we use the multithreading approach for speed
        data['dist_haversine'] = apply_multithreaded(
            data[['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']], haversine_distance)

        # 这里计算了行程方向的纬度差和经度差，以及角度（行程方向的角度）。
        data['delta_lat'] = data['dropoff_latitude'] - data['pickup_latitude']
        data['delta_lon'] = data['dropoff_longitude'] - data['pickup_longitude']
        data['angle'] = (180 / np.pi) * np.arctan2(data['delta_lat'], data['delta_lon']) + 180
        d_new = xgb.DMatrix(data)
        # 进行预测
        predictions = xgb_model.predict(d_new)
        print(predictions[0])
        # 返回预测结果
        return jsonify({'prediction': float(np.expm1(predictions[0]))})
    except Exception as e:
        # 捕获异常，并返回错误信息
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'msg': 'Hello World!'})
# 运行应用程序
if __name__ == '__main__':
    app.run(debug=True, port=8080)

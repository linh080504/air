from flask import Flask, render_template, jsonify
import requests
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
from datetime import datetime

app = Flask(__name__)

# ThingSpeak API thông tin
CHANNEL_ID = '2886155'
READ_API_KEY = '53SYKPEROI721J6B'

# Hàm lấy dữ liệu từ ThingSpeak, lấy tất cả các bản ghi
def fetch_all_data():
    url = f'https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=50'  # Lấy 50 bản ghi gần nhất
    response = requests.get(url)
    return response.json()['feeds']  # Trả về tất cả dữ liệu

# Hàm lấy dữ liệu mới nhất
def fetch_latest_data():
    all_data = fetch_all_data()
    return all_data[-1]  # Trả về bản ghi mới nhất

# Hàm tạo biểu đồ cho tất cả dữ liệu
def create_chart(data, field, field_name):
    time_labels = [datetime.strptime(feed['created_at'], '%Y-%m-%dT%H:%M:%SZ') for feed in data]  # Chuyển đổi thành datetime
    field_data = []

    # Kiểm tra giá trị từng trường, thay None thành 0 hoặc giá trị mặc định
    for feed in data:
        value = feed.get(f'field{field}', None)
        if value is None:
            field_data.append(0)  # Hoặc thay bằng giá trị mặc định khác nếu cần
        else:
            field_data.append(float(value))  # Chuyển đổi thành float nếu có giá trị

    plt.figure(figsize=(10, 6))
    plt.plot(time_labels, field_data, marker='o', color='r', label=f'{field_name}')
    plt.xlabel('Date')
    plt.ylabel(f'{field_name}')
    plt.title(f'{field_name} Data')
    plt.xticks(rotation=45)

    # Thiết lập trục x cho ngày tháng chỉ hiển thị ngày và tháng
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    # Tùy chỉnh kiểu tooltip cho điểm dữ liệu
    plt.tight_layout()

    # Lưu biểu đồ vào bộ nhớ
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/')
def index():
    all_data = fetch_all_data()  # Lấy tất cả dữ liệu
    latest_data = fetch_latest_data()  # Lấy dữ liệu mới nhất

    # Tạo biểu đồ cho tất cả 6 trường dữ liệu
    charts = []
    fields = ["PM2.5", "PM10", "Temperature", "Humidity", "CO", "Smoke"]
    for i, field_name in enumerate(fields, 1):
        chart = create_chart(all_data, i, field_name)  # Tạo biểu đồ với tất cả dữ liệu cho từng trường
        charts.append(chart)

    return render_template('index.html', data=latest_data, charts=charts)

if __name__ == '__main__':
    app.run(debug=True)

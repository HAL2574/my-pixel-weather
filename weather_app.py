import streamlit as st
import requests
import random
import base64
from PIL import Image
import io

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# --- 2. 都市選択 ---
city_map = {
    "札幌": "Sapporo", "旭川": "Asahikawa", "帯広": "Obihiro",
    "小樽": "Otaru", "東京": "Tokyo", "ロンドン": "London", "ハワイ": "Honolulu"
}
selected_city_jp = st.selectbox("都市を選択してください", options=list(city_map.keys()), index=0)

# --- 3. データ取得 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"
city_en = city_map[selected_city_jp]
url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&lang=ja&units=metric"

data = None
try:
    res = requests.get(url, timeout=5)
    if res.status_code == 200: data = res.json()
except: pass

# --- 4. 描画処理 ---
if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    
    themes = {
        "Clear":  {"bg": "#87CEEB", "img": "sunny.gif", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.gif", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.gif", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.gif", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    # --- 5. CSS & HTML (情報を下に集約) ---
    st.markdown(f"""
        <style>
        .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        header {{ visibility: hidden; display: none; }}
        [data-testid="stHeader"] {{ display: none; }}
        
        .weather-screen {{
            position: relative;
            width: 100vw;
            height: 85vh; /* iPhoneの画面に合わせて微調整 */
            overflow: hidden;
            background-color: {selected['bg']};
        }}
        
        .bg-gif {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* 情報を画面下部にまとめるエリア */
        .info-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 30px 20px 40px 20px; /* 下側に余裕を持たせる */
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.7)); /* 下にいくほど暗くなるグラデーション */
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            z-index: 100;
        }}

        .city-box {{ text-align: left; }}
        .city-name {{ font-size: 20px; opacity: 0.9; }}
        .weather-desc {{ font-size: 32px; font-weight: bold; }}

        .temp-box {{ text-align: right; }}
        .temp-val {{ font-size: 64px; font-weight: bold; line-height: 1; }}
        </style>

        <div class="weather-screen">
            <img src="data:image/gif;base64,{img_b64}" class="bg-gif">
            <div class="info-overlay">
                <div class="city-box">
                    <div class="city-name">{selected_city_jp}</div>
                    <div class="weather-desc">{selected['txt']}</div>
                </div>
                <div class="temp-box">
                    <div class="temp-val">{temp}℃</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。")

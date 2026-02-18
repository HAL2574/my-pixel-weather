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
        # GIFアニメーションをバイナリとして読み込む
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

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
    
    # 天気ごとの設定 (gifファイルを読み込むように変更)
    themes = {
        "Clear":  {"bg": "#87CEEB", "img": "sunny.gif", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.gif", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.gif", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.gif", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    # --- 5. HTML/CSS (情報をすべてドット絵に重ねる) ---
    st.markdown(f"""
        <style>
        .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        header {{ visibility: hidden; display: none; }}
        [data-testid="stHeader"] {{ display: none; }}
        
        /* 全画面カード */
        .weather-screen {{
            position: relative;
            width: 100vw;
            height: 90vh; /* 画面のほぼすべてをドット絵に */
            overflow: hidden;
            background-color: {selected['bg']};
        }}
        
        .bg-gif {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* 全情報をドット絵の上に浮かせる */
        .overlay-content {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            text-align: center;
            z-index: 100;
            background: rgba(0, 0, 0, 0.1); /* 少しだけ暗くして文字を見やすく */
        }}

        .city-label {{ font-size: 24px; margin-bottom: 5px; text-shadow: 2px 2px 8px rgba(0,0,0,0.8); }}
        .temp-label {{ font-size: 90px; font-weight: bold; text-shadow: 3px 3px 15px rgba(0,0,0,0.8); }}
        .desc-label {{ font-size: 28px; margin-top: 10px; background: rgba(255,255,255,0.2); padding: 5px 20px; border-radius: 50px; }}
        </style>

        <div class="weather-screen">
            <img src="data:image/gif;base64,{img_b64}" class="bg-gif">
            <div class="overlay-content">
                <div class="city-label">{selected_city_jp}</div>
                <div class="temp-label">{temp}℃</div>
                <div class="desc-label">{selected['txt']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。")

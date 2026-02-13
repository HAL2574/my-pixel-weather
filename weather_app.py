import streamlit as st
import requests
import datetime
import random
import base64
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# 画像をWebで表示できる形式に変換する関数
def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# 全画面表示のためのCSS
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    .main-container {
        position: relative; width: 100vw; height: 100vh;
        background-color: white; overflow: hidden;
    }
    .image-box {
        position: relative; width: 100%; height: 75vh;
        overflow: hidden;
    }
    .pixel-img {
        width: 100%; height: 100%; object-fit: cover;
    }
    .temp-txt {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 70px; font-weight: bold;
        text-shadow: 3px 3px 10px rgba(0,0,0,0.7); z-index: 10;
    }
    .info-box {
        height: 25vh; padding: 20px; background: white;
    }
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; }
    @keyframes fall { to { transform: translateY(80vh); } }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None
    except: return None

# 検索入力
city = st.text_input("都市名を入力してね", value="Tokyo")
data = get_weather(city)

if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    
    # テーマ判定
    themes = {
        "Clear":  {"bg": "#FFD700", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    
    # 画像をエンコード
    img_b64 = get_image_base64(selected["img"])

    # 雪エフェクト (Snowの時だけ)
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(20):
            left, dur = random.randint(0, 100), random.uniform(4, 8)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # 画面描画
    st.markdown(f"""
        <div class="main-container">
            <div class="image-box" style="background-color: {selected['bg']};">
                <img src="data:image/png;base64,{img_b64}" class="pixel-img">
                {effect_html}
                <div class="temp-txt">{temp}℃</div>
            </div>
            <div class="info-box">
                <h1 style="margin:0;">天気: {selected['txt']}</h1>
                <p style="color:gray;">{city} の現在の気温</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("都市名を確認してね！")

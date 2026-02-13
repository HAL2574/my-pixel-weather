import streamlit as st
import requests
import datetime
import random
import os

# --- ページ設定 (余白をなくす) ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# iPhoneで見た時に隙間をゼロにする魔法のCSS
st.markdown("""
    <style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .stApp { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None
    except: return None

city = st.text_input("都市名", value="Tokyo")
data = get_weather(city)

if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    rain = data.get('rain', {}).get('1h', 0)
    snow = data.get('snow', {}).get('1h', 0)
    
    is_night = datetime.datetime.now().hour >= 18 or datetime.datetime.now().hour < 6
    
    themes = {
        "Clear":  {"day": "#FFD700", "night": "#191970", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"day": "#4682B4", "night": "#2F4F4F", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"day": "#E0FFFF", "night": "#4B0082", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"day": "#A9A9A9", "night": "#696969", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    bg_color = selected["night"] if is_night else selected["day"]

    # エフェクト
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(30):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(50):
            left, dur = random.randint(0, 100), random.uniform(0.5, 1)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # 画像のURLを取得 (GitHubから直接読み込む)
    img_url = f"https://raw.githubusercontent.com/hal2574/my-pixel-weather/main/{selected['img']}"

    # メインビジュアル
    st.markdown(f"""
        <style>
        .weather-card {{
            position: relative; width: 100vw; height: 110vw;
            background-color: {bg_color}; overflow: hidden;
            display: flex; justify-content: center; align-items: center;
        }}
        .bg-img {{
            position: absolute; width: 100%; height: 100%;
            object-fit: cover;
        }}
        .temp {{
            position: relative; color: white; font-size: 80px; font-weight: bold;
            text-shadow: 3px 3px 10px rgba(0,0,0,0.5); z-index: 10;
        }}
        .snow {{ position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; }}
        .rain {{ position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; }}
        @keyframes fall {{ to {{ transform: translateY(120vw); }} }}
        </style>
        <div class="weather-card">
            <img src="{img_url}" class="bg-img">
            {effect_html}
            <div class="temp">{temp}℃</div>
        </div>
    """, unsafe_allow_html=True)

    # ステータスエリア
    st.markdown(f"""
        <div style="padding: 20px;">
            <h2 style="margin:0;">天気: {selected['txt']}</h2>
            <p style="font-size: 18px; color: gray;">気温: {temp}℃ / 降水量: {max(rain, snow)} mm/h</p>
        </div>
    """, unsafe_allow_html=True)

import streamlit as st
import requests
import datetime
import random
import os
from PIL import Image

# --- ページ設定 ---
st.set_page_config(page_title="Pixel Weather", page_icon="❄️")

# CSSでiPhone向けに見た目を調整
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- UI部分 ---
city = st.text_input("都市名を入力 (例: Tokyo, Sapporo)", value="Tokyo")
data = get_weather(city)

if data:
    weather_main = data['weather'][0]['main']
    temp = data['main']['temp']
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

    # エフェクト生成
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(30):
            left, dur, delay = random.randint(0, 100), random.uniform(3, 7), random.uniform(0, 5)
            effect_html += f'<div class="particle" style="left:{left}%; width:5px; height:5px; background:white; border-radius:50%; animation-duration:{dur}s; animation-delay:{delay}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(50):
            left, dur = random.randint(0, 100), random.uniform(0.5, 1)
            effect_html += f'<div class="particle" style="left:{left}%; width:2px; height:15px; background:#ADD8E6; animation-duration:{dur}s;"></div>'

    # メイン画面のHTML
    st.markdown(f"""
        <style>
        .weather-box {{
            position: relative; width: 100%; height: 450px;
            background-color: {bg_color}; overflow: hidden; border-radius: 15px;
            display: flex; justify-content: center; align-items: center;
        }}
        .pixel-img {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }}
        .temp-display {{ color: white; font-size: 60px; font-weight: bold; z-index: 10; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .particle {{ position: absolute; top: -20px; animation: fall linear infinite; }}
        @keyframes fall {{ to {{ transform: translateY(500px); }} }}
        </style>
        <div class="weather-box">
            <img src="https://raw.githubusercontent.com/{st.runtime.exists() and st.get_option('server.baseUrlPath') or 'hal2574'}/my-pixel-weather/main/{selected['img']}" class="pixel-img">
            {effect_html}
            <div class="temp-display">{temp}℃</div>
        </div>
    """, unsafe_allow_html=True)

    # 下部ステータス
    st.write(f"### 天気: {selected['txt']}")
    st.write(f"降水量: {max(rain, snow)} mm/h")
else:
    st.warning("都市データが見つかりませんでした。")

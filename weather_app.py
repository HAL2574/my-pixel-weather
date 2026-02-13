import streamlit as st
import requests
import datetime
import random

# --- ページ設定 (タイトルと全幅レイアウト) ---
st.set_page_config(page_title="Pixel Weather", layout="wide")

# iPhoneの画面いっぱいに表示するための究極のCSS調整
st.markdown("""
    <style>
    /* 全体の余白をゼロにする */
    .block-container { padding: 0 !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* 入力欄のスタイル */
    .stTextInput { position: absolute; top: 10px; left: 10px; z-index: 100; width: 120px !important; opacity: 0.8; }
    
    /* 天気カードのメインコンテナ (画面高さ100%を目指す) */
    .weather-full-card {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        overflow: hidden; display: flex; flex-direction: column;
    }
    
    /* 画像エリア (画面の80%を占有) */
    .image-area {
        position: relative; width: 100%; height: 75vh;
        background-position: center; background-size: cover;
    }
    
    .pixel-bg {
        width: 100%; height: 100%; object-fit: cover;
    }

    /* 気温のオーバーレイ */
    .temp-overlay {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 80px; font-weight: bold;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.6); z-index: 50;
    }

    /* 情報エリア (下の白い部分) */
    .info-area {
        height: 25vh; background: white; padding: 20px;
        display: flex; flex-direction: column; justify-content: center;
    }

    /* エフェクト */
    .snow { position: absolute; top: -10px; width: 8px; height: 8px; background: white; border-radius: 50%; animation: fall linear infinite; }
    .rain { position: absolute; top: -20px; width: 2px; height: 20px; background: #ADD8E6; animation: fall linear infinite; }
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

# 入力欄
city = st.text_input("", value="Tokyo", label_visibility="collapsed")
data = get_weather(city)

if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    rain = data.get('rain', {}).get('1h', 0)
    snow = data.get('snow', {}).get('1h', 0)
    
    now_hour = datetime.datetime.now().hour
    is_night = now_hour >= 18 or now_hour < 6
    
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
            left, dur = random.randint(0, 100), random.uniform(4, 8)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(50):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.2)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    img_url = f"https://raw.githubusercontent.com/hal2574/my-pixel-weather/main/{selected['img']}"

    # 画面全体の構成
    st.markdown(f"""
        <div class="weather-full-card">
            <div class="image-area" style="background-color: {bg_color};">
                <img src="{img_url}" class="pixel-bg">
                {effect_html}
                <div class="temp-overlay">{temp}℃</div>
            </div>
            <div class="info-area">
                <h1 style="margin:0; font-size: 28px;">{selected['txt']}</h1>
                <p style="margin:0; color: gray; font-size: 18px;">
                    {city} / 降水量: {max(rain, snow)} mm/h
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("City not found")

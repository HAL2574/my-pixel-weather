import streamlit as st
import requests
import datetime
import random
import base64
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# --- CSS (積雪アニメーションを追加) ---
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    .main-container { width: 100vw; height: 100vh; background-color: white; overflow: hidden; display: flex; flex-direction: column; }
    .image-box { position: relative; width: 100%; height: 65vh; overflow: hidden; }
    .pixel-img { width: 100%; height: 100%; object-fit: cover; }
    .temp-txt { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 80px; font-weight: bold; text-shadow: 2px 2px 15px rgba(0,0,0,0.6); z-index: 10; }
    .info-box { height: 35vh; padding: 15px 25px; background: white; }
    
    /* 降る雪のアニメーション */
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 5; }
    @keyframes fall { to { transform: translateY(65vh); } }

    /* ★積もる雪のアニメーション★ */
    .snow-pile {
        position: absolute; bottom: 0; left: 0; width: 100%;
        background: white;
        z-index: 4; /* 画像より前、降る雪より後ろ */
        animation: pile-up 60s ease-in-out forwards; /* 60秒かけてゆっくり積もる */
        filter: blur(2px); /* 少しふわっとさせる */
    }
    @keyframes pile-up {
        from { height: 0px; }
        to { height: 40px; } /* 最大40pxまで積もる */
    }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except: return None

city_map = {
    "札幌": "Sapporo", "小樽": "Otaru", "東京": "Tokyo", 
    "ロンドン": "London", "ハワイ": "Honolulu"
}

selected_city_jp = st.selectbox("都市を選択", options=list(city_map.keys()), index=0)
city_en = city_map[selected_city_jp]
data = get_weather(city_en)

if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    
    themes = {
        "Clear":  {"bg": "#FFD700", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    # 演出のHTML生成
    effect_html = ""
    if weather_main == "Snow":
        # 降る雪
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
        # 積もる雪（白い土台）
        effect_html += '<div class="snow-pile"></div>'
    
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.6, 1.2)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s; position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 5;"></div>'

    st.markdown(f"""
        <div class="main-container">
            <div class="image-box" style="background-color: {selected['bg']};">
                <img src="data:image/png;base64,{img_b64}" class="pixel-img">
                {effect_html}
                <div class="temp-txt">{temp}℃</div>
            </div>
            <div class="info-box">
                <h1 style="margin:0; font-size: 32px; color: #333;">{selected_city_jp}：{selected['txt']}</h1>
                <p style="color:gray; font-size: 18px; margin-top: 10px;">
                    現在の気温：{temp}℃
                </p>
                <p style="color:#eee; font-size: 12px; margin-top: 20px;">
                    Snow Pile Effect Enabled ❄️
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。")

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

# --- CSS (レイアウト崩れ防止・文字を最前面に) ---
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    .main-container { width: 100vw; height: 100vh; background-color: white; overflow: hidden; display: flex; flex-direction: column; }
    .image-box { position: relative; width: 100%; height: 60vh; overflow: hidden; background-color: #eee; }
    .pixel-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* 気温の文字が絶対に消えないように設定 */
    .temp-txt { 
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        color: white; font-size: 75px; font-weight: bold; 
        text-shadow: 2px 2px 12px rgba(0,0,0,0.7); z-index: 100; 
    }
    
    .info-box { height: 40vh; padding: 20px; background: white; z-index: 10; }
    
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 50; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 50; }
    
    .snow-pile { position: absolute; bottom: 0; left: 0; width: 100%; background: white; z-index: 40; animation: pile-up 60s ease-out forwards; filter: blur(1px); }
    @keyframes fall { to { transform: translateY(60vh); } }
    @keyframes pile-up { from { height: 0px; } to { height: 30px; } }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except: pass
    return None

# --- 都市選択トグル (旭川と帯広を追加) ---
city_map = {
    "札幌": "Sapporo", 
    "旭川": "Asahikawa",
    "帯広": "Obihiro",
    "小樽": "Otaru", 
    "東京": "Tokyo", 
    "ロンドン": "London", 
    "ハワイ": "Honolulu"
}

# セレクトボックス
selected_city_jp = st.selectbox("都市を選択してください", options=list(city_map.keys()), index=0)
city_en = city_map[selected_city_jp]

# データを取得
data = get_weather(city_en)

# --- 画面描画 ---
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

    # 演出HTML
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(20):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
        effect_html += '<div class="snow-pile"></div>'
    elif weather_main == "Rain":
        for _ in range(30):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.3)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # メイン表示
    st.markdown(f"""
        <div class="main-container">
            <div class="image-box" style="background-color: {selected['bg']};">
                <img src="data:image/png;base64,{img_b64}" class="pixel-img">
                {effect_html}
                <div class="temp-txt">{temp}℃</div>
            </div>
            <div class="info-box">
                <h2 style="margin:0; color:#333;">{selected_city_jp}の天気</h2>
                <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{selected['txt']}</p>
                <p style="color:gray;">現在の気温：{temp}℃</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning(f"現在、{selected_city_jp}の情報を取得できません。")

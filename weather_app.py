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
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# --- 2. 都市選択 ---
city_map = {
    "札幌": "Sapporo", "旭川": "Asahikawa", "帯広": "Obihiro",
    "小樽": "Otaru", "東京": "Tokyo", "ロンドン": "London", "ハワイ": "Honolulu"
}
selected_city_jp = st.selectbox("都市を選択してください", options=list(city_map.keys()), index=0)
city_en = city_map[selected_city_jp]

# --- 3. データ取得 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&lang=ja&units=metric"
data = None
try:
    res = requests.get(url, timeout=5)
    if res.status_code == 200: data = res.json()
except: pass

# --- 4. CSS設定 (ここを大幅強化) ---
st.markdown("""
    <style>
    /* 画面全体の余白を強制排除 */
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    [data-testid="stHeader"] { display: none; }
    
    /* 画像を入れる箱：背景色を画像と同じにして目立たなくする */
    .image-container {
        position: relative;
        width: 100vw;
        height: 100vw; /* 正方形に固定して枠をなくす */
        margin: 0;
        padding: 0;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 画像：コンテナを完全に覆い尽くす */
    .pixel-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important; /* 隙間を作らずトリミングして埋める */
    }
    
    .temp-overlay {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 80px; font-weight: bold;
        text-shadow: 3px 3px 15px rgba(0,0,0,0.8); z-index: 10;
    }
    
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 5; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 5; }
    @keyframes fall { to { transform: translateY(100vw); } }
    
    .info-area { padding: 25px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. メイン表示 ---
if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    
    themes = {
        "Clear":  {"bg": "#87CEEB", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    effect_html = ""
    if weather_main == "Snow":
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.3)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # 描画
    st.markdown(f"""
        <div class="image-container" style="background-color: {selected['bg']};">
            <img src="data:image/png;base64,{img_b64}" class="pixel-img">
            {effect_html}
            <div class="temp-overlay">{temp}℃</div>
        </div>
        <div class="info-area">
            <h2 style="margin:0; font-size: 28px;">{selected_city_jp}：{selected['txt']}</h2>
            <p style="font-size: 18px; color: gray; margin-top: 10px;">現在の気温は {temp}℃ です</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。")

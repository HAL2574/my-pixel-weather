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

# セレクトボックス（操作のため、これだけは画面最上部に置きます）
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
        "Clear":  {"bg": "#87CEEB", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    # 雪・雨の演出用HTML
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.3)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # --- CSS & HTML 統合表示 ---
    # 下部の文字情報を info-area から画像内の info-overlay に移動しました
    st.markdown(f"""
        <style>
        .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        header {{ visibility: hidden; display: none; }}
        [data-testid="stHeader"] {{ display: none; }}
        
        /* メインのカード：画面のほぼ全域を使う */
        .weather-card {{
            position: relative;
            width: 100vw;
            height: 85vh; /* 文字を中に入れるので、高さを少し広げました */
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: {selected['bg']};
        }}
        
        .pixel-img {{
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
        }}
        
        /* 中央の気温 */
        .temp-overlay {{
            position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%);
            color: white; font-size: 90px; font-weight: bold;
            text-shadow: 4px 4px 15px rgba(0,0,0,0.8); z-index: 100;
        }}
        
        /* 下部の都市名・天気情報（ドット絵の中に配置） */
        .info-overlay {{
            position: absolute;
            bottom: 40px;
            left: 0;
            width: 100%;
            text-align: center;
            color: white;
            z-index: 100;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        }}
        .city-name {{ font-size: 32px; font-weight: bold; margin: 0; }}
        .weather-desc {{ font-size: 20px; opacity: 0.9; margin: 5px 0 0 0; }}
        
        /* アニメーション */
        .snow {{ position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 50; }}
        .rain {{ position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 50; }}
        @keyframes fall {{ to {{ transform: translateY(85vh); }} }}
        </style>

        <div class="weather-card">
            <img src="data:image/png;base64,{img_b64}" class="pixel-img">
            {effect_html}
            <div class="temp-overlay">{temp}℃</div>
            
            <div class="info-overlay">
                <p class="city-name">{selected_city_jp}</p>
                <p class="weather-desc">{selected['txt']}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。")

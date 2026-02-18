import streamlit as st
import requests
import random
import base64
from PIL import Image
import io

# --- 1. ページ設定 (スマホで見やすく) ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# 画像変換関数
def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# --- 2. 都市選択 (操作しやすく上部に配置) ---
city_map = {
    "札幌": "Sapporo", 
    "旭川": "Asahikawa",
    "帯広": "Obihiro",
    "小樽": "Otaru", 
    "東京": "Tokyo", 
    "ロンドン": "London", 
    "ハワイ": "Honolulu"
}

selected_city_jp = st.selectbox("都市を選択してください", options=list(city_map.keys()), index=0)
city_en = city_map[selected_city_jp]

# --- 3. データ取得 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&lang=ja&units=metric"
data = None
try:
    res = requests.get(url, timeout=5)
    if res.status_code == 200:
        data = res.json()
except:
    pass

# --- 4. CSS設定 (大画面重視) ---
st.markdown("""
    <style>
    /* 左右の余白を削って画面幅を広く使う */
    .block-container { padding: 1rem 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    [data-testid="stHeader"] { display: none; }
    
    /* 画像エリア：画面の高さの70%を使う(大迫力) */
    .image-container {
        position: relative;
        width: 100vw;
        height: 70vh; 
        overflow: hidden;
        background-color: #eee;
    }
    .pixel-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* 気温の文字 */
    .temp-overlay {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 80px; font-weight: bold;
        text-shadow: 3px 3px 15px rgba(0,0,0,0.8); z-index: 10;
    }
    
    /* アニメーション：画面の高さに合わせて落ちる距離を調整 */
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 5; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 5; }
    @keyframes fall { to { transform: translateY(70vh); } }
    
    /* 下の情報エリア */
    .info-area {
        padding: 20px 25px;
        background: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. メイン表示 ---
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

    # 雪・雨の演出
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.3)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # 画像と気温を表示
    st.markdown(f"""
        <div class="image-container" style="background-color: {selected['bg']};">
            <img src="data:image/png;base64,{img_b64}" class="pixel-img">
            {effect_html}
            <div class="temp-overlay">{temp}℃</div>
        </div>
    """, unsafe_allow_html=True)

    # 文字情報は画像の下に配置 (スクロールで見える)
    st.markdown(f"""
        <div class="info-area">
            <h2 style="margin:0; font-size: 30px;">{selected_city_jp}は「{selected['txt']}」</h2>
            <p style="font-size: 20px; color: gray; margin-top: 10px;">
                現在の気温：{temp}℃
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("お天気データの取得に失敗しました。")

import streamlit as st
import requests
import random
import base64
from PIL import Image
import io

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# 画像変換関数
def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# --- 2. 都市選択 (ここを最初に行う) ---
city_map = {
    "札幌": "Sapporo", 
    "旭川": "Asahikawa",
    "帯広": "Obihiro",
    "小樽": "Otaru", 
    "東京": "Tokyo", 
    "ロンドン": "London", 
    "ハワイ": "Honolulu"
}

# 選択肢を画面に表示
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

# --- 4. CSS設定 (画像エリアの高さとアニメーション) ---
st.markdown("""
    <style>
    /* ヘッダーなどを消す */
    header { visibility: hidden; display: none; }
    [data-testid="stHeader"] { display: none; }
    
    /* 画像エリアのスタイル */
    .image-container {
        position: relative;
        width: 100%;
        height: 350px; /* iPhoneで見やすい高さ */
        overflow: hidden;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .pixel-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* 気温の文字 */
    .temp-overlay {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 70px; font-weight: bold;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); z-index: 10;
    }
    
    /* アニメーション */
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 5; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 5; }
    @keyframes fall { to { transform: translateY(350px); } }
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
        for _ in range(20):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(30):
            left, dur = random.randint(0, 100), random.uniform(0.7, 1.3)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # 画像と気温の表示
    st.markdown(f"""
        <div class="image-container" style="background-color: {selected['bg']};">
            <img src="data:image/png;base64,{img_b64}" class="pixel-img">
            {effect_html}
            <div class="temp-overlay">{temp}℃</div>
        </div>
    """, unsafe_allow_html=True)

    # 文字情報の表示 (Streamlitの標準機能を使うので確実)
    st.subheader(f"{selected_city_jp}の天気：{selected['txt']}")
    st.write(f"現在の気温は **{temp}℃** です。")

else:
    st.error("お天気データの取得に失敗しました。もう一度都市を選び直してみてください。")

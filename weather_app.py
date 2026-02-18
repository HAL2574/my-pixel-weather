import streamlit as st
import requests
import datetime
import random
import base64
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# 画像変換
def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# --- CSS (変更なし) ---
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    .main-container { width: 100vw; height: 100vh; background-color: white; overflow: hidden; display: flex; flex-direction: column; }
    .image-box { position: relative; width: 100%; height: 70vh; overflow: hidden; }
    .pixel-img { width: 100%; height: 100%; object-fit: cover; }
    .temp-txt { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 75px; font-weight: bold; text-shadow: 2px 2px 12px rgba(0,0,0,0.6); z-index: 10; }
    .info-box { height: 30vh; padding: 15px 25px; background: white; }
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; }
    @keyframes fall { to { transform: translateY(75vh); } }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city):
    # スペースなどが入っても大丈夫なように修正
    city = city.strip()
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            return f"Error: {res.status_code}" # エラーコードを返す
    except Exception as e:
        return str(e)

# --- 検索窓 (初期値は Sapporo) ---
city_input = st.text_input("都市名 (例: Sapporo, London, Tokyo)", value="Sapporo")

# データの取得
data = get_weather(city_input)

# データが正常に取得できた場合
if isinstance(data, dict):
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    rain_vol = data.get('rain', {}).get('1h', 0)
    snow_vol = data.get('snow', {}).get('1h', 0)
    
    themes = {
        "Clear":  {"bg": "#FFD700", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    img_b64 = get_image_base64(selected["img"])

    # パーティクル
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.6, 1.2)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # メイン描画
    st.markdown(f"""
        <div class="main-container">
            <div class="image-box" style="background-color: {selected['bg']};">
                <img src="data:image/png;base64,{img_b64}" class="pixel-img">
                {effect_html}
                <div class="temp-txt">{temp}℃</div>
            </div>
            <div class="info-box">
                <h1 style="margin:0; font-size: 32px; color: #333;">天気: {selected['txt']}</h1>
                <p style="color:gray; font-size: 18px; margin-top: 5px;">
                    {city_input} の気温：{temp}℃<br>
                    降水量：{max(rain_vol, snow_vol)} mm/h
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# エラーが起きた場合
else:
    st.error(f"「{city_input}」のデータが見つかりませんでした。正しい都市名を英単語で入力してね！")
    st.info("例: Otaru, Asahikawa, Hakodate")

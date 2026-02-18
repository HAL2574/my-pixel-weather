import streamlit as st
import requests
import datetime
import random
import base64
from PIL import Image
import io

# --- ページ全体の基本設定 ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# ローカルの画像ファイルをWeb表示用に変換する関数
def get_image_base64(path):
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except:
        return ""

# --- iPhoneで見栄えを最高にするためのCSSデザイン ---
st.markdown("""
    <style>
    /* 画面の余白を徹底的に削る */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* 画面構成のベース */
    .main-container {
        width: 100vw; height: 100vh;
        background-color: white; overflow: hidden;
        display: flex; flex-direction: column;
    }
    
    /* ドット絵が表示されるメインエリア */
    .image-box {
        position: relative; width: 100%; height: 65vh;
        overflow: hidden;
    }
    .pixel-img {
        width: 100%; height: 100%; object-fit: cover;
    }
    
    /* 気温の数字を中央に配置 */
    .temp-txt {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 80px; font-weight: bold;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6); z-index: 10;
    }
    
    /* 下半分の情報エリア */
    .info-box {
        height: 35vh; padding: 15px 25px; background: white;
    }
    
    /* アニメーション（雪と雨） */
    .snow { position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; }
    .rain { position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; }
    @keyframes fall { to { transform: translateY(65vh); } }
    
    /* セレクトボックスのラベルを少し見やすく */
    .stSelectbox label { font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- お天気データの取得設定 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&lang=ja&units=metric"
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- 都市選択のトグル設定 ---
# 札幌を一番上(初期値)にしています。お好みで増やしてください！
city_map = {
    "札幌": "Sapporo",
    "小樽": "Otaru",
    "旭川": "Asahikawa",
    "函館": "Hakodate",
    "東京": "Tokyo",
    "大阪": "Osaka",
    "福岡": "Fukuoka",
    "ロンドン": "London",
    "ハワイ": "Honolulu"
}

# iPhoneで操作しやすいセレクトボックス
selected_city_jp = st.selectbox("都市を選択", options=list(city_map.keys()), index=0)

# 選択された都市の英語名を取得してAPIへ
city_en = city_map[selected_city_jp]
data = get_weather(city_en)

# --- 画面の描画処理 ---
if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    rain_vol = data.get('rain', {}).get('1h', 0)
    snow_vol = data.get('snow', {}).get('1h', 0)
    
    # 天気ごとのテーマ設定
    themes = {
        "Clear":  {"bg": "#FFD700", "img": "sunny.png", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "img": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "img": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "img": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    
    # 画像を読み込み
    img_b64 = get_image_base64(selected["img"])

    # アニメーションのHTML生成
    effect_html = ""
    if weather_main == "Snow":
        for _ in range(25):
            left, dur = random.randint(0, 100), random.uniform(3, 7)
            effect_html += f'<div class="snow" style="left:{left}%; animation-duration:{dur}s;"></div>'
    elif weather_main == "Rain":
        for _ in range(40):
            left, dur = random.randint(0, 100), random.uniform(0.6, 1.2)
            effect_html += f'<div class="rain" style="left:{left}%; animation-duration:{dur}s;"></div>'

    # メイン画面の表示
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
                    現在の気温：{temp}℃<br>
                    降水量目安：{max(rain_vol, snow_vol)} mm/h
                </p>
                <p style="color:#ccc; font-size: 12px; margin-top: 20px;">
                    Pixel Weather App v1.0
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("データの取得に失敗しました。時間をおいて試してみてね。")

import streamlit as st
import requests
import random
import base64
from PIL import Image
import io

# --- 1. ページ設定 (余白を完全に殺す) ---
st.set_page_config(page_title="Pixel Weather", layout="centered")

# ファイルをBase64に変換する関数（画像もGIFも対応）
def get_file_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except:
        return ""

# --- 2. 都市選択 ---
city_map = {
    "札幌": "Sapporo", "旭川": "Asahikawa", "帯広": "Obihiro",
    "小樽": "Otaru", "東京": "Tokyo", "ロンドン": "London", "ハワイ": "Honolulu"
}
selected_city_jp = st.selectbox("都市を選択してください", options=list(city_map.keys()), index=0)

# --- 3. データ取得 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"
city_en = city_map[selected_city_jp]
url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&lang=ja&units=metric"

data = None
try:
    res = requests.get(url, timeout=5)
    if res.status_code == 200:
        data = res.json()
except:
    pass

# --- 4. 描画処理 ---
if data:
    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    
    # 天気ごとの設定（晴れの場合は sunny.gif を使用）
    themes = {
        "Clear":  {"bg": "#87CEEB", "file": "sunny.gif", "txt": "快晴"},
        "Rain":   {"bg": "#4682B4", "file": "rainy.png", "txt": "雨"},
        "Snow":   {"bg": "#E0FFFF", "file": "snowy.png", "txt": "雪"},
        "Clouds": {"bg": "#A9A9A9", "file": "cloudy.png", "txt": "曇り"}
    }
    selected = themes.get(weather_main, themes["Clouds"])
    file_b64 = get_file_base64(selected["file"])

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

    # --- CSS & HTML 埋め込み ---
    st.markdown(f"""
        <style>
        /* Streamlitの標準余白を強制解除 */
        .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        header {{ visibility: hidden; display: none; }}
        [data-testid="stHeader"] {{ display: none; }}
        
        /* 全画面コンテナ：iPhoneの画面高さを活かす */
        .weather-container {{
            position: relative;
            width: 100vw;
            height: 75vh;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: {selected['bg']};
        }}
        
        /* 背景（画像・GIF共通）：アスペクト比を維持しつつ画面を埋め尽くす */
        .pixel-bg {{
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            image-rendering: pixelated; /* ドットをくっきりさせる */
        }}
        
        /* 気温：最前面に配置 */
        .temp-overlay {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: white; font-size: 90px; font-weight: bold;
            text-shadow: 4px 4px 20px rgba(0,0,0,0.8);
            z-index: 100;
            font-family: 'Courier New', Courier, monospace;
        }}
        
        /* 天気エフェクト（雪・雨） */
        .snow {{ position: absolute; top: -10px; width: 6px; height: 6px; background: white; border-radius: 50%; animation: fall linear infinite; z-index: 50; }}
        .rain {{ position: absolute; top: -15px; width: 2px; height: 15px; background: #ADD8E6; animation: fall linear infinite; z-index: 50; }}
        @keyframes fall {{ to {{ transform: translateY(75vh); }} }}
        
        /* 情報エリア */
        .info-area {{
            padding: 30px 25px;
            background: white;
            font-family: sans

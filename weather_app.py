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
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&lang=ja&units=

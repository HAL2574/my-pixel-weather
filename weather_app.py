import tkinter as tk
import requests
from PIL import Image, ImageTk
import os
import random
import datetime
import math

# --- 設定 ---
API_KEY = "1cd0ee42efdec18da432fea8bde0aed0"
particles = []
snow_pile_id = None
snow_height = 0
sun_moon_id = None
angle = 0  # 太陽・月の移動用

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ja&units=metric"
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except: return None

def update_display():
    global snow_height, snow_pile_id, sun_moon_id
    city = city_entry.get() or "Tokyo"
    data = get_weather_data(city)
    if not data: return

    weather_main = data['weather'][0]['main']
    temp = round(data['main']['temp'], 1)
    rain_vol = data.get('rain', {}).get('1h', 0)
    snow_vol = data.get('snow', {}).get('1h', 0)

    # 時刻判定
    now_hour = datetime.datetime.now().hour
    is_night = now_hour >= 18 or now_hour < 6

    # 演出のリセット
    snow_height = 0
    if snow_pile_id: canvas.delete(snow_pile_id)
    if sun_moon_id: canvas.delete(sun_moon_id)
    
    # テーマ設定
    theme = {
        "Clear":  {"day": "#FFD700", "night": "#191970", "img": "sunny.png",  "text": "快晴"},
        "Rain":   {"day": "#4682B4", "night": "#2F4F4F", "img": "rainy.png",  "text": "雨"},
        "Clouds": {"day": "#A9A9A9", "night": "#696969", "img": "cloudy.png", "text": "曇り"},
        "Snow":   {"day": "#E0FFFF", "night": "#4B0082", "img": "snowy.png",  "text": "雪"},
    }
    selected = theme.get(weather_main, theme["Clouds"])
    bg_color = selected["night"] if is_night else selected["day"]

    # UI更新
    canvas.config(bg=bg_color)
    label_weather.config(text=f"天気: {selected['text']}")
    label_temp.config(text=f"気温: {temp}℃")
    label_rain.config(text=f"降水量: {rain_vol if weather_main != 'Snow' else snow_vol}mm")

    # 画像トリミング処理
    img_path = os.path.join(os.path.dirname(__file__), selected["img"])
    if os.path.exists(img_path):
        img = Image.open(img_path)
        w, h = img.size
        target_ratio = 400 / 530
        if w/h > target_ratio:
            new_w = h * target_ratio
            left = (w - new_w) / 2
            img = img.crop((left, 0, left + new_w, h))
        img = img.resize((400, 530), Image.NEAREST)
        photo = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_container, image=photo)
        canvas.image = photo

    # 太陽・月の作成 (晴れの時)
    if weather_main == "Clear":
        color = "white" if is_night else "orange"
        sun_moon_id = canvas.create_oval(0, 0, 40, 40, fill=color, outline="")

    setup_particles(weather_main, rain_vol, snow_vol)

def setup_particles(weather_main, rain_vol, snow_vol):
    for p in particles: canvas.delete(p["id"])
    particles.clear()
    
    if weather_main in ["Rain", "Drizzle", "Thunderstorm"]:
        for _ in range(int(50 + rain_vol * 100)):
            x, y = random.randint(0, 400), random.randint(0, 530)
            p_id = canvas.create_line(x, y, x, y+15, fill="#ADD8E6")
            particles.append({"id": p_id, "speed": random.uniform(10, 15), "type": "rain"})
    elif weather_main == "Snow":
        for _ in range(int(40 + snow_vol * 80)):
            x, y = random.randint(0, 400), random.randint(0, 530)
            size = random.randint(1, 4)
            p_id = canvas.create_oval(x, y, x+size, y+size, fill="white", outline="white")
            particles.append({"id": p_id, "speed": random.uniform(0.6, 1.3), "type": "snow", "size": size})

def animate():
    global snow_height, snow_pile_id, angle
    
    # 1. 雨・雪の移動
    for p in particles:
        coords = canvas.coords(p["id"])
        if not coords: continue
        new_y = coords[1] + p["speed"]
        if p["type"] == "rain":
            if new_y > 530: new_y = -20
            canvas.coords(p["id"], coords[0], new_y, coords[0], new_y+15)
        else:
            new_x = coords[0] + random.uniform(-0.3, 0.3)
            if new_y > 530:
                new_y, new_x = -10, random.randint(0, 400)
                # 雪が底についたら積もらせる
                if snow_height < 50: snow_height += 0.05
            canvas.coords(p["id"], new_x, new_y, new_x + p["size"], new_y + p["size"])

    # 2. 雪を積もらせる描画更新
    if snow_height > 0:
        if snow_pile_id: canvas.delete(snow_pile_id)
        snow_pile_id = canvas.create_rectangle(0, 530 - snow_height, 400, 530, fill="white", outline="")

    # 3. 太陽・月の移動 (サイン・コサインで弧を描く)
    if sun_moon_id:
        angle += 0.01
        sun_x = 200 + 150 * math.cos(angle)
        sun_y = 150 + 80 * math.sin(angle)
        canvas.coords(sun_moon_id, sun_x-20, sun_y-20, sun_x+20, sun_y+20)

    root.after(30, animate)

# --- GUI構築 ---
root = tk.Tk()
root.title("Weather App Master")
root.geometry("400x650")
root.config(bg="white")
root.resizable(False, False)

canvas = tk.Canvas(root, width=400, height=530, highlightthickness=0, bd=0)
canvas.pack(fill="x")
image_container = canvas.create_image(200, 265, anchor="center")

info_frame = tk.Frame(root, bg="white", padx=15, pady=5)
info_frame.pack(fill="both", expand=True)

label_weather = tk.Label(info_frame, text="天気: --", font=("MS Gothic", 16, "bold"), bg="white")
label_weather.grid(row=0, column=0, sticky="w", padx=5)
label_temp = tk.Label(info_frame, text="気温: --℃", font=("MS Gothic", 14), bg="white")
label_temp.grid(row=1, column=0, sticky="w", padx=5)
label_rain = tk.Label(info_frame, text="降水量: --mm", font=("MS Gothic", 14), bg="white")
label_rain.grid(row=1, column=1, sticky="w", padx=10)

search_container = tk.Frame(info_frame, bg="white")
search_container.grid(row=0, column=2, rowspan=2, sticky="e", padx=5)
city_entry = tk.Entry(search_container, width=10, font=("Helvetica", 11))
city_entry.pack()
city_entry.insert(0, "Sapporo")
tk.Button(search_container, text="検索", font=("MS Gothic", 9), command=update_display).pack(fill="x", pady=2)

update_display()
animate()
root.mainloop()
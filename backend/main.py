from flask import Flask, jsonify
import cv2
import pytesseract
import pandas as pd
import time

app = Flask(__name__)

# Konfigurasi Timeframe
TIMEFRAME = 60  # Bisa diubah sesuai kebutuhan (dalam detik)

# Fungsi untuk mengambil screenshot layar (Dummy)
def capture_screen():
    img_path = "screenshot.png"
    return img_path

# Fungsi membaca harga dari gambar menggunakan OCR
def read_price_from_screen(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img, config='--psm 7')
    
    try:
        price = float(''.join(filter(str.isdigit, text))) / 100
        return price if price > 0 else None
    except ValueError:
        return None

# Fungsi untuk analisis sinyal
def analyze_signal(price_data):
    price_data['SMA_5'] = price_data['Close'].rolling(window=5).mean()
    price_data['SMA_10'] = price_data['Close'].rolling(window=10).mean()
    
    if price_data['SMA_5'].iloc[-1] > price_data['SMA_10'].iloc[-1]:
        return "BUY"
    elif price_data['SMA_5'].iloc[-1] < price_data['SMA_10'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

# Endpoint API untuk mendapatkan sinyal trading
@app.route('/signal', methods=['GET'])
def get_signal():
    img_path = capture_screen()
    price = read_price_from_screen(img_path)

    if price is not None:
        df = pd.DataFrame([{'Close': price}])
        signal = analyze_signal(df)
        return jsonify({"signal": signal})
    else:
        return jsonify({"error": "Gagal membaca harga"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import cv2
import numpy as np
import base64
import webbrowser
from pathlib import Path
import os

def save_and_encode_image(image, filename):
    """画像を保存してbase64エンコードされたデータURLを返す"""
    cv2.imwrite(filename, image)
    with open(filename, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded}"

def create_html_report(images_data):
    """検出結果をHTMLレポートとして生成"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Detection Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }
            .image-container {
                margin: 20px 0;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h2 {
                color: #333;
                margin-bottom: 10px;
            }
            img {
                max-width: 100%;
                height: auto;
            }
        </style>
    </head>
    <body>
        <h1>画像認識結果</h1>
    """
    
    # 各画像の結果を追加
    for title, data_url in images_data:
        html_content += f"""
        <div class="image-container">
            <h2>{title}</h2>
            <img src="{data_url}" alt="{title}">
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    # HTMLファイルを保存
    report_path = "detection_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return report_path

def detect_objects(image_path):
    """
    複数の顔を検出可能な画像認識関数
    結果をブラウザで表示
    """
    # 画像の読み込み
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("画像を読み込めませんでした")
    
    # 作業用に画像をコピー
    output_image = image.copy()
    
    # グレースケールに変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 顔検出の準備
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # 顔検出の実行
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # 検出された顔の数を表示
    print(f"検出された顔の数: {len(faces)}")
    
    # 検出された顔それぞれに枠と番号を描画
    for i, (x, y, w, h) in enumerate(faces, 1):
        cv2.rectangle(output_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.putText(
            output_image,
            f"Face #{i}",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2
        )
        
        confidence = f"Size: {w}x{h}"
        cv2.putText(
            output_image,
            confidence,
            (x, y+h+20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )
    
    # エッジ検出（Canny）
    edges = cv2.Canny(gray, 100, 200)
    
    # 特定の色（青色）の検出
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blue_lower = np.array([100, 50, 50])
    blue_upper = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    
    # 一時ファイルの保存とエンコード
    images_data = [
        ("顔検出結果", save_and_encode_image(output_image, "detected_faces.jpg")),
        ("エッジ検出結果", save_and_encode_image(edges, "edges.jpg")),
        ("青色検出結果", save_and_encode_image(blue_mask, "blue_mask.jpg"))
    ]
    
    # HTMLレポートの生成と表示
    report_path = create_html_report(images_data)
    webbrowser.open('file://' + os.path.abspath(report_path))

if __name__ == "__main__":
    image_path = R"C:\Users\user\OneDrive\Pictures\sample.jpg"
    try:
        detect_objects(image_path)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
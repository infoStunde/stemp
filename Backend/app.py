from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import send_file
from pdf2image import convert_from_path
from PIL import ImageDraw, ImageFont
import os
import io

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({'filename': file.filename})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/uploads/<filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/preview/<filename>', methods=['GET'])
def preview_pdf(filename):
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    # Windows: poppler_path=r"C:\poppler\Library\bin"
    images = convert_from_path(pdf_path, first_page=1, last_page=1, size=1000, poppler_path=r"./../Lib/poppler-24.08.0/Library/bin")
    img = images[0]
    draw = ImageDraw.Draw(img)

    # Stempel-Text und Position (unten, mittig)
    stamp_text = request.args.get('stamp', 'TEST-STEMPEL')
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    w, h = img.size
    bbox = draw.textbbox((0, 0), stamp_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (w - text_width) // 2
    y = h - text_height - 200  # 40px Abstand zum unteren Rand

    # Stempel zeichnen (schwarz auf weißem Kasten)
    draw.rectangle([x-10, y-10, x+text_width+10, y+text_height+10], fill="white")
    draw.text((x, y), stamp_text, fill="red", font=font)

    # Bild zurückgeben
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # 10000 ist nur ein Fallback für lokale Tests
    app.run(host='0.0.0.0', port=port)

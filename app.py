from flask import Flask, request, jsonify , render_template
from flask_cors import CORS, cross_origin
import requests
import pytesseract
from werkzeug.utils import secure_filename
from PIL import Image
from pyzbar.pyzbar import decode
from io import BytesIO

app = Flask(__name__, template_folder='temp')
CORS(app)  # อนุญาตทั้งหมด

@app.route('/scan',methods=['GET'])
def temp_scan():
    return render_template('index.html'),200

@app.route('/', methods=['GET'])
def decode_qr():
    # รับ URL จาก query parameters
    url = request.args.get('url')
    # ตรวจสอบว่า URL ถูกต้อง
    if not url:
        return jsonify({"error": "URL is required."}), 400
    # ดาวน์โหลดภาพจาก URL
    response = requests.get(url)
    # ตรวจสอบว่าการดาวน์โหลดสำเร็จ
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve the image."}), 400
    # เปิดภาพ
    image = Image.open(BytesIO(response.content))
    
    # อ่าน QR Code
    decoded_objects = decode(image)

    # หากไม่มี QR Code
    if not decoded_objects:
        return jsonify({"message": "No QR Code found."}), 404

    # แสดงข้อมูลที่อ่านได้จาก QR Code
    results = [obj.data.decode('utf-8') for obj in decoded_objects]
    return jsonify({"results": results[0]})

# สร้าง endpoint สำหรับการรับรูปภาพ
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    # ตรวจสอบว่ามีการเลือกไฟล์หรือไม่
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # ตรวจสอบว่าไฟล์เป็นประเภทภาพที่อนุญาต
    if file and allowed_file(file.filename):
        # อ่านไฟล์โดยไม่ทำการบันทึก
        image = Image.open(BytesIO(file.read()))
        # ทำการประมวลผล เช่น อ่านขนาดภาพ
        width, height = image.size
    # อ่าน QR Code
        decoded_objects = decode(image)
    # หากไม่มี QR Code
        if not decoded_objects:
            return jsonify({"message": "No QR Code found."}), 404
    # แสดงข้อมูลที่อ่านได้จาก QR Code
        results = [obj.data.decode('utf-8') for obj in decoded_objects]
        return jsonify({"results": results[0]})
    else:
        return jsonify({"error": "File type not allowed"}), 400

# ฟังก์ชันตรวจสอบนามสกุลไฟล์ที่อนุญาต
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
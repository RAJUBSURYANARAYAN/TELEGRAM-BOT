import string
import random
import os
import uuid
from flask import Flask, request, render_template, jsonify, send_from_directory, abort
from database import init_db, save_code

print("Starting Flask app...")

app = Flask(__name__)
TEMP_UPLOAD_FOLDER = "temp_uploads"
UPLOAD_FOLDER = "uploads"
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database
init_db()

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    folder_uuid = str(uuid.uuid4())
    upload_path = os.path.join(TEMP_UPLOAD_FOLDER, folder_uuid)
    os.makedirs(upload_path, exist_ok=True)

    for file in files:
        if file:
            filepath = os.path.join(upload_path, file.filename)
            file.save(filepath)

    # Generate a unique code
    code = generate_code()
    while not save_code(code, folder_uuid):
        code = generate_code()

    return jsonify({"code": code, "message": "Files uploaded successfully!"})

@app.route('/download/<chat_id>/<filename>')
def download_file(chat_id, filename):
    # Ensure no path traversal in chat_id or filename
    if "/" in chat_id or "\\" in chat_id or ".." in chat_id:
        abort(400)
    if "/" in filename or "\\" in filename or ".." in filename:
        abort(400)
        
    user_dir = os.path.join(UPLOAD_FOLDER, chat_id)
    if not os.path.exists(os.path.join(user_dir, filename)):
        abort(404)
        
    return send_from_directory(user_dir, filename, as_attachment=True)

if __name__ == '__main__':
    print("Flask app is running! Access it via http://localhost:5000 on this PC.")
    print("To access on mobile, connect to the same Wi-Fi and use your PC's IP address (e.g., http://192.168.1.X:5000)")
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, render_template
import os

print("Starting Flask app...")  # ← DEBUG LINE to confirm it's running

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return f"File {file.filename} uploaded successfully!"
    return "Upload failed."

if __name__ == '__main__':
    print("Flask app is running at http://127.0.0.1:5000")  # ← DEBUG LINE
    app.run(debug=True)
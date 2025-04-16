import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cấu hình thư mục upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tạo thư mục nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Kiểm tra định dạng file cho phép
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'files' not in request.files:
            return "Không có phần file trong request", 400

        files = request.files.getlist('files')
        invalid_files = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
            else:
                invalid_files.append(file.filename)

        if invalid_files:
            return f"Các file không hợp lệ: {', '.join(invalid_files)}", 400

        return redirect(url_for('index'))

    # GET: hiển thị ảnh
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)

@app.route('/download/<filename>')
def download_file(filename):
    filename = secure_filename(filename)

    if not filename or '/' in filename or '..' in filename:
        return "Tên file không hợp lệ", 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Không tìm thấy file", 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filename = secure_filename(filename)

    if not filename or '/' in filename or '..' in filename:
        return "Tên file không hợp lệ", 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index'))
    else:
        return "Không tìm thấy file", 404

if __name__ == '__main__':
    app.run(debug=True)
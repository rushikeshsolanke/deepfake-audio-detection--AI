import os
import time
import tempfile
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file, make_response
from tensorflow import keras
from tensorflow.keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import pdfkit
import sqlite3
from database import get_db_connection



app = Flask(__name__,
            static_folder="static",
            template_folder="templates")
app.secret_key ="deepfake"

path_to_wkhtmltopdf = os.path.join(app.static_folder, 'wkhtmltopdf.exe')
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = username
           
            return redirect(url_for("home"))
        flash('Invalid username or password', 'danger')
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form['full_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template("registration.html")

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        if user:
            flash('Username or email already exists', 'danger')
        else:
            conn.execute('INSERT INTO users (full_name, email, username, password) VALUES (?, ?, ?, ?)',
                         (full_name, email, username, generate_password_hash(password)))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for("login"))
        conn.close()
    return render_template("registration.html")


@app.route("/logout")
@login_required
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for("login"))

class_names = ['Real','Fake']
def create_spectrogram(file):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        file.save(temp_file.name)
        audio_file = temp_file.name

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    y, sr = librosa.load(audio_file)
    ms = librosa.feature.melspectrogram(y=y, sr=sr)
    log_ms = librosa.power_to_db(ms, ref=np.max)
    librosa.display.specshow(log_ms, sr=sr)
    plt.savefig('static/melspectrogram.png')
    plt.close(fig)
    image_data = load_img('static/melspectrogram.png', target_size=(224, 224))
    return image_data  


def predictions(image_data,model):

    img_array = np.array(image_data)
    img_array1 = img_array / 255
    img_batch = np.expand_dims(img_array1, axis=0)

    prediction = model.predict(img_batch)
    class_label = np.argmax(prediction)
    return class_label, prediction

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
        return render_template("home.html")

    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/features")
def features():
    return render_template("features.html")



@app.route("/download_report", methods=["POST"])
@login_required
def download_report():
    detection_message = request.form['detection_message']
    percentage = request.form['percentage']
    execution_time = request.form['execution_time']
    audio_path = request.form['audio_path']
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    rendered = render_template("download_report.html", detection_message=detection_message, percentage=percentage, execution_time=execution_time, audio_path=audio_path, today_date=today_date)
    
    # Convert the rendered HTML to a PDF
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # Handle wav file upload
        file = request.files.get("audio_file")
        if file and file.filename.endswith(".wav"):
            print('file uploaded')
            start_time = time.time()
            spec = create_spectrogram(file)
            print(spec)
            print('spec created')
            model = keras.models.load_model('saved_model/model')
            class_label,prediction = predictions(spec, model)
            print(class_names[class_label])
            print(class_label)
            detection_message = f"Detection Result: {class_names[class_label]}"
            end_time = time.time()
            execution_time = end_time - start_time
            execution_time = round(execution_time, 2)
            percentage="%.2f" %(prediction[0][class_label]*100)
            return render_template("audio_Result.html", detection_message=detection_message, percentage=percentage, execution_time=execution_time, audio_path = file.filename)
            # return render_template("audio_Result.html")
        flash('Upload valid audio format.', 'danger')
        return render_template("audio_upload.html")

    return render_template("audio_upload.html")




if __name__ == "__main__":
    app.run(debug=False)
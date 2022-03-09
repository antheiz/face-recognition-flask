import os, secrets, time
from app import app, db, bcrypt
from app.models import User
from flask import render_template, Response, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegisterForm, LoginForm, PersonalForm
from .models import User
from PIL import Image

# CV2 FaceRecognition
import cv2
import face_recognition
import numpy as np


# Register Akun User
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash('Akun berhasil dibuat, Silakan login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, judul='Register')


# Login User
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Gagal login, silakan coba lagi.')
    return render_template('login.html', form=form, judul="Login")


# Logout User
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#for image settings 
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    # form_picture.save(picture_path)

    i = Image.open(form_picture)
    i.save(picture_path)

    return picture_fn


# NOTE: For Recognition

@app.route('/proses-transaksi')
def transaksi_proses():

    # Load a sample picture and learn how to recognize it.
    known_face_encodings = []
    data = [row.foto for row in User.query.all()]
    
    for i in data:
        person_image = face_recognition.load_image_file("app/static/img/" + i)
        person_face_encoding = face_recognition.face_encodings(person_image)[0]
        known_face_encodings.append(person_face_encoding)

    print(known_face_encodings)
    person_name = [row.username for row in User.query.all()]

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # camera = cv2.VideoCapture(0)
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
                
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = person_name[best_match_index]
                
                face_names.append(name.upper())
                    

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 155), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')





@app.route('/dashboard', methods=['GET','POST'])
@login_required
def index():
    form = PersonalForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.foto.data)
        user = User.query.filter_by(username=current_user.username).first()
        user.foto = picture_file
        db.session.commit()        
        flash('Foto berhasil diupload!','success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form, judul ="Beranda")

@app.route('/success')
def success():
    return render_template('success.html', judul='Berhasil Transaksi')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(transaksi_proses(), mimetype='multipart/x-mixed-replace; boundary=frame')



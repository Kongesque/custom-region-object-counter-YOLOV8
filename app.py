from flask import Flask, render_template, Response, request, session, jsonify, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import os
import cv2
import time
import uuid
from detector import detection

app = Flask(__name__)  
app.config['SECRET_KEY'] = 'kongesque'  # NOTE: Hardcoded key is unsafe. Use os.environ.get('SECRET_KEY') in production.
app.config['UPLOAD_FOLDER'] = 'static/files/input'  
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

points = []

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Run")

def extract_frame(video_path, frame_number):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    return frame

def generate_frames(video_path, points,frame_size, color):
    yolo_output = detection(video_path, points, frame_size, color)
    for detection_ in yolo_output:
        _, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes | Routes 

@app.route('/', methods=['GET', 'POST'])
def main():
    form = UploadFileForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        taskID = str(uuid.uuid4())
        filename = taskID + "_" + secure_filename(file.filename) 
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['taskID'] = taskID
        session['video_path_' + taskID] = filepath
        print(filepath)
        frame_path = "static/files/frame/frame_" + taskID + ".jpg"
        cv2.imwrite(frame_path, extract_frame(session.get('video_path_' + taskID, None), 0))
        frame = cv2.imread(frame_path)

        frame_size = frame.shape[1], frame.shape[0]
        session['frame_size_' + taskID] = frame_size
        session['points_' + taskID] = []
        session['color_' + taskID] = (5, 189, 251)

        return redirect(url_for('draw', taskID=taskID))
    return render_template('main.html', form=form)
    
@app.route('/settings/<taskID>', methods=['GET', 'POST'])
def draw(taskID):
    points_key = 'points_' + taskID
    session[points_key] = []
    color_key = 'color_' + taskID
    session[color_key] = (5, 189, 251)
    video_path_key = 'video_path_' + taskID

    if video_path_key in session:
        return render_template('draw.html', taskID=taskID)
    return redirect(url_for('main'))

@app.route('/submit', methods=['POST'])
def submit():
    taskID = session.get('taskID')
    video_path_key = 'video_path_' + taskID
    frame_size_key = 'frame_size_' + taskID
    color_key = 'color_' + taskID
    points_key = 'points_' + taskID
    print(session.get(video_path_key), session.get(points_key), session.get(frame_size_key), session.get(color_key), session.get('taskID'))
    yolo_output = detection(session.get(video_path_key), session.get(points_key), session.get(frame_size_key), session.get(color_key), session.get('taskID'))
    for frame in yolo_output:
        pass
    time.sleep(5)
    return redirect(url_for('result', taskID=taskID))

@app.route('/result/<taskID>', methods=['GET', 'POST']) 
def result(taskID):
    form = UploadFileForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        taskID = str(uuid.uuid4())
        filename = taskID + "_" + secure_filename(file.filename) 
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['taskID'] = taskID
        session['video_path_' + taskID] = filepath
        frame_path = "static/files/frame/frame_" + taskID + ".jpg"
        cv2.imwrite(frame_path, extract_frame(session.get('video_path_' + taskID, None), 0))
        frame = cv2.imread(frame_path)

        frame_size = frame.shape[1], frame.shape[0]
        session['frame_size_' + taskID] = frame_size
        session['points_' + taskID] = []
        session['color_' + taskID] = (5, 189, 251)
        
        return redirect(url_for('draw', taskID=taskID))
    return render_template('result.html', form=form, taskID=taskID)


@app.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    data = request.get_json()
    taskID =  session.get('taskID')
    print("taskID:", taskID)
    x, y = data.get('x'), data.get('y')

    points_key = 'points_' + taskID
    points = session.get(points_key, [])
    points.append((x, y))
    session[points_key] = points
    print(points)
    return jsonify({"message": "Coordinates received successfully"})

@app.route('/color_setting', methods=['POST'])
def color_setting():
    data = request.json
    taskID =  session.get('taskID')
    color_key = 'color_' + taskID
    color = (int(data['b']), int(data['g']), int(data['r']))
    session[color_key] = color
    print(color)
    return jsonify({"message": "Color settings updated successfully"})

@app.route('/video')
def video():
    video_path = session.get('video_path')
    frame_size = session.get('frame_size')
    color = session.get('color')
    points = session.get('points')
    if video_path:
        return Response(generate_frames(video_path, points,frame_size, color), mimetype='multipart/x-mixed-replace; boundary=frame')
    return jsonify({"error": "Video not found"}), 404

@app.route('/clear', methods=['POST'])
def clear_coordinates():
    taskID = session.get('taskID')
    points_key = 'points_' + taskID
    session[points_key] = []
    return jsonify({"message": "Coordinates cleared successfully"})
    
if __name__ == "__main__":
    app.run(debug=True) 
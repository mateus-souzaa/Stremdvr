from flask import Flask, Response, render_template
import cv2
import urllib.parse

app = Flask(__name__)

# Configuração do RTSP com a senha codificada
username = 'admin'
password = 'P08S11PDC#'
ip = '192.168.140.100'
port = '554'

# Codificando a senha para URL
password_encoded = urllib.parse.quote_plus(password)

# URL RTSP corretamente formatada
RTSP_URL = f'rtsp://{username}:{password_encoded}@{ip}:{port}'

def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

@app.route('/visualizacao')
def visualizacao():
    return render_template('visualizacao.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify, render_template, Response
from camera import CameraHandler
from sensors import DataHandler

app = Flask(__name__)


@app.route('/')
def index():
    # rendering web page
    return render_template('index.html')


def gen(camera):
    while True:
        # get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(CameraHandler()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/sensor_data', methods=['GET'])
def sensor_data():
    data = DataHandler().get_data()
    _, _, fsr1, fsr2, fsr3, fsl1, fsl2, fsl3 = data.split(',')
    return jsonify(fsr1, fsr2, fsr3, fsl1, fsl2, fsl3)


if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0', port='5000', debug=True)

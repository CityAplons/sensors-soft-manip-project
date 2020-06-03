from flask import Flask, jsonify, render_template, request, Response
from camera import CameraHandler
from sensors import DataHandler

sensorsObject = DataHandler("192.168.1.11")
sensorData = "!No data"

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


@app.route('/true_value', methods=['GET'])
def true_value():
    cameraValue = CameraHandler().getValues()     # Mean HUE value (float)
    global sensorData
    if sensorData[0] != "!":
        fsr, fsl, hue = sensorData.split(',')
        if cameraValue > 0:
            return "Camera: " + str(cameraValue) + ", Sensor: " + hue
        else:
            return "Camera: no data, Sensor: " + hue
    else:
        if cameraValue > 0:
            return "Camera: " + str(cameraValue) + ", Sensor: no data"
        else:
            return "Camera: no data, Sensor: no data"


@app.route('/sensor_data', methods=['GET'])
def sensor_data():
    global sensorsObject
    global sensorData
    data = sensorsObject.get_data()
    sensorData = data
    cameraValue = CameraHandler().getValues()
    # print(data)
    if data[0] != "!":
        fsr, fsl, hue = data.split(',')
        return jsonify(fsr, fsl, hue, cameraValue)
    else:
        return "!Connection error"


@app.route('/set_new_ip', methods=['POST'])
def set_new_ip():
    global sensorsObject
    ip = request.form.get('ip')
    sensorsObject = DataHandler(ip)
    return "OK"


if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0', port='5000', debug=True)

from flask import Flask, jsonify, render_template, request, Response
from camera import CameraHandler
from sensors import DataHandler

sensorsObject = DataHandler("192.168.1.11")
sensorData = "!No data"
cameraData = 0

app = Flask(__name__)


@app.route('/')
def index():
    # rendering web page
    return render_template('index.html')


def gen(camera):
    while True:
        global cameraData
        # get camera frame
        frame = camera.get_frame()
        cameraData = camera.getValues()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(CameraHandler()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/true_value', methods=['GET'])
def true_value():
    global cameraData
    global sensorData
    if sensorData[0] != "!":
        fsr, fsl, hue = sensorData.split(',')
        if cameraData > 0:
            return "Camera: " + str(cameraData) + ", Sensor: " + hue
        else:
            return "Camera: no data, Sensor: " + hue
    else:
        if cameraData > 0:
            return "Camera: " + str(cameraData) + ", Sensor: no data"
        else:
            return "Camera: no data, Sensor: no data"


@app.route('/sensor_data', methods=['GET'])
def sensor_data():
    global sensorsObject
    global sensorData
    global cameraData
    data = sensorsObject.get_data()
    sensorData = data
    # print(data)
    if data[0] != "!":
        fsr, fsl, hue = data.split(',')
        return jsonify(fsr, fsl, hue, cameraData)
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

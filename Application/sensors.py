import websockets

class CameraHandler(object):
    def __init__(self):
        # creating websocket instance
        self.url = "ws://192.168.1.75/ws"

    def __del__(self):
        # releasing camera
        self.camera.close()

    def get_data(self):
        xml = "test"
        return xml
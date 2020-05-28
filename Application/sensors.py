from websocket import create_connection


class DataHandler(object):
    def __init__(self):
        self.url = "ws://192.168.1.76/ws"
        self.ws = create_connection(self.url)

    def __del__(self):
        self.ws.close()

    def get_data(self):
        try:
            xml = self.ws.recv()
        except:
            xml = "0,0,0,0,0,0,0,0"
        return xml


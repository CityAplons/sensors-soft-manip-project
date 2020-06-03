import websockets
import asyncio


class EchoWebsocket:
    def __init__(self, ip):
        self.url = 'ws://' + ip + '/ws'

    async def __aenter__(self):
        self._conn = websockets.connect(self.url)
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()


class DataHandler:
    data = None

    def __init__(self, ip):
        self.wws = EchoWebsocket(ip)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.get_current_data())
        self.loop.run_forever()

    def __del__(self):
        self.loop.close()

    def get_data(self):
        return self.data

    async def get_current_data(self):
        try:
            async with self.wws as echo:
                self.data = await echo.receive()
        except Exception:
            self.data = "!Connection error"

import json
import asyncio
import websockets
from abc import abstractmethod

SOCKET_PORT = 8081

class App:
    def __init__(self, event_loop):
        self._event_loop = event_loop
        self._client_socket = None

        self._funcs = {}
        self._funcs_idx = 0

        server = websockets.serve(self._socket_handler, "0.0.0.0", SOCKET_PORT)
        event_loop.run_until_complete(server)

    async def _socket_handler(self, client_socket, path):
        self._client_socket = client_socket
        async for msg in self._client_socket:
            print("[debug] %s" % msg)
            result = self._process(json.loads(msg))
            if result is not None:
                await self._client_socket.send(json.dumps(result))

    def _wrap(self, py_obj):
        if callable(py_obj):
            self._funcs_idx += 1
            self._funcs["__pyreact_pyfunc_%d" % self._funcs_idx] = py_obj
            return "__pyreact_pyfunc_%d" % self._funcs_idx

        elif isinstance(py_obj, list):
            return [self._wrap(o) for o in py_obj]

        elif isinstance(py_obj, dict):
            return {k: self._wrap(py_obj[k]) for k in py_obj.keys()}

        elif hasattr(py_obj, '__dict__'):
            res = {k: self._wrap(py_obj.__dict__[k]) for k in py_obj.__dict__.keys()}
            for m in py_obj.__class__.__dict__.keys():
                if not m.startswith("__"):
                    def make(func):
                        def call(*args, **kwargs):
                            py_obj.__class__.__dict__[func](py_obj, *args, **kwargs)
                        return call
                    res[m] = self._wrap(make(m))
            return res

        else:
            return py_obj

    def _unwrap(self, js_obj):
        if isinstance(js_obj, list):
            return [self._unwrap(o) for o in js_obj]

        elif isinstance(js_obj, dict):
            return {k: self._unwrap(js_obj[k]) for k in js_obj.keys()}

        else:
            return js_obj

    def _process(self, data):
        if data['__pyreact_kind'] == 'func_call':
            if data['__pyreact_id'] not in self._funcs:
                print("[debug] %s not in %s" % (data['__pyreact_id'], self._funcs.keys()))
            else:
                self._funcs[data['__pyreact_id']](
                    *self._unwrap(data['__pyreact_args']))

        props = self.render()
        return {
            'props': self._wrap(props),
            '__pyreact_kind': 'render'
        }

    @abstractmethod
    def render(self):
        pass


class DummyData:
    def __init__(self, counter):
        self.counter = 0

    def inc(self):
        self.counter += 1

    def dec(self):
        self.counter -= 1

class AppImpl(App):
    def __init__(self, event_loop):
        super().__init__(event_loop)
        self.dummy = DummyData(0)

    def render(self):
        return {
            'dummy': self.dummy,
        }


if __name__ == '__main__':
    try:
        server = AppImpl(asyncio.get_event_loop())
        asyncio.get_event_loop().run_forever()

    except Exception as e:
        print(e)

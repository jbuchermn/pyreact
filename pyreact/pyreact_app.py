import json
import asyncio
import websockets
from abc import abstractmethod

SOCKET_PORT = 8081

async def _run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    await proc.communicate()


class PyReactApp:
    def __init__(self, js_path=None, event_loop=asyncio.get_event_loop()):
        self._client_socket = None

        self._funcs = {}
        self._funcs_idx = 0

        server = websockets.serve(self._socket_handler, "0.0.0.0", SOCKET_PORT)
        event_loop.run_until_complete(server)

        if js_path is not None:
            event_loop.create_task(_run("cd \"%s\" && npm run start" % js_path))


    async def _socket_handler(self, client_socket, path):
        self._client_socket = client_socket
        async for msg in self._client_socket:
            print("[debug] %s" % msg)
            result = self._process(json.loads(msg))
            if result is not None:
                await self._client_socket.send(json.dumps(result))

    async def render(self):
        result = self._process({})
        if result is not None and self._client_socket is not None:
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
            res = {k: self._wrap(py_obj.__dict__[k])
                   for k in py_obj.__dict__.keys()}
            for m in py_obj.__class__.__dict__.keys():
                if not m.startswith("__"):
                    def make(func):
                        def call(*args, **kwargs):
                            py_obj.__class__.__dict__[func](
                                py_obj, *args, **kwargs)
                        return call
                    res[m] = self._wrap(make(m))
            return res

        else:
            return py_obj

    def _process(self, data):
        if '__pyreact_kind' in data and data['__pyreact_kind'] == 'func_call':
            if data['__pyreact_id'] not in self._funcs:
                print("[debug] cannot call %s, available: %s" %
                      (data['__pyreact_id'], self._funcs.keys()))
            else:
                self._funcs[data['__pyreact_id']](
                    *data['__pyreact_args'])

        self._funcs = {}
        props = self._render()
        return {
            'props': self._wrap(props),
            '__pyreact_kind': 'render'
        }

    @abstractmethod
    def _render(self):
        pass


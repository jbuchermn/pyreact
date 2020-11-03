import asyncio
from pyreact import PyReactApp

class DummyData:
    def __init__(self, counter):
        self.counter = 0

    def inc(self):
        self.counter += 1

    def dec(self):
        self.counter -= 1


class AppImpl(PyReactApp):
    def __init__(self):
        super().__init__("./example")
        self.dummy = DummyData(0)

    def _render(self):
        return {
            'dummy': self.dummy,
        }


if __name__ == '__main__':
    try:
        server = AppImpl()
        asyncio.get_event_loop().run_forever()

    except Exception as e:
        print(e)

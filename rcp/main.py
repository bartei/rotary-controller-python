from keke import ktrace
from kivy.base import EventLoop
from kivy.logger import Logger, KivyFormatter
from kivy.core.window import Window
import platform
import asyncio

log = Logger.getChild(__name__)

if "arm" in platform.machine():
    Window.show_cursor = False
else:
    Window.show_cursor = True
    Window.size = (1024, 600)

for h in log.root.handlers:
    h.formatter = KivyFormatter('%(asctime)s - %(name)s:%(lineno)s-%(funcName)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    from rcp.app import MainApp
    # Monkeypatch to add more trace events
    EventLoop.idle = ktrace()(EventLoop.idle)
    asyncio.run(MainApp().async_run())

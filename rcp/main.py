import asyncio
from keke import ktrace
from kivy.base import EventLoop
from kivy.logger import Logger
log = Logger.getChild(__name__)


if __name__ == "__main__":
    from rcp.app import MainApp
    # Monkeypatch to add more trace events
    EventLoop.idle = ktrace()(EventLoop.idle)
    try:
        asyncio.run(MainApp().async_run())
    except KeyboardInterrupt:
        log.info("Exiting Application")

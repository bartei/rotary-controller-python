from keke import ktrace
from kivy.base import EventLoop
from kivy.logger import Logger, KivyFormatter
from kivy.core.window import Window
import platform
import asyncio
import sentry_sdk

sentry_sdk.init(
    dsn="https://8fd20c0607e9c930a16d51a4b1eacc94@o4509625403506688.ingest.us.sentry.io/4509625405014016",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

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

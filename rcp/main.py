from keke import ktrace
from kivy.base import EventLoop
from kivy.logger import Logger, KivyFormatter

log = Logger.getChild(__name__)

Window.show_cursor = False
for h in log.root.handlers:
    h.formatter = KivyFormatter('%(asctime)s - %(name)s:%(lineno)s-%(funcName)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    from rcp.app import MainApp
    # Monkeypatch to add more trace events
    EventLoop.idle = ktrace()(EventLoop.idle)
    MainApp().run()

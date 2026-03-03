from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

ITEMS_PER_PAGE = 12  # 4 cols x 3 rows


class InputsSetupScreen(Screen):

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self._page = 0
        super().__init__(**kv)
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        container = self.ids.inputs_container
        container.clear_widgets()

        items = list(enumerate(self.app.scales))
        total_pages = max(1, (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        self._page = min(self._page, total_pages - 1)

        start = self._page * ITEMS_PER_PAGE
        page_items = items[start:start + ITEMS_PER_PAGE]

        for i, scale in page_items:
            btn = Button(text=f"Input {i}", font_size=22)
            btn.bind(on_release=lambda _, idx=i: self._goto_input(idx))
            container.add_widget(btn)

        self._update_footer(total_pages)

    def _update_footer(self, total_pages):
        footer = self.ids.page_footer
        footer.clear_widgets()
        if total_pages <= 1:
            footer.height = 0
            return
        footer.height = 60
        prev_btn = Button(text="Previous", font_size=22, disabled=self._page == 0)
        prev_btn.bind(on_release=lambda _: self._change_page(-1))
        page_label = Label(text=f"Page {self._page + 1} / {total_pages}", font_size=22)
        next_btn = Button(text="Next", font_size=22, disabled=self._page >= total_pages - 1)
        next_btn.bind(on_release=lambda _: self._change_page(1))
        footer.add_widget(prev_btn)
        footer.add_widget(page_label)
        footer.add_widget(next_btn)

    def _change_page(self, delta):
        self._page += delta
        self._rebuild_buttons()

    def _goto_input(self, index):
        screen_name = f"scale_{index}"
        if self.app.manager.has_screen(screen_name):
            self.app.manager.goto(screen_name)
        else:
            log.warning(f"Screen {screen_name} not found")

    def on_pre_enter(self, *args):
        self._rebuild_buttons()
